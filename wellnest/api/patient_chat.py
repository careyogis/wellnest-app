import frappe
from frappe.utils import now_datetime


# Public APIs

@frappe.whitelist()
def get_doctor_patient_chats():
    """Return chat conversations belonging to the logged-in doctor."""

    practitioner = _get_current_practitioner()

    appointments = frappe.get_all(
        "Patient Appointment",
        filters={"practitioner": practitioner},
        fields=[
            "name",
            "patient",
            "scheduled_time",
            "status",
        ],
        order_by="scheduled_time desc",
    )

    conversations = []

    for appointment_data in appointments:
        appointment = frappe.get_doc(
            "Patient Appointment",
            appointment_data.name,
        )

        messages = appointment.patient_chat_messages or []

        # Show only appointments with an existing chat history.
        if not messages:
            continue

        # Find the associated prescription and follow-up period.
        prescription_name = frappe.db.get_value(
            "Smart Prescription",
            {"patient_appointment": appointment.name},
            "name",
        )

        prescription = None
        if prescription_name:
            prescription = frappe.db.get_value(
                "Smart Prescription",
                prescription_name,
                ["workflow_state", "follow_up_in_days", "modified"],
                as_dict=True,
            )

        follow_up_days = int(
            (prescription.follow_up_in_days if prescription else 0) or 0
        )

        completed_at = prescription.modified if prescription else None

        follow_up_active = False

        if (
            prescription
            and prescription.workflow_state == "Complete"
            and follow_up_days > 0
            and completed_at
        ):
            follow_up_active = (
                now_datetime()
                <= frappe.utils.add_days(completed_at, follow_up_days)
            )

        latest_message = messages[-1] if messages else None

        unread_count = sum(
            1
            for message in messages
            if message.sender_type == "Patient"
            and not message.read_by_doctor
        )

        patient_name = frappe.db.get_value(
            "Patient",
            appointment.patient,
            "full_name",
        ) or appointment.patient

        conversations.append({
            "appointment": appointment.name,
            "patient": appointment.patient,
            "patient_name": patient_name,
            "scheduled_time": appointment.scheduled_time,
            "status": appointment.status,
            "latest_message": (
                latest_message.message or (
                    "Attachment" if latest_message.attachment else ""
                )
            ) if latest_message else "",
            "latest_message_at": (
                latest_message.sent_at if latest_message else None
            ),
            "unread_count": unread_count,
            "chat_status": "Active" if follow_up_active else "Closed",
        })

    conversations.sort(
        key=lambda item: item["latest_message_at"] or item["scheduled_time"],
        reverse=True,
    )

    return {"conversations": conversations}


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