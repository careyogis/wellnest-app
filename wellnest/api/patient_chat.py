import frappe
from frappe.utils import now_datetime


def _get_current_practitioner():
    """Return the Practitioner linked to the logged-in doctor."""

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw(
            "Practitioner not found.",
            frappe.PermissionError,
        )

    return practitioner


def _get_authorized_appointment(appointment_name):
    """Return the appointment after verifying the logged-in doctor owns it."""

    if not appointment_name:
        frappe.throw("Patient appointment is required.")

    appointment = frappe.get_doc(
        "Patient Appointment",
        appointment_name,
    )

    practitioner = _get_current_practitioner()

    if appointment.practitioner != practitioner:
        frappe.throw(
            "You are not authorized to access this patient's chat.",
            frappe.PermissionError,
        )

    if not appointment.patient:
        frappe.throw("Patient not found for this appointment.")

    return appointment, practitioner


def _get_current_customer():
    """Return the Customer linked to the logged-in patient user."""

    user = frappe.session.user

    if not user or user == "Guest":
        frappe.throw(
            "You must be logged in as a patient.",
            frappe.PermissionError,
        )

    contact_name = frappe.db.get_value(
        "Contact Email",
        {"email_id": user},
        "parent",
    )

    if not contact_name:
        frappe.throw(
            "Customer contact not found.",
            frappe.PermissionError,
        )

    customer_name = frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": "Customer",
            "parenttype": "Contact",
            "parent": contact_name,
        },
        "link_name",
    )

    if not customer_name:
        frappe.throw(
            "Customer not found for the logged-in user.",
            frappe.PermissionError,
        )

    return customer_name


def _get_current_patient():
    """Return the Patient linked to the logged-in customer's account."""

    customer = _get_current_customer()

    patient = frappe.db.get_value(
        "Patient",
        {"customer": customer},
        "name",
    )

    if not patient:
        frappe.throw(
            "Patient not found for the logged-in user.",
            frappe.PermissionError,
        )

    return patient


def _get_authorized_patient_appointment(appointment_name):
    """
    Return the appointment only if it belongs to the logged-in patient.
    """

    if not appointment_name:
        frappe.throw("Patient appointment is required.")

    appointment = frappe.get_doc(
        "Patient Appointment",
        appointment_name,
    )

    patient = _get_current_patient()

    if appointment.patient != patient:
        frappe.throw(
            "You are not authorized to access this appointment.",
            frappe.PermissionError,
        )

    return appointment, patient


@frappe.whitelist()
def get_patient_chat(patient_appointment):
    """Return all chat messages for the current doctor appointment."""

    appointment, practitioner = _get_authorized_appointment(
        patient_appointment
    )

    messages = frappe.get_all(
        "Patient Chat Message",
        filters={
            "patient_appointment": appointment.name,
        },
        fields=[
            "name",
            "patient_appointment",
            "patient",
            "practitioner",
            "sender_type",
            "sender",
            "message",
            "attachment",
            "sent_at",
            "read_by_doctor",
            "read_by_patient",
        ],
        order_by="sent_at asc, creation asc",
    )

    return {
        "patient": appointment.patient,
        "practitioner": practitioner,
        "messages": messages,
    }


@frappe.whitelist()
def send_patient_chat_message(
    patient_appointment,
    message=None,
    attachment=None,
):
    """Send a message from the currently logged-in doctor."""

    appointment, practitioner = _get_authorized_appointment(
        patient_appointment
    )

    message = (message or "").strip()
    attachment = attachment or None

    if not message and not attachment:
        frappe.throw(
            "Message or attachment is required."
        )

    doc = frappe.get_doc(
        {
            "doctype": "Patient Chat Message",
            "patient_appointment": appointment.name,
            "patient": appointment.patient,
            "practitioner": practitioner,
            "sender_type": "Doctor",
            "sender": frappe.session.user,
            "message": message,
            "attachment": attachment,
            "sent_at": now_datetime(),
            "read_by_doctor": 1,
            "read_by_patient": 0,
        }
    )

    doc.insert(
        ignore_permissions=True
    )

    return {
        "name": doc.name,
        "patient_appointment": doc.patient_appointment,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
        "sender_type": doc.sender_type,
        "sender": doc.sender,
        "message": doc.message,
        "attachment": doc.attachment,
        "sent_at": doc.sent_at,
        "read_by_doctor": doc.read_by_doctor,
        "read_by_patient": doc.read_by_patient,
    }


@frappe.whitelist()
def mark_patient_chat_read(patient_appointment):
    """Mark all patient messages as read by the doctor."""

    appointment, _ = _get_authorized_appointment(
        patient_appointment
    )

    frappe.db.set_value(
        "Patient Chat Message",
        {
            "patient_appointment": appointment.name,
            "sender_type": "Patient",
            "read_by_doctor": 0,
        },
        "read_by_doctor",
        1,
        update_modified=False,
    )

    frappe.db.commit()

    return {
        "success": True,
    }


@frappe.whitelist()
def get_patient_appointments():
    """Return appointments belonging to the logged-in patient."""

    patient = _get_current_patient()

    appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "patient": patient,
        },
        fields=[
            "name",
            "patient",
            "practitioner",
            "scheduled_time",
            "status",
            "consultation_type",
            "main_complaints",
        ],
        order_by="scheduled_time desc",
    )

    return {
        "patient": patient,
        "appointments": appointments,
    }


@frappe.whitelist()
def get_patient_chat_for_current_user(patient_appointment):
    """
    Return chat messages after verifying that the appointment
    belongs to the logged-in patient.
    """

    appointment, patient = _get_authorized_patient_appointment(
        patient_appointment
    )

    messages = frappe.get_all(
        "Patient Chat Message",
        filters={
            "patient_appointment": appointment.name,
        },
        fields=[
            "name",
            "patient_appointment",
            "patient",
            "practitioner",
            "sender_type",
            "sender",
            "message",
            "attachment",
            "sent_at",
            "read_by_doctor",
            "read_by_patient",
        ],
        order_by="sent_at asc, creation asc",
    )

    return {
        "patient": patient,
        "appointment": appointment.name,
        "messages": messages,
    }


@frappe.whitelist()
def send_patient_chat_message_from_patient(
    patient_appointment,
    message=None,
    attachment=None,
):
    """Send a chat message from the logged-in patient."""

    appointment, patient = _get_authorized_patient_appointment(
        patient_appointment
    )

    message = (message or "").strip()
    attachment = attachment or None

    if not message and not attachment:
        frappe.throw(
            "Message or attachment is required."
        )

    doc = frappe.get_doc(
        {
            "doctype": "Patient Chat Message",
            "patient_appointment": appointment.name,
            "patient": patient,
            "practitioner": appointment.practitioner,
            "sender_type": "Patient",
            "sender": frappe.session.user,
            "message": message,
            "attachment": attachment,
            "sent_at": now_datetime(),
            "read_by_doctor": 0,
            "read_by_patient": 1,
        }
    )

    doc.insert(
        ignore_permissions=True
    )

    return {
        "name": doc.name,
        "patient_appointment": doc.patient_appointment,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
        "sender_type": doc.sender_type,
        "sender": doc.sender,
        "message": doc.message,
        "attachment": doc.attachment,
        "sent_at": doc.sent_at,
        "read_by_doctor": doc.read_by_doctor,
        "read_by_patient": doc.read_by_patient,
    }


@frappe.whitelist()
def mark_patient_chat_read_by_patient(patient_appointment):
    """Mark all doctor messages as read by the logged-in patient."""

    appointment, patient = _get_authorized_patient_appointment(
        patient_appointment
    )

    frappe.db.set_value(
        "Patient Chat Message",
        {
            "patient_appointment": appointment.name,
            "patient": patient,
            "sender_type": "Doctor",
            "read_by_patient": 0,
        },
        "read_by_patient",
        1,
        update_modified=False,
    )

    frappe.db.commit()

    return {
        "success": True,
    }