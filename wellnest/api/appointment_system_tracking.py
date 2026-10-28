
import frappe


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
