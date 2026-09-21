import frappe
from datetime import datetime

from .gemini_provider import parse_prescription
from frappe.utils.file_manager import save_file


def process_prescription(
    image_bytes,
    patient,
    patient_appointment,
    file_url,
):
    practitioner = None

    if patient_appointment:
        practitioner = frappe.get_value(
            "Patient Appointment",
            patient_appointment,
            "practitioner",
        )

    result = parse_prescription(image_bytes)

    parsed_result = result["parsed"]
    raw_response = result["raw_response"]

    if not parsed_result.get("is_prescription", True):
        return None

    prescription = parsed_result.get(
        "prescription",
        parsed_result,
    )

    doc = frappe.new_doc("Smart Prescription")

    doc.patient = patient

    if practitioner:
        doc.practitioner = practitioner
        doc.workflow_state = "Draft"
    else:
        doc.workflow_state = "Complete"

    if patient_appointment:
        doc.patient_appointment = patient_appointment

    doc.prescription_date = prescription.get("date") or ""

    # Diagnosis
    diagnoses = prescription.get("diagnosis") or []
    doc.diagnosis = "\n".join(
        str(diagnosis)
        for diagnosis in diagnoses
        if diagnosis
    )

    # Investigations
    investigations = prescription.get("investigations") or []
    doc.investigations = _format_structured_items(
        investigations,
        "name",
    )

    # General instructions
    general_instructions = prescription.get("general_instructions") or []
    doc.general_instructions = _format_structured_items(
        general_instructions,
        "instruction",
    )

    # Follow-up
    follow_up = prescription.get("follow_up") or {}
    doc.follow_up_duration = follow_up.get("duration") or ""

    # Medicines
    for medicine in prescription.get("medicines") or []:
        item = doc.append("medicines", {})

        item.medicine_name = (
            medicine.get("normalized_name")
            or medicine.get("original_name")
            or ""
        )

        item.original_name = medicine.get("original_name") or ""

        generic_names = medicine.get("generic_names") or []
        item.generic_names = ", ".join(
            str(name)
            for name in generic_names
            if name
        )

        item.dosage = medicine.get("strength") or ""
        item.dosage_form = medicine.get("dosage_form") or ""
        item.timing = medicine.get("frequency") or ""
        item.duration = medicine.get("duration") or ""
        item.instructions = medicine.get("instruction") or ""
        item.instruction_translation = (
            medicine.get("instruction_translation") or ""
        )

    doc.insert(ignore_permissions=True)

    # Save raw Gemini response
    gemini_file = save_file(
        f"{doc.name}-gemini-response.json",
        raw_response.encode("utf-8"),
        "Smart Prescription",
        doc.name,
        is_private=1,
        df="raw_ai_response",
    )

    doc.raw_ai_response = gemini_file.file_url
    doc.original_uploaded_prescription = file_url

    doc.save(ignore_permissions=True)

    return doc.name


def _format_structured_items(items, primary_key):
    formatted = []

    for item in items:
        if not isinstance(item, dict):
            continue

        primary = item.get(primary_key)
        instruction = item.get("instruction")
        translation = item.get("instruction_translation")

        parts = []

        if primary:
            parts.append(str(primary))

        if instruction:
            parts.append(str(instruction))

        if translation:
            parts.append(str(translation))

        if parts:
            formatted.append(" | ".join(parts))

    return "\n".join(formatted)


def _parse_date(value):
    if not value:
        return None

    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(
                str(value).strip(),
                fmt,
            ).date()
        except ValueError:
            continue

    return None