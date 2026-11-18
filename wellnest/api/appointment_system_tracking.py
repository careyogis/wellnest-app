import frappe
from frappe.utils import add_months, now_datetime, get_datetime


def get_or_create_tracking(appointment_name):
    """Return the system-tracking record for a Patient Appointment."""
    tracking_name = frappe.db.get_value(
        "Appointment System Tracking",
        {"patient_appointment": appointment_name},
        "name",
    )

    if tracking_name:
        return frappe.get_doc("Appointment System Tracking", tracking_name)

    tracking = frappe.get_doc({
        "doctype": "Appointment System Tracking",
        "patient_appointment": appointment_name,
    })

    try:
        tracking.insert(ignore_permissions=True)
        return tracking
    except frappe.DuplicateEntryError:
        # Another worker may have created this record concurrently.
        tracking_name = frappe.db.get_value(
            "Appointment System Tracking",
            {"patient_appointment": appointment_name},
            "name",
        )
        if tracking_name:
            return frappe.get_doc("Appointment System Tracking", tracking_name)
        raise

def update_consultation_completion(appointment_name, event_type, event_time=None):
    """Record consultation events and create activity once both are complete."""

    tracking = get_or_create_tracking(appointment_name)
    event_time = event_time or now_datetime()

    if event_type == "consultation":
        if not tracking.consultation_ended_at:
            tracking.db_set("consultation_ended_at", event_time)

    elif event_type == "prescription":
        if not tracking.prescription_completed_at:
            tracking.db_set("prescription_completed_at", event_time)

    else:
        frappe.throw("Invalid consultation completion event.")

    tracking.reload()

    consultation_ended_at = tracking.consultation_ended_at
    prescription_completed_at = tracking.prescription_completed_at

    # Both events must be completed before the consultation is fully complete.
    if not consultation_ended_at or not prescription_completed_at:
        return

    overall_completed_at = max(
        get_datetime(consultation_ended_at),
        get_datetime(prescription_completed_at),
    )

    tracking.db_set("overall_completed_at", overall_completed_at)

    appointment = frappe.get_doc(
        "Patient Appointment",
        appointment_name,
    )

    event_key = f"consultation-completed:{appointment.name}"

    existing_activity = frappe.db.get_value(
        "Patient Activity",
        {"event_key": event_key},
        "name",
    )

    if existing_activity:
        frappe.db.set_value(
            "Patient Activity",
            existing_activity,
            "event_time",
            overall_completed_at,
        )
        return

    activity = frappe.get_doc({
        "doctype": "Patient Activity",
        "practitioner": appointment.practitioner,
        "patient": appointment.patient,
        "patient_appointment": appointment.name,
        "activity_type": "Consultation completed",
        "event_key": event_key,
        "event_time": overall_completed_at,
    })

    try:
        activity.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        if not frappe.db.exists("Patient Activity", {"event_key": event_key}):
            raise

def create_health_vault_patient_activity(doc, method=None):
    """Create a Patient Activity when a Health Vault record is uploaded."""

    if not doc.patient:
        return

    appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "patient": doc.patient,
            "practitioner": ["is", "set"],
        },
        fields=["name", "practitioner"],
        order_by="scheduled_time desc, creation desc",
        limit_page_length=1,
    )

    if not appointments:
        return

    appointment = appointments[0]
    event_key = f"medical-report:{doc.name}"

    if frappe.db.exists("Patient Activity", {"event_key": event_key}):
        return

    activity = frappe.get_doc({
        "doctype": "Patient Activity",
        "practitioner": appointment.practitioner,
        "patient": doc.patient,
        "patient_appointment": appointment.name,
        "activity_type": "Medical report uploaded",
        "event_key": event_key,
        "event_time": doc.creation or now_datetime(),
    })

    try:
        activity.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        if not frappe.db.exists("Patient Activity", {"event_key": event_key}):
            raise

@frappe.whitelist()
def get_patient_activities():
    if frappe.session.user == "Guest":
        frappe.throw(
            "Please log in to view patient activity.",
            frappe.PermissionError,
        )

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found")

    current_time = now_datetime()
    one_month_ago = add_months(current_time, -1)

    activities = frappe.get_all(
        "Patient Activity",
        filters={
            "practitioner": practitioner,
            "event_time": ["between", [one_month_ago, current_time]],
        },
        fields=[
            "patient",
            "patient_appointment",
            "activity_type",
            "event_time",
            "event_key",
        ],
        order_by="event_time desc",
    )

    for activity in activities:
        activity["patient_name"] = frappe.db.get_value(
            "Patient",
            activity["patient"],
            "full_name",
        ) or activity["patient"]

    return activities
