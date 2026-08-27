# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatientAppointment(Document):
    pass


@frappe.whitelist()
def get_teleconsultation_appointments():
    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found")

    return frappe.get_all(
        "Patient Appointment",
        filters={
            "practitioner": practitioner,
            "consultation_type": "Online",
        },
        fields=[
            "name",
            "patient",
            "practitioner",
            "scheduled_time",
            "consultation_status",
            "consultation_fee",
            "payment_status",
            "video_room_id",
        ],
        order_by="scheduled_time asc",
    )