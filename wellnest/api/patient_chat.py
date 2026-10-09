import frappe
from frappe.utils import now_datetime


# Public APIs

@frappe.whitelist()
def get_patient_chat(patient_appointment):
    """Return all chat messages for the current doctor appointment."""

    appointment, practitioner = _get_authorized_appointment(patient_appointment)

    return {
        "patient": appointment.patient,
        "practitioner": practitioner,
        "messages": _serialize_messages(appointment.patient_chat_messages),
    }


@frappe.whitelist()
def send_patient_chat_message(
    patient_appointment,
    message=None,
    attachment=None,
):
    """Send a message from the currently logged-in doctor."""

    appointment, practitioner = _get_authorized_appointment(patient_appointment)

    message = (message or "").strip()
    attachment = attachment or None

    if not message and not attachment:
        frappe.throw("Message or attachment is required.")

    row = appointment.append(
        "patient_chat_messages",
        {
            "sender_type": "Doctor",
            "sender": frappe.session.user,
            "message": message,
            "attachment": attachment,
            "sent_at": now_datetime(),
            "read_by_doctor": 1,
            "read_by_patient": 0,
        },
    )

    appointment.save(ignore_permissions=True)

    return _serialize_message(row)


@frappe.whitelist()
def mark_patient_chat_read(patient_appointment):
    """Mark all patient messages as read by the doctor."""

    appointment, _ = _get_authorized_appointment(patient_appointment)

    changed = False

    for row in appointment.patient_chat_messages:
        if row.sender_type == "Patient" and not row.read_by_doctor:
            row.read_by_doctor = 1
            changed = True

    if changed:
        appointment.save(ignore_permissions=True)

    return {
        "success": True,
    }


@frappe.whitelist()
def get_patient_appointments():
    """Return appointments belonging to the logged-in patient."""

    patient = _get_current_patient()

    appointments = frappe.get_all(
        "Patient Appointment",
        filters={"patient": patient},
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

    return {
        "patient": patient,
        "appointment": appointment.name,
        "messages": _serialize_messages(appointment.patient_chat_messages),
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
        frappe.throw("Message or attachment is required.")

    row = appointment.append(
        "patient_chat_messages",
        {
            "sender_type": "Patient",
            "sender": frappe.session.user,
            "message": message,
            "attachment": attachment,
            "sent_at": now_datetime(),
            "read_by_doctor": 0,
            "read_by_patient": 1,
        },
    )

    appointment.save(ignore_permissions=True)

    return _serialize_message(row)


@frappe.whitelist()
def mark_patient_chat_read_by_patient(patient_appointment):
    """Mark all doctor messages as read by the logged-in patient."""

    appointment, _ = _get_authorized_patient_appointment(
        patient_appointment
    )

    changed = False

    for row in appointment.patient_chat_messages:
        if row.sender_type == "Doctor" and not row.read_by_patient:
            row.read_by_patient = 1
            changed = True

    if changed:
        appointment.save(ignore_permissions=True)

    return {
        "success": True,
    }


# Private helpers

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

    return appointment, practitioner


def _get_current_customer():
    """Return the Customer linked to the logged-in patient user."""

    user = frappe.session.user

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
    """Return the appointment only if it belongs to the logged-in patient."""

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


def _serialize_message(row):
    """Return a consistent API representation of a chat message."""

    return {
        "name": row.name,
        "sender_type": row.sender_type,
        "sender": row.sender,
        "message": row.message,
        "attachment": row.attachment,
        "sent_at": row.sent_at,
        "read_by_doctor": row.read_by_doctor,
        "read_by_patient": row.read_by_patient,
    }


def _serialize_messages(rows):
    """Serialize all chat message child rows."""

    return [_serialize_message(row) for row in rows]