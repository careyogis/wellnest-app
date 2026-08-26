# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class PatientAppointment(Document):
	pass
import frappe
from frappe.model.document import Document


class TeleconsultationAppointment(Document):
    pass


@frappe.whitelist()
def get_teleconsultation_appointments():
    return frappe.get_all(
        "Teleconsultation Appointment",
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