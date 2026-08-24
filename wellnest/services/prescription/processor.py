import frappe
from datetime import datetime


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

        if doc.medication:
            frappe.logger().info(
                f"Skipping {document_name}: Medication "
                f"{doc.medication} already exists."
            )
            return

        doc.db_set("processing_status", "Processing")
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

        doc.db_set(
            "prescription_result",
            frappe.as_json(result)
        )

        medication_name = _create_medication(
            document_name,
            result,
            doc.patient
        )

        doc.db_set("medication", medication_name)

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


def _create_medication(document_name, result, patient):
    prescription = result.get("prescription", result)
    doctor_data = prescription.get("doctor") or {}

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

    medication_fields = [
        "original_name",
        "normalized_name",
        "strength",
        "dosage_form",
        "duration",
        "instruction",
        "instruction_translation",
    ]

    for medicine in prescription.get("medicines") or []:
        item = medication.append("medication_items", {})

        original_name = medicine.get("original_name")
        normalized_name = medicine.get("normalized_name")

        item.medicine_name = normalized_name or original_name or ""
        item.frequency = medicine.get("frequency")

        generic_names = medicine.get("generic_names") or []

        if isinstance(generic_names, list):
            item.custom_generic_name = ", ".join(
                str(name) for name in generic_names
            )
        else:
            item.custom_generic_name = str(generic_names)

        for field in medication_fields:
            setattr(
                item,
                f"custom_{field}",
                medicine.get(field)
            )

    medication.insert(ignore_permissions=True)

    frappe.logger().info(
        f"Medication {medication.name} created from "
        f"Medical Document {document_name}"
    )

    return medication.name


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
