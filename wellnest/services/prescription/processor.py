import frappe
from datetime import datetime


def _parse_date(value):
    if not value:
        return None

    value = str(value).strip()

    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def _find_patient(patient_name):
    if not patient_name:
        return None

    patient = frappe.db.get_value(
        "Patient",
        {"full_name": patient_name},
        "name"
    )

    if patient:
        return patient

    if frappe.db.exists("Patient", patient_name):
        return patient_name

    return None


def _create_medication(document_name, result):
    # Gemini may return the prescription directly or wrapped in "prescription"
    prescription = result.get("prescription", result)

    patient_data = prescription.get("patient") or {}
    doctor_data = prescription.get("doctor") or {}

    patient_name = patient_data.get("name")
    patient = _find_patient(patient_name)

    medication = frappe.new_doc("Medication")

    if patient:
        medication.patient = patient

    medication.prescribed_by = doctor_data.get("name")

    medication.custom_prescription_date = _parse_date(
        prescription.get("date")
    )

    medication.custom_hospital = prescription.get("hospital")

    diagnoses = prescription.get("diagnosis") or []

    if isinstance(diagnoses, list):
        medication.custom_diagnosis = "\n".join(
            str(item) for item in diagnoses
        )
    else:
        medication.custom_diagnosis = str(diagnoses)

    investigations = prescription.get("investigations") or []

    if investigations:
        medication.custom_investigations = frappe.as_json(
            investigations,
            indent=2
        )

    general_instructions = prescription.get(
        "general_instructions"
    ) or []

    if general_instructions:
        medication.custom_general_instructions = frappe.as_json(
            general_instructions,
            indent=2
        )

    follow_up = prescription.get("follow_up") or {}

    if isinstance(follow_up, dict):
        medication.custom_follow_up = (
            follow_up.get("duration")
            or follow_up.get("duration_original")
        )
    else:
        medication.custom_follow_up = str(follow_up)

    medicines = prescription.get("medicines") or []

    for medicine in medicines:
        item = medication.append("medication_items", {})

        original_name = medicine.get("original_name")
        normalized_name = medicine.get("normalized_name")

        item.medicine_name = (
            normalized_name
            or original_name
            or ""
        )

        item.frequency = medicine.get("frequency")
        item.dosage = medicine.get("dosage")

        item.custom_original_name = original_name
        item.custom_normalized_name = normalized_name

        generic_names = medicine.get("generic_names") or []

        if isinstance(generic_names, list):
            item.custom_generic_name = ", ".join(
                str(name) for name in generic_names
            )
        else:
            item.custom_generic_name = str(generic_names)

        item.custom_strength = medicine.get("strength")
        item.custom_dosage_form = medicine.get("dosage_form")
        item.custom_duration = medicine.get("duration")
        item.custom_instruction = medicine.get("instruction")
        item.custom_instruction_translation = medicine.get(
            "instruction_translation"
        )

    medication.insert(ignore_permissions=True)

    frappe.logger().info(
        f"Medication {medication.name} created from "
        f"Medical Document {document_name}"
    )

    return medication.name


def process_prescription(document_name):
    """
    Background job for processing a prescription Medical Document.
    """

    try:
        doc = frappe.get_doc("Medical Document", document_name)

        if doc.document_type != "Prescription":
            frappe.logger().info(
                f"Skipping {document_name}: document type is "
                f"{doc.document_type}"
            )
            return

        if not doc.file:
            frappe.throw("No prescription file attached to the document.")

        doc.db_set("processing_status", "Processing")
        doc.db_set("processing_error", None)
        doc.db_set("prescription_result", None)
        frappe.db.commit()

        file_url = doc.file

        if file_url.startswith("/files/"):
            file_path = frappe.get_site_path(
                "public",
                file_url.lstrip("/")
            )

        elif file_url.startswith("/private/files/"):
            file_name = file_url.split(
                "/private/files/",
                1
            )[1]

            file_path = frappe.get_site_path(
                "private",
                "files",
                file_name
            )

        else:
            frappe.throw(
                f"Unsupported file path: {file_url}"
            )

        with open(file_path, "rb") as file:
            image_bytes = file.read()

        if not image_bytes:
            frappe.throw("The prescription file is empty.")

        from wellnest.services.prescription.gemini_provider import (
            parse_prescription
        )

        result = parse_prescription(image_bytes)

        # Preserve the raw Gemini response
        doc.db_set(
            "prescription_result",
            frappe.as_json(result)
        )

        # Create structured Medication record
        medication_name = _create_medication(
            document_name,
            result
        )

        doc.db_set(
            "processing_status",
            "Completed"
        )

        doc.db_set(
            "processing_error",
            None
        )

        frappe.db.commit()

        frappe.logger().info(
            f"Prescription processing completed for {document_name}. "
            f"Medication created: {medication_name}"
        )

    except Exception as e:
        frappe.db.rollback()

        error_message = str(e)

        frappe.log_error(
            title=f"Prescription Processing Failed: {document_name}",
            message=frappe.get_traceback(),
        )

        try:
            doc = frappe.get_doc(
                "Medical Document",
                document_name
            )

            doc.db_set(
                "processing_status",
                "Failed"
            )

            doc.db_set(
                "processing_error",
                error_message
            )

            frappe.db.commit()

        except Exception:
            frappe.log_error(
                title=(
                    "Unable to update prescription "
                    f"failure status: {document_name}"
                ),
                message=frappe.get_traceback(),
            )

        raise
