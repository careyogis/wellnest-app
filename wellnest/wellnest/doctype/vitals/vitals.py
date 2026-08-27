# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Vitals(Document):
    pass


@frappe.whitelist()
def get_consultation_vitals(appointment):
    """
    Get the Vitals record associated with a teleconsultation appointment.
    """

    current_practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not current_practitioner:
        frappe.throw("Practitioner not found")

    appointment_practitioner = frappe.db.get_value(
        "Patient Appointment",
        appointment,
        "practitioner",
    )

    if not appointment_practitioner:
        frappe.throw(
            "Patient Appointment not found",
            frappe.DoesNotExistError,
        )

    if appointment_practitioner != current_practitioner:
        frappe.throw(
            "Not authorized to access this consultation",
            frappe.PermissionError,
        )

    vital_name = frappe.db.get_value(
        "Vitals",
        {"teleconsultation_appointment": appointment},
        "name",
    )

    if not vital_name:
        return None

    vital_doc = frappe.get_doc("Vitals", vital_name)

    return {
        "name": vital_doc.name,
        "patient": vital_doc.patient,
        "practitioner": vital_doc.practitioner,
        "teleconsultation_appointment": vital_doc.teleconsultation_appointment,
        "recorded_on": vital_doc.recorded_on,
        "recorded_by": vital_doc.recorded_by,
        "vital_reading": [
            {
                "vital_type": row.vital_type,
                "unit": row.unit,
                "value": row.value,
                "remarks": row.remarks,
            }
            for row in vital_doc.vital_reading
        ],
    }


@frappe.whitelist()
def save_consultation_vitals(appointment, readings):
    """
    Create or update the Vitals record for a teleconsultation appointment.
    """

    readings = frappe.parse_json(readings)

    appointment_doc = frappe.get_doc(
        "Patient Appointment",
        appointment,
    )

    vital_name = frappe.db.get_value(
        "Vitals",
        {"teleconsultation_appointment": appointment},
        "name",
    )

    if vital_name:
        vital_doc = frappe.get_doc("Vitals", vital_name)
    else:
        vital_doc = frappe.new_doc("Vitals")

        vital_doc.patient = appointment_doc.patient
        vital_doc.practitioner = appointment_doc.practitioner
        vital_doc.teleconsultation_appointment = appointment

    vital_doc.recorded_by = frappe.session.user
    vital_doc.recorded_on = frappe.utils.now_datetime()

    # Replace the existing readings with the current consultation values.
    vital_doc.set("vital_reading", [])

    for reading in readings:
        if not reading.get("value"):
            continue

        row = vital_doc.append("vital_reading", {})

        row.vital_type = reading.get("vital_type")
        row.unit = reading.get("unit")
        row.value = reading.get("value")
        row.remarks = reading.get("remarks")

    if vital_name:
        vital_doc.save()
    else:
        vital_doc.insert()

    return {
        "name": vital_doc.name,
        "patient": vital_doc.patient,
        "practitioner": vital_doc.practitioner,
        "teleconsultation_appointment": vital_doc.teleconsultation_appointment,
        "recorded_on": vital_doc.recorded_on,
        "vital_reading": [
            {
                "vital_type": row.vital_type,
                "unit": row.unit,
                "value": row.value,
                "remarks": row.remarks,
            }
            for row in vital_doc.vital_reading
        ],
    }