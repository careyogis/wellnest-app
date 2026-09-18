# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import hashlib

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime

from wellnest.api.teleconsult import get_agora_token
from wellnest.api.notifications import notify_doctor_of_new_booking


class PatientAppointment(Document):
    def after_insert(self):
        try:
            # Notify the doctor of the new booking
            practitioner = frappe.get_value(
                "Practitioner",
                self.practitioner,
                ["full_name", "email", "mobile"],
                as_dict=True,
            )

            patient = frappe.get_value(
                "Patient",
                self.patient,
                ["full_name", "date_of_birth"],
                as_dict=True,
            )

            site_url = frappe.utils.get_url()

            # Convert the string to a datetime object, then format it
            scheduled_time_obj = get_datetime(self.scheduled_time)
            formatted_date_time = scheduled_time_obj.strftime("%d-%m-%Y %I:%M %p")

            if practitioner and practitioner.email:
                frappe.sendmail(
                    recipients=[practitioner.email],
                    subject="A new consultation has booked for you at CareYogi",
                    message=f"""Hello <b>{practitioner.full_name}</b>,<br/>

                A new consultation has been booked for you at CareYogi.<br/><br/>

                <b>Patient</b>: {patient.full_name if patient else self.patient}<br/>
                <b>Age</b>: {patient.date_of_birth if patient else ""}<br/>
                <b>Reason</b>: {self.main_complaints}<br/>
                <b>Date/Time</b>: {formatted_date_time}.<br/>
                <b>Consultation Mode</b>: {self.consultation_type}.<br/>

                Please ensure you login to the <a href='{site_url}/doctor-app/consultations'>doctor-app</a> at or before the scheduled time.<br/><br/>

                With regards,<br/>
                CareYogi Digital Hospital<br/>
                """
                )

            if practitioner and practitioner.mobile:
                notify_doctor_of_new_booking(
                    patient_appointmentId=self.name,
                    practitioner_name=practitioner.full_name,
                    practitioner_mobile=practitioner.mobile,
                    scheduled_datetime=formatted_date_time,
                    consultation_type=self.consultation_type,
                    patient_name=patient.full_name if patient else self.patient,
                    patient_dob=patient.date_of_birth if patient else None,
                    reason=self.main_complaints,
                )
        except:
            frappe.log_error(
                title="Failed to notify the doctor about the appointment",
                message=frappe.get_traceback(),
            )


@frappe.whitelist()
def get_teleconsultation_appointments():
    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found")

    appointments = frappe.get_all(
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
            "status",
            "consultation_fee",
            "payment_status",
            "main_complaints",
        ],
        order_by="scheduled_time asc",
    )

    for appointment in appointments:
        appointment["patient_name"] = frappe.db.get_value(
            "Patient",
            appointment["patient"],
            "full_name",
        ) or appointment["patient"]

        appointment["prescription_workflow_state"] = frappe.db.get_value(
            "Smart Prescription",
            {"patient_appointment": appointment["name"]},
            "workflow_state",
        )

    return appointments

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
def start_consultation(appointmentId):
    appointment = _get_appointment_for_current_practitioner(appointmentId)

    if appointment.consultation_type != "Online":
        frappe.throw("Only online appointments can be started")

    if appointment.status != "In-Progress" and appointment.status != "Scheduled":
        frappe.throw(
            f"Consultation can only be started from Scheduled or In-Progress status. Current status for appt: {appointment.name} is {appointment.status}"
        )

    uid = _get_agora_uid(frappe.session.user)

    token_response = get_agora_token(
        channel_name=appointment.name,
        uid=uid,
        role="publisher",
    )

    # Customer app polls this field to detect when to join RTC
    appointment.db_set("status", "In-Progress")

    return {
        "channel_name": appointment.name,
        "uid": uid,
        "rtcToken": token_response["rtcToken"],
        "appId": token_response.get("appId"),
        "status": appointment.status,
    }


@frappe.whitelist()
def end_consultation(appointment):
    appointment = _get_appointment_for_current_practitioner(appointment)

    if appointment.status != "In-Progress":
        frappe.throw(
            "Only an in-progress consultation can be ended"
        )

    appointment.db_set("status", "Completed")

    return {
        "appointment": appointment.name,
        "status": "Completed",
    }