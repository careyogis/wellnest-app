import frappe
from datetime import timedelta
from frappe.utils import now_datetime


@frappe.whitelist()
def sweep_unverified_appointments(older_than_minutes: int = 30) -> dict:
    """
    Cleans up all 'Patient Appointment' records that are in 'Unverified' status
    and were created more than `older_than_minutes` minutes ago (default: 30 minutes).

    Intended to run as a scheduled cron task to free up abandoned appointment slots.

    Args:
        older_than_minutes (int): Threshold in minutes. Appointments created earlier than
                                  (now - older_than_minutes) will be swept. Defaults to 30.

    Returns:
        dict: Summary of the sweep operation including count and names of deleted documents.
    """
    try:
        older_than_minutes = int(older_than_minutes)
        if older_than_minutes < 0:
            older_than_minutes = 30
    except (ValueError, TypeError):
        older_than_minutes = 30

    cutoff_datetime = now_datetime() - timedelta(minutes=older_than_minutes)

    appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "status": "Unverified",
            "creation": ["<=", cutoff_datetime],
        },
        fields=["name"],
        order_by="creation asc",
    )

    deleted_appointments = []
    failed_appointments = []

    frappe.logger().info(
        f"[Sweep] Found {len(appointments)} 'Unverified' Patient Appointment(s) "
        f"created on or before {cutoff_datetime} to clean up."
    )

    for appt in appointments:
        appointment_name = appt["name"] if isinstance(appt, dict) else appt.name

        try:
            # Re-fetch status and payment_status to prevent race conditions
            current_status, current_payment_status = frappe.db.get_value(
                "Patient Appointment",
                appointment_name,
                ["status", "payment_status"],
            ) or (None, None)

            if current_status != "Unverified":
                frappe.logger().info(
                    f"[Sweep] Skipping {appointment_name}: status changed to '{current_status}'."
                )
                continue

            if current_payment_status == "Paid":
                frappe.logger().warning(
                    f"[Sweep] Skipping {appointment_name}: status is 'Unverified' but payment_status is 'Paid'."
                )
                continue

            frappe.delete_doc(
                "Patient Appointment",
                appointment_name,
                ignore_permissions=True,
                force=True,
            )
            frappe.db.commit()
            deleted_appointments.append(appointment_name)
            frappe.logger().info(
                f"[Sweep] Successfully deleted unverified Patient Appointment: {appointment_name}"
            )
        except Exception as e:
            frappe.db.rollback()
            frappe.log_error(
                title=f"Failed to sweep unverified Patient Appointment {appointment_name}",
                message=frappe.get_traceback(),
            )
            failed_appointments.append({"name": appointment_name, "error": str(e)})

    return {
        "success": True,
        "deleted_count": len(deleted_appointments),
        "deleted_appointments": deleted_appointments,
        "failed_count": len(failed_appointments),
        "failed_appointments": failed_appointments,
    }
