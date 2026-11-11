
import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def get_doctor_notifications(page=1, page_length=20, status="All"):
    """Return paginated notification history for the logged-in doctor."""

    practitioner = _get_current_practitioner()

    try:
        page = max(1, int(page))
        page_length = min(100, max(1, int(page_length)))
    except (TypeError, ValueError):
        frappe.throw("Invalid pagination parameters.")

    if status not in ("All", "Read", "Unread"):
        frappe.throw("Invalid notification status.")

    filters = {"practitioner": practitioner}

    if status == "Read":
        filters["is_read"] = 1
    elif status == "Unread":
        filters["is_read"] = 0

    total = frappe.db.count("Doctor Notification", filters=filters)

    notifications = frappe.get_all(
        "Doctor Notification",
        filters=filters,
        fields=[
            "name",
            "notification_type",
            "patient",
            "patient_appointment",
            "message_id",
            "title",
            "description",
            "event_time",
            "is_read",
            "read_at",
        ],
        order_by="event_time desc, creation desc",
        start=(page - 1) * page_length,
        page_length=page_length,
    )

    for notification in notifications:
        notification["patient_name"] = (
            frappe.db.get_value(
                "Patient",
                notification["patient"],
                "full_name",
            )
            or notification["patient"]
        )

    return {
        "notifications": notifications,
        "total": total,
        "page": page,
        "page_length": page_length,
        "has_more": page * page_length < total,
    }


@frappe.whitelist()
def mark_doctor_notification_read(notification_name):
    """Mark one notification as read for the logged-in doctor."""

    practitioner = _get_current_practitioner()

    if not notification_name:
        frappe.throw("Notification ID is required.")

    notification = frappe.get_doc(
        "Doctor Notification",
        notification_name,
    )

    if notification.practitioner != practitioner:
        frappe.throw(
            "You are not authorized to access this notification.",
            frappe.PermissionError,
        )

    if not notification.is_read:
        notification.is_read = 1
        notification.read_at = now_datetime()
        notification.save(ignore_permissions=True)

    return {
        "success": True,
        "is_read": notification.is_read,
        "read_at": notification.read_at,
    }


@frappe.whitelist()
def mark_all_doctor_notifications_read():
    """Mark all unread notifications as read for the logged-in doctor."""

    practitioner = _get_current_practitioner()
    read_time = now_datetime()

    unread_notifications = frappe.get_all(
        "Doctor Notification",
        filters={
            "practitioner": practitioner,
            "is_read": 0,
        },
        pluck="name",
    )

    for notification_name in unread_notifications:
        frappe.db.set_value(
            "Doctor Notification",
            notification_name,
            {
                "is_read": 1,
                "read_at": read_time,
            },
        )

    return {
        "success": True,
        "updated_count": len(unread_notifications),
        "read_at": read_time,
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


def create_doctor_notification(
    practitioner,
    patient,
    patient_appointment,
    notification_type,
    event_key,
    title,
    description,
    event_time=None,
    message_id=None,
):
    """Create a doctor notification once for a unique event."""

    if not event_key:
        frappe.throw("Notification event key is required.")

    if frappe.db.exists(
        "Doctor Notification",
        {"event_key": event_key},
    ):
        return None

    notification = frappe.get_doc({
        "doctype": "Doctor Notification",
        "practitioner": practitioner,
        "patient": patient,
        "patient_appointment": patient_appointment,
        "notification_type": notification_type,
        "event_key": event_key,
        "title": title,
        "description": description,
        "event_time": event_time or now_datetime(),
        "message_id": message_id,
        "is_read": 0,
    })

    try:
        notification.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        # Another request already created this event.
        return None

    return notification.name
