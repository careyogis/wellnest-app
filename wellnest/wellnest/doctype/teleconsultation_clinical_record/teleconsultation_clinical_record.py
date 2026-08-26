# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TeleconsultationClinicalRecord(Document):
    pass


@frappe.whitelist()
def get_clinical_record(appointment):
    record_name = frappe.db.get_value(
        "Teleconsultation Clinical Record",
        {"teleconsultation_appointment": appointment},
        "name",
    )

    if not record_name:
        return None

    record = frappe.get_doc("Teleconsultation Clinical Record", record_name)

    return {
        "name": record.name,
        "teleconsultation_appointment": record.teleconsultation_appointment,
        "patient": record.patient,
        "practitioner": record.practitioner,
        "consultation_date": record.consultation_date,
        "chief_complaints": [
            {
                "complaint": row.complaint,
                "duration": row.duration,
            }
            for row in record.chief_complaints
        ],
        "history": record.history,
        "examination": record.examination,
        "provisional_diagnosis": record.provisional_diagnosis,
        "investigations": [
            {
                "investigation": row.investigation,
            }
            for row in record.teleconsultation_investigation
        ],
        "follow_up_advice": record.follow_up_advice,
        "diet_advice": record.diet_advice,
        "exercise_advice": record.exercise_advice,
        "status": record.status,
    }

@frappe.whitelist()
def save_clinical_record(appointment, data):
    data = frappe.parse_json(data)

    appointment_doc = frappe.get_doc(
        "Teleconsultation Appointment",
        appointment
    )

    record_name = frappe.db.get_value(
        "Teleconsultation Clinical Record",
        {"teleconsultation_appointment": appointment},
        "name",
    )

    if record_name:
        record = frappe.get_doc(
            "Teleconsultation Clinical Record",
            record_name
        )
    else:
        record = frappe.new_doc("Teleconsultation Clinical Record")
        record.teleconsultation_appointment = appointment
        record.patient = appointment_doc.patient
        record.practitioner = appointment_doc.practitioner

    if data.get("consultation_date"):
        record.consultation_date = data.get("consultation_date")

    record.history = data.get("history")
    record.examination = data.get("examination")
    record.provisional_diagnosis = data.get("provisional_diagnosis")
    record.follow_up_advice = data.get("follow_up_advice")
    record.diet_advice = data.get("diet_advice")
    record.exercise_advice = data.get("exercise_advice")

    if data.get("status"):
        record.status = data.get("status")

    record.set("chief_complaints", [])

    for complaint in data.get("chief_complaints", []):
        row = record.append("chief_complaints", {})
        row.complaint = complaint.get("complaint")
        row.duration = complaint.get("duration")

    record.set("teleconsultation_investigation", [])

    for investigation in data.get("investigations", []):
        row = record.append("teleconsultation_investigation", {})
        row.investigation = investigation.get("investigation")

    if record_name:
        record.save()
    else:
        record.insert()

    return {
        "name": record.name,
        "teleconsultation_appointment": record.teleconsultation_appointment,
        "patient": record.patient,
        "practitioner": record.practitioner,
        "consultation_date": record.consultation_date,
        "chief_complaints": [
            {
                "complaint": row.complaint,
                "duration": row.duration,
            }
            for row in record.chief_complaints
        ],
        "history": record.history,
        "examination": record.examination,
        "provisional_diagnosis": record.provisional_diagnosis,
        "investigations": [
            {
                "investigation": row.investigation,
            }
            for row in record.teleconsultation_investigation
        ],
        "follow_up_advice": record.follow_up_advice,
        "diet_advice": record.diet_advice,
        "exercise_advice": record.exercise_advice,
        "status": record.status,
    }