import frappe
from frappe.utils import formatdate, format_time, getdate, get_time

def get_context(context):
    service_id = frappe.form_dict.get("service_id")
    if not service_id:
        frappe.throw("Invalid Appointment ID")

    frappe.flags.ignore_permissions = True
    appointment = frappe.get_doc("Patient Appointment", service_id)
    practitioner = frappe.get_doc("Practitioner", appointment.practitioner) if appointment.practitioner else None
    patient = frappe.get_doc("Patient", appointment.patient) if appointment.patient else None
    frappe.flags.ignore_permissions = False

    # Determine amount
    amount = float(appointment.consultation_fee or 0)
    
    patient_email = ""
    patient_mobile = ""
    if patient:
        patient_mobile = patient.get("mobile") or ""
        customer = patient.get("customer")
        if customer:
            patient_email = frappe.db.get_value("Customer", customer, "email_id") or ""
        
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
