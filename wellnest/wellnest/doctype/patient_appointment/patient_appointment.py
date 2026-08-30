# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import hashlib

import frappe
from frappe.model.document import Document

from wellnest.api.teleconsult import get_agora_token


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

def _get_agora_uid(user):
    """Return a stable numeric Agora UID for a user."""
    digest = hashlib.sha256(user.encode("utf-8")).digest()
    return (int.from_bytes(digest[:4], "big") % 99999) + 1


def _get_current_practitioner():
    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found")

    return practitioner


def _get_appointment_for_current_practitioner(appointment_name):
    appointment = frappe.get_doc("Patient Appointment", appointment_name)

    practitioner = _get_current_practitioner()

    if appointment.practitioner != practitioner:
        frappe.throw("You are not authorized to access this appointment")

    return appointment



@frappe.whitelist()
def start_consultation(appointment):
    appointment = _get_appointment_for_current_practitioner(appointment)

    if appointment.consultation_type != "Online":
        frappe.throw("Only online appointments can be started")

    if appointment.consultation_status != "Scheduled":
        frappe.throw(
            "Consultation can only be started from Scheduled status"
        )

    if not appointment.video_room_id:
        appointment.db_set("video_room_id", appointment.name)
        appointment.reload()

    uid = _get_agora_uid(frappe.session.user)

    token_response = get_agora_token(
        channel_name=appointment.video_room_id,
        uid=uid,
        role="publisher",
    )

    # Customer app polls this field to detect when to join RTC
    appointment.db_set("consultation_status", "In-Progress")

    return {
        "appointment": appointment.name,
        "video_room_id": appointment.video_room_id,
        "channel_name": appointment.video_room_id,
        "uid": uid,
        "rtcToken": token_response["rtcToken"],
        "consultation_status": "In-Progress",
    }


@frappe.whitelist()
def end_consultation(appointment):
    appointment = _get_appointment_for_current_practitioner(appointment)

    if appointment.consultation_status != "In-Progress":
        frappe.throw(
            "Only an in-progress consultation can be ended"
        )

    appointment.db_set("consultation_status", "Completed")

    return {
        "appointment": appointment.name,
        "consultation_status": "Completed",
    }