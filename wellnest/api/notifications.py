import frappe
import requests
from frappe.utils import now_datetime
from frappe.utils import get_site_name

@frappe.whitelist(allow_guest=False)
def get_app_notifications(patient_id):
	now = now_datetime()
	
	# Fetch Global
	global_notifs = frappe.get_all(
		"App Notification",
		filters={
			"target_audience": "Global Broadcast",
			"scheduled_time": ["<=", now],
			"push_sent": 0
		},
		fields=["name", "title", "body", "action_type", "action_url", "creation"],
		order_by="creation desc",
		limit=20
	)

	# Fetch Specific
	specific_notifs = frappe.get_all(
		"App Notification",
		filters={
			"target_audience": "Specific Patient",
			"patient": patient_id,
			"scheduled_time": ["<=", now],
			"push_sent": 0
		},
		fields=["name", "title", "body", "action_type", "action_url", "creation"],
		order_by="creation desc",
		limit=20
	)

	all_notifs = global_notifs + specific_notifs
	# Sort by creation descending
	all_notifs.sort(key=lambda x: x["creation"], reverse=True)
	
	return all_notifs[:30]

@frappe.whitelist()
def notify_doctor_of_new_booking(patient_appointmentId, practitioner_name, practitioner_mobile, scheduled_datetime, consultation_type, patient_name, patient_dob, reason):
	# from frappe.utils import now_datetime
	# from datetime import timedelta
	try:
		_logInfo(f"Sending WhatsApp alert to the doctor: {practitioner_name} for the appointment: {patient_appointmentId}")

		if not practitioner_mobile:
			frappe.log_error(f"Doctor: {practitioner_name} does not have a mobile number. Cannot send WhatsApp alert.", "Doctor WhatsApp Alert Error")
			return

		age = now_datetime().year - patient_dob.year if patient_dob else "N/A"

		if not practitioner_mobile.startswith("+91"):
			practitioner_mobile = "+91" + practitioner_mobile

		_send_booking_whatsapp_message(practitioner_name, practitioner_mobile, patient_appointmentId, scheduled_datetime, consultation_type, patient_name, age, reason)
	except Exception as exp:
		frappe.log_error(frappe.get_traceback(), "WhatsApp Alert Error")
		_logInfo(f"Check the error: {str(exp)}")


	_logInfo(f"Finished sending WhatsApp alerts")

def notify_doctor_of_prescription_review(patient_appointment):
    try:
        if not patient_appointment:
            _logInfo(
                "Prescription WhatsApp notification skipped: "
                "no patient appointment."
            )
            return

        appointment = frappe.get_doc(
            "Patient Appointment",
            patient_appointment,
        )

        if not appointment.practitioner:
            frappe.log_error(
                f"Patient Appointment {patient_appointment} "
                f"does not have a practitioner.",
                "Prescription WhatsApp Notification Error",
            )
            return

        if not appointment.patient:
            frappe.log_error(
                f"Patient Appointment {patient_appointment} "
                f"does not have a patient.",
                "Prescription WhatsApp Notification Error",
            )
            return

        doctor = frappe.get_doc(
            "Practitioner",
            appointment.practitioner,
        )

        patient = frappe.get_doc(
            "Patient",
            appointment.patient,
        )

        doctor_phone = doctor.mobile

        if not doctor_phone:
            frappe.log_error(
                f"Doctor {doctor.name} does not have a mobile number. "
                f"Cannot send prescription review WhatsApp alert.",
                "Prescription WhatsApp Notification Error",
            )
            return

        if not doctor_phone.startswith("+91"):
            doctor_phone = "+91" + doctor_phone

        doctor_name = doctor.full_name or doctor.name
        patient_name = patient.full_name or patient.name

        _logInfo(
            f"Sending prescription review WhatsApp alert to "
            f"{doctor_name} ({doctor_phone}) for appointment "
            f"{patient_appointment}"
        )

        return _send_prescription_review_whatsapp_message(
            doctor_phone,
            doctor_name,
            patient_name,
            patient_appointment,
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Prescription WhatsApp Notification Error",
        )

        _logInfo(
            f"Failed to send prescription review WhatsApp alert "
            f"for appointment {patient_appointment}"
        )

def notify_doctor_of_prescription_sla_reminder(patient_appointment):
    try:
        appointment = frappe.get_doc(
            "Patient Appointment",
            patient_appointment,
        )

        if not appointment.practitioner or not appointment.patient:
            return

        doctor = frappe.get_doc(
            "Practitioner",
            appointment.practitioner,
        )

        patient = frappe.get_doc(
            "Patient",
            appointment.patient,
        )

        doctor_phone = doctor.mobile

        if not doctor_phone:
            frappe.log_error(
                f"Doctor {doctor.name} does not have a mobile number.",
                "Prescription SLA WhatsApp Notification Error",
            )
            return

        if not doctor_phone.startswith("+91"):
            doctor_phone = "+91" + doctor_phone

        doctor_name = doctor.full_name or doctor.name
        patient_name = patient.full_name or patient.name

        _send_prescription_sla_whatsapp_message(
            doctor_phone,
            doctor_name,
            patient_name,
            patient_appointment,
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Prescription SLA WhatsApp Notification Error",
        )


def _send_prescription_sla_whatsapp_message(
    doctor_phone,
    doctor_name,
    patient_name,
    patient_appointment,
):
    import requests

    access_token = frappe.conf.get("ACCESS_TOKEN")
    phone_number_id = frappe.conf.get("PHONE_NUMBER_ID")
    version = frappe.conf.get("VERSION")
    site_url = frappe.utils.get_url()

    url = (
        f"https://graph.facebook.com/"
        f"{version}/{phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    deep_link = (
        f"{site_url}/doctor-app/consultations/"
        f"{patient_appointment}"
    )

    payload = {
        "messaging_product": "whatsapp",
        "to": doctor_phone,
        "type": "template",
        "template": {
            "name": "doctor_pending_prescription_reminder",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": doctor_name,
                        },
                        {
                            "type": "text",
                            "text": patient_name,
                        },
                        {
                            "type": "text",
                            "text": deep_link,
                        },
                    ],
                }
            ],
        },
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
    )

    _logInfo(
        f"Prescription SLA WhatsApp response for "
        f"{patient_appointment}: "
        f"HTTP {response.status_code} - {response.text}"
    )

    if not response.ok:
        frappe.log_error(
            (
                f"HTTP Status: {response.status_code}\n"
                f"Response: {response.text}\n"
                f"Appointment: {patient_appointment}"
            ),
            "Prescription SLA WhatsApp API Error",
        )

    return response.json()


def send_prescription_sla_reminders():
    from datetime import timedelta

    now = now_datetime()
    sla_deadline = now - timedelta(hours=5)

    try:
        appointments = frappe.get_all(
            "Patient Appointment",
            filters=[
                ["status", "=", "Completed"],
                ["consultation_ended_at", "is", "set"],
                ["consultation_ended_at", ">", sla_deadline],
            ],
            fields=[
                "name",
                "practitioner",
                "patient",
                "consultation_ended_at",
                "prescription_sla_last_reminder_at",
            ],
            ignore_permissions=True,
        )

        for appointment in appointments:
            if appointment.prescription_sla_last_reminder_at:
                hours_since_last_reminder = (
                    now - appointment.prescription_sla_last_reminder_at
                ).total_seconds() / 3600

                if hours_since_last_reminder < 1:
                    continue

            prescription_name = frappe.db.get_value(
                "Smart Prescription",
                {
                    "patient_appointment": appointment.name,
                },
                "name",
            )

            if not prescription_name:
                should_remind = True
            else:
                workflow_state = frappe.db.get_value(
                    "Smart Prescription",
                    prescription_name,
                    "workflow_state",
                )

                should_remind = workflow_state != "Complete"

            if not should_remind:
                continue

            notify_doctor_of_prescription_sla_reminder(
                appointment.name
            )

            frappe.db.set_value(
                "Patient Appointment",
                appointment.name,
                "prescription_sla_last_reminder_at",
                now,
            )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Prescription SLA Reminder Error",
        )


def _send_prescription_review_whatsapp_message(
    doctor_phone,
    doctor_name,
    patient_name,
    patient_appointment,
):
    import requests

    _logInfo(
        f"Sending prescription WhatsApp message to "
        f"{doctor_name} ({doctor_phone}) for appointment "
        f"{patient_appointment}"
    )

    access_token = frappe.conf.get("ACCESS_TOKEN")
    phone_number_id = frappe.conf.get("PHONE_NUMBER_ID")
    version = frappe.conf.get("VERSION")
    site_url = frappe.utils.get_url()

    url = (
        f"https://graph.facebook.com/"
        f"{version}/{phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    deep_link = (
        f"{site_url}/doctor-app/consultations/"
        f"{patient_appointment}"
    )

    payload = {
        "messaging_product": "whatsapp",
        "to": doctor_phone,
        "type": "template",
        "template": {
            "name": "doctor_prescription_ready_for_review",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": doctor_name,
                        },
                        {
                            "type": "text",
                            "text": patient_name,
                        },
                        {
                            "type": "text",
                            "text": patient_appointment,
                        },
                        {
                            "type": "text",
                            "text": deep_link,
                        },
                    ],
                },
            ],
        },
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
    )

    _logInfo(
        f"Prescription WhatsApp response "
        f"for {patient_appointment}: "
        f"HTTP {response.status_code} - {response.text}"
    )

    if not response.ok:
        frappe.log_error(
            (
                f"HTTP Status: {response.status_code}\n"
                f"Response: {response.text}\n"
                f"Appointment: {patient_appointment}"
            ),
            "Prescription WhatsApp API Error",
        )

    return response.json()


def send_doctor_whatsapp_alert():
	from frappe.utils import now_datetime
	from datetime import timedelta

	minutes_before = frappe.conf.get('DOCTOR_REMINDER_MINUTES_BEFORE') or 10  # Set the time before the appointment to send the alert

	_logInfo(f"Initiating WhatsApp alerts to the doctors")

	try:
		all_upcoming_appointments = frappe.get_all(
			"Patient Appointment",
			filters=[
				["status", "=", "Scheduled"],
				["scheduled_time", ">=", now_datetime()],
				["scheduled_time", "<=", now_datetime() + timedelta(minutes=minutes_before)],
			],
			fields=["name", "practitioner", "patient", "scheduled_time", "consultation_type", "main_complaints"],
			ignore_permissions=True,
		)

		for appointment in all_upcoming_appointments:
			doctor = frappe.get_doc("Practitioner", appointment.practitioner)
			patient = frappe.get_doc("Patient", appointment.patient)
			doctor_phone = doctor.mobile
			if not doctor_phone:
				frappe.log_error(f"Doctor {doctor.name} does not have a mobile number. Cannot send WhatsApp alert.", "Doctor WhatsApp Alert Error")
				continue

			if not doctor_phone.startswith("+91"):
				doctor_phone = "+91" + doctor_phone
							
			doctor_name = doctor.full_name
			patient_name = patient.full_name
			age = now_datetime().year - patient.date_of_birth.year if patient.date_of_birth else "N/A"
			reason = appointment.main_complaints or "N/A"
			time = appointment.scheduled_time.strftime("%I:%M %p")
			mode = appointment.consultation_type
			appointment_id = appointment.name
			_send_whatsapp_message(doctor_phone, doctor_name, patient_name, age, reason, time, mode, appointment_id)
	except Exception as exp:
		frappe.log_error(frappe.get_traceback(), "WhatsApp Alert Error")
		_logInfo(f"Check the error: {str(exp)}")


	_logInfo(f"Finished sending WhatsApp alerts")


def _send_whatsapp_message(doctor_phone, doctor_name, patient_name, age, reason, time, mode, appointment_id):	
	import requests

	_logInfo(f"Sending WhatsApp message to {doctor_name} ({doctor_phone}) for appointment {appointment_id} with patient {patient_name}, Aged {age}, Reason: {reason}, Time: {time}, Mode: {mode}")

	access_token = frappe.conf.get('ACCESS_TOKEN')
	phone_number_id = frappe.conf.get('PHONE_NUMBER_ID')
	version = frappe.conf.get('VERSION')
	site_url = frappe.utils.get_url()


	url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"

	headers = {
		"Authorization": f"Bearer {access_token}",
		"Content-Type": "application/json"
	}

	payload = {
        "messaging_product": "whatsapp",
        "to": doctor_phone,
        "type": "template",
        "template": {
            "name": "doctor_video_consultation_reminder_today",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": doctor_name},
                        {"type": "text", "text": patient_name},
                        {"type": "text", "text": age},
                        {"type": "text", "text": reason},
                        {"type": "text", "text": time},
                        {"type": "text", "text": mode},
                        {"type": "text", "text": f"{site_url}/doctor-app/consultations/{appointment_id}"}
                    ]
                }
            ]
        }
	}

	response = requests.post(url, json=payload, headers=headers)
	return response.json()

def _send_booking_whatsapp_message(practitioner_name, practitioner_mobile, patient_appointmentId, scheduled_datetime, consultation_type, patient_name, age, reason):	
	import requests

	_logInfo(f"Sending WhatsApp message to {practitioner_name} ({practitioner_mobile}) for appointment {patient_appointmentId}, Time: {scheduled_datetime}, Mode: {consultation_type}")

	access_token = frappe.conf.get('ACCESS_TOKEN')
	phone_number_id = frappe.conf.get('PHONE_NUMBER_ID')
	version = frappe.conf.get('VERSION')
	site_url = frappe.utils.get_url()


	url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"

	headers = {
		"Authorization": f"Bearer {access_token}",
		"Content-Type": "application/json"
	}

	payload = {
        "messaging_product": "whatsapp",
        "to": practitioner_mobile,
        "type": "template",
        "template": {
            "name": "doctor_new_consultation_booking",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": practitioner_name},
                        {"type": "text", "text": patient_name},
                        {"type": "text", "text": age},
                        {"type": "text", "text": reason or "Not Provided"},
                        {"type": "text", "text": scheduled_datetime},
                        {"type": "text", "text": consultation_type},
                        {"type": "text", "text": f"{site_url}/doctor-app/consultations/{patient_appointmentId}"}

                    ]
                }
            ]
        }
	}

	response = requests.post(url, json=payload, headers=headers)
	return response.json()

def _logInfo(message):
	import logging

	# Initialize a custom logger for your app or module
	logger = frappe.logger("Health", allow_site=True, file_count=5, max_size=250000)

	# Explicitly set the logging level to INFO
	logger.setLevel(logging.INFO)

	# Log your info message
	logger.info(message)