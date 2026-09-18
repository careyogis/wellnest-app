import frappe
from frappe.utils import formatdate, format_time, getdate, get_time

no_cache = 1

def get_context(context):
    service_id = frappe.form_dict.get("service_id")
    if not service_id:
        # improperly called, so return
        return

    frappe.flags.ignore_permissions = True
    appointment = frappe.get_value("Patient Appointment", service_id, ["name", "practitioner", "patient", "scheduled_time", "consultation_type", "consultation_fee"], as_dict=True)
    practitioner = frappe.get_value("Practitioner", appointment.practitioner, ["full_name"], as_dict=True) if appointment.practitioner else None
    patient = frappe.get_value("Patient", appointment.patient, ["full_name", "mobile", "customer"], as_dict=True) if appointment.patient else None
    frappe.flags.ignore_permissions = False

    # Determine amount
    amount = float(appointment.consultation_fee or 0)
    
    patient_email = ""
    patient_mobile = ""
    if patient:
        patient_mobile = patient.get("mobile") or ""
        if patient_mobile and (not patient_mobile.startswith("+91")):
            patient_mobile = "+91" + patient_mobile

        customer = patient.get("customer")
        if customer:
            # Get the email from Contact where the customer is linked, as the email is not directly on the Customer doctype
            contact_name = frappe.db.get_value(
                "Dynamic Link",
                {"link_doctype": "Customer", "parenttype": "Contact", "link_name": customer},
                "parent"
            )
            patient_email = frappe.db.get_value("Contact", contact_name, "email_ids.email_id") or ""
        
        if not patient_email and frappe.session.user != "Guest":
            patient_email = frappe.session.user

    if not patient_email :
        patient_email = 'unknown'

    # Passing dynamic values to context
    context.appointment = appointment
    context.practitioner = practitioner
    context.patient = patient
    context.patient_email = patient_email
    context.patient_mobile = patient_mobile
    context.amount = amount
    context.amount_paise = int(amount * 100)
    
    context.formatted_date = ""
    if appointment.scheduled_time:
        context.formatted_date = frappe.utils.format_datetime(appointment.scheduled_time, "dd MMM yyyy, hh:mm a")

    context.issue_date = frappe.utils.formatdate(frappe.utils.today(), "dd MMM yyyy")
    context.csrf_token = frappe.sessions.get_csrf_token()
