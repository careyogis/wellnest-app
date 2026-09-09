import frappe
from datetime import datetime

from .gemini_provider import parse_prescription


def process_prescription(
    image_bytes,
    patient,
    patient_appointment,
):    
    practitioner = None
    if patient_appointment:
        practitioner = frappe.get_value("Patient Appointment", patient_appointment, "practitioner")

    result = parse_prescription(image_bytes)
    prescription = result.get("prescription", result)

    doc = frappe.new_doc("Smart Prescription")

    doc.patient = patient
    
    # If this is written by our Doctor, we wait for him/her to review 
    # If this was done by some other doctor, there's no one to review - so we save it as final 
    if practitioner:
        doc.practitioner = practitioner
        doc.workflow_state = "Draft"
    else:
        doc.workflow_state = "Complete"

    if patient_appointment:
        doc.patient_appointment = patient_appointment

    doc.prescription_date = _parse_date(
        prescription.get("date")
    )
    doc.response_data = frappe.as_json(result)

    advice = []

    for instruction in prescription.get("general_instructions") or []:
        if isinstance(instruction, dict):
            text = instruction.get("instruction")
            translation = instruction.get("instruction_translation")

            if text:
                advice.append(
                    f"{text} ({translation})"
                    if translation else text
                )

    if advice:
        doc.advice = "\n".join(advice)

    for medicine in prescription.get("medicines") or []:
        item = doc.append("medicines", {})

        item.medicine_name = (
            medicine.get("normalized_name")
            or medicine.get("original_name")
            or ""
        )
        item.dosage = medicine.get("strength") or ""
        item.timing = medicine.get("frequency") or ""
        item.duration = medicine.get("duration") or ""
        item.instructions = medicine.get("instruction") or ""

    doc.insert(ignore_permissions=True)

    return doc.name


def _parse_date(value):
    if not value:
        return None

    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(
                str(value).strip(),
                fmt
            ).date()
        except ValueError:
            continue

    return None
