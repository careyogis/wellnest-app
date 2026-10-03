import time                                                                                                                                  
import frappe
import frappe.utils
from agora_token_builder import RtcTokenBuilder
from wellnest.api.logger import log_call_event
from frappe import _
from frappe.utils import now_datetime

@frappe.whitelist()
def get_agora_token(channel_name, uid=1001, role="publisher"):
	# Store certificate in site_config.json                                                                                              
	app_id = frappe.conf.get("agora_app_id")
	app_cert = frappe.conf.get("agora_app_certificate")

	if not app_cert:
		# If testing mode (certificate disabled in Agora Console)                                                                                    
		return {"rtcToken": "", "appId": app_id}

	# 15 mins expiry
	privilege_expired_ts = int(time.time()) + 1800
	role_type = 1 if role == "publisher" else 2
																																						
	token = RtcTokenBuilder.buildTokenWithUid(
		app_id, app_cert, channel_name, int(uid), role_type, privilege_expired_ts
	)
	return {"rtcToken": token, "appId": app_id}


@frappe.whitelist()                     
def book_appointment(practitioner, patient, scheduled_time, consultation_type, consultation_fee, main_complaints="Not provided"):
	"""
	Creates a Patient Appointment in Unverified status.
	"""
	# 1. Create Patient Appointment                                                                                                                   
	appointment = frappe.get_doc({
		"doctype": "Patient Appointment",
		"practitioner": practitioner,
		"patient": patient,
		"scheduled_time": scheduled_time,                                                                                                        
		"appointment_type": consultation_type,
		"consultation_fee": consultation_fee,
		"main_complaints": main_complaints,
		"status": "Unverified"
	})
	appointment.insert(ignore_permissions=True)

	doctor_full_name = frappe.get_value("Practitioner", practitioner, "full_name")
	scheduled_time_obj = frappe.utils.get_datetime(scheduled_time)

	# 2. Schedule an App Notification
	app_notification = frappe.get_doc({                                                                                                         
		"doctype": "App Notification",
		"title": "Upcoming doctor appointment",
		"body": f"You have an upcoming appointment with {doctor_full_name} at {scheduled_time_obj.strftime('%d-%m-%Y %I:%M %p')}.",
		"target_audience": "Specific Patient",
		"patient": patient,
		"scheduled_time": (frappe.utils.add_to_date(scheduled_time, minutes=-15)),
	})
	app_notification.insert(ignore_permissions=True)
	frappe.db.commit()

	# 3. Return the appointment name
	return {
		"name": appointment.name
	}

@frappe.whitelist()
def report_doctor_noshow(appointment_id):
	"""
	Updates the status of a Patient Appointment to 'No Show' and creates a support ticket for investigating.
	"""
	appointment = frappe.get_doc("Patient Appointment", appointment_id)

	if appointment.status != "Scheduled":
		frappe.log_error(f"Customer reported 'No Show' for the appointmentId: {appointment_id}, but the status was {appointment.status}")
		return {"message": f"Appointment in {appointment.status} state cannot be marked as 'No Show'."}

	# Do not mark No Show till at least 15 mins passed the scheduled_time
	if frappe.utils.now_datetime() < frappe.utils.add_to_date(appointment.scheduled_time, minutes=15):
		frappe.log_error(f"Customer reported 'No Show' for the appointmentId: {appointment_id}, but inside 15 mins post the secheduled time of: {appointment.scheduled_time}")
		return {"message": f"Cannot mark appointment as 'No Show' until it is at least 15 minutes past the scheduled time of:{appointment.scheduled_time}"}

	appointment.status = "No Show"
	appointment.save(ignore_permissions=True)
																																		
	# Create an Issue for the support team to investigate
	issue = frappe.get_doc({
		"doctype": "Issue",
		"subject": f"Customer reported 'No Show' for appointment {appointment_id}",
		"description": f"The customer reported that the doctor: {appointment.practitioner} did not show up for the appointment with ID {appointment_id}. Please investigate.",
		"issue_type": "Service",
	})
	issue.insert(ignore_permissions=True)
	log_call_event("patient_reported_noshow", appointment_id)
	return {"message": "Appointment marked as 'No Show' and the support team have been notified."}


@frappe.whitelist()
def cancel_appointment(appointment_id: str, cancel_reason: str, patient: str = None) -> dict:
    """Cancel a Patient Appointment on behalf of the logged-in user.

    Args:
        appointment_id: The name (PK) of the Patient Appointment document.
        cancel_reason:  One of the valid cancellation reasons.

    Returns:
        {"success": True, "appointment": appointment_id}
    """
    VALID_CANCEL_REASONS = [
		"Emergency",
		"Health Issues",
		"Personal Commitment",
		"Technical Issues",
		"Choose not to say",
		"Others",
	]

    if cancel_reason not in VALID_CANCEL_REASONS:
        frappe.throw(
            _("Invalid cancel reason. Must be one of: {0}").format(
                ", ".join(VALID_CANCEL_REASONS)
            ),
            frappe.ValidationError,
        )

    doc = frappe.get_doc("Patient Appointment", appointment_id)

    # Security: the caller must own the appointment (be the linked patient's user).
    if not patient:
        patient = frappe.get_value("Patient", doc.patient, "customer")
        
    if patient and patient != frappe.session.user and not frappe.has_permission(
        "Patient Appointment", "write", doc
    ):
        frappe.throw(_("You are not authorised to cancel this appointment."), frappe.PermissionError)

    if doc.status == "Cancelled":
        frappe.throw(_("This appointment is already cancelled."), frappe.ValidationError)

    doc.status = "Cancelled"
    doc.cancel_reason = cancel_reason
    doc.cancelled_by = frappe.session.user
    doc.cancelled_at = now_datetime()
    doc.save(ignore_permissions=True)

    return {"success": True, "appointment": appointment_id}

@frappe.whitelist()
def reschedule_appointment(
    old_appointment_id: str,
    practitioner: str,
    patient: str,
    scheduled_time: str,
    consultation_type: str,
    consultation_fee: float = 0,
    main_complaints: str = "",
) -> dict:
    """Reschedule a Patient Appointment by cancelling the old one and
    creating a new one at the requested time.

    Args:
        old_appointment_id: The appointment to cancel.
        practitioner:       Practitioner docname for the new appointment.
        patient:            Patient docname.
        scheduled_time:     New datetime string ("YYYY-MM-DD HH:MM:SS").
        consultation_type:  e.g. "Online".
        consultation_fee:   Fee for the new appointment.
        main_complaints:    Optional patient complaint text.

    Returns:
        {"success": True, "new_appointment": <new_appointment_name>}
    """
    # Cancel the old appointment with a neutral reason.
    cancel_appointment(
        appointment_id=old_appointment_id,
        cancel_reason="Personal Commitment",
    )

    # Create the new appointment by reusing the existing book_appointment logic.
    result = book_appointment(
        practitioner=practitioner,
        patient=patient,
        scheduled_time=scheduled_time,
        consultation_type=consultation_type,
        consultation_fee=consultation_fee,
        main_complaints=main_complaints if main_complaints else None,
	)

    new_name = result.get("name") if isinstance(result, dict) else str(result)

    return {"success": True, "new_appointment": new_name}
