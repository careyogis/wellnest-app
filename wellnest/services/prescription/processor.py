import frappe
from rq import get_current_job
from datetime import datetime

from .gemini_provider import parse_prescription
from frappe.utils.file_manager import save_file


def process_prescription(
    image_bytes,
    prescription_name,
):
    print("\n" + "-" * 80)
    print(">>> PRESCRIPTION OCR PROCESSING START")
    print(f">>> Smart Prescription: {prescription_name}")
    print("-" * 80)

    doc = frappe.get_doc(
        "Smart Prescription",
        prescription_name,
    )

    print(
        f">>> Existing Smart Prescription loaded: "
        f"{doc.name}"
    )
    print(
        f">>> Current workflow state: "
        f"{doc.workflow_state}"
    )

    print(">>> Sending prescription image for OCR processing...")

    result = parse_prescription(image_bytes)

    parsed_result = result["parsed"]
    raw_response = result["raw_response"]

    frappe.logger().info(
        f"Prescription OCR parsed result: {parsed_result}"
    )

    print(">>> OCR response received")

    if not parsed_result.get("is_prescription", True):
        frappe.logger().warning(
            f"Prescription OCR rejected image as non-prescription. "
            f"Appointment={doc.patient_appointment}"
        )

        print(
            ">>> OCR RESULT: Image was NOT identified as a prescription"
        )

        return {
            "success": False,
            "reason": "not_a_prescription",
        }

    print(">>> OCR RESULT: Valid prescription detected")

    prescription = parsed_result.get(
        "prescription",
        parsed_result,
    )

    doc.set("medicines", [])

        # Map Gemini prescription data to the single set of UI fields
    doc.prescription_date = prescription.get("date") or ""

    diagnoses = prescription.get("provisional_diagnosis") or []
    examinations = prescription.get("examination") or []

    provisional_diagnosis_items = []

    for diagnosis in diagnoses:
        if diagnosis:
            provisional_diagnosis_items.append(
                str(diagnosis)
        )

    for examination in examinations:
        if isinstance(examination, dict):
            examination_name = examination.get("name")
            if examination_name:
                provisional_diagnosis_items.append(
                    str(examination_name)
                )
        elif examination:
            provisional_diagnosis_items.append(
                str(examination)
            )

    doc.provisional_diagnosis = "\n".join(
        provisional_diagnosis_items
    )

    investigations = prescription.get("investigations") or []
    doc.investigations = _format_structured_items(
        investigations,
        "name",
    )

    # Follow-up in X days
    follow_up = prescription.get("follow_up") or {}
    follow_up_duration = follow_up.get("duration") or ""

    medicines = prescription.get("medicines") or []

    print(
        f">>> Medicines detected: {len(medicines)}"
    )

    for medicine in medicines:
        item = doc.append("medicines", {})

        item.medicine_name = (
            medicine.get("normalized_name")
            or medicine.get("original_name")
            or ""
        )

        item.original_name = (
            medicine.get("original_name") or ""
        )

        generic_names = (
            medicine.get("generic_names") or []
        )

        item.generic_names = ", ".join(
            str(name)
            for name in generic_names
            if name
        )

        item.dosage = (
            medicine.get("strength") or ""
        )

        item.dosage_form = (
            medicine.get("dosage_form") or ""
        )

        item.timing = (
            medicine.get("frequency") or ""
        )

        item.duration = (
            medicine.get("duration") or ""
        )

        item.instructions = (
            medicine.get("instruction") or ""
        )

        item.instruction_translation = (
            medicine.get("instruction_translation") or ""
        )

    print(">>> Saving raw Gemini response...")

    gemini_file = save_file(
        f"{doc.name}-gemini-response.json",
        raw_response.encode("utf-8"),
        "Smart Prescription",
        doc.name,
        is_private=1,
        df="raw_ai_response",
    )

    doc.raw_ai_response = gemini_file.file_url

    doc.workflow_state = "Draft"

    print(
        f">>> Updating workflow state: "
        f"{doc.workflow_state}"
    )

    doc.save(ignore_permissions=True)

    frappe.db.commit()

    print(
        f">>> Smart Prescription updated successfully: "
        f"{doc.name}"
    )
    print(
        ">>> PRESCRIPTION OCR PROCESSING COMPLETE"
    )
    print("-" * 80 + "\n")

    return {
        "success": True,
        "name": doc.name,
    }


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

def process_prescription_job(
    prescription,
    file_url,
):
    print("\n" + "=" * 80)
    print(">>> PRESCRIPTION OCR JOB START")
    print(f">>> Smart Prescription: {prescription}")
    print(f">>> File URL: {file_url}")
    print("=" * 80)

    try:
        doc = frappe.get_doc(
            "Smart Prescription",
            prescription,
        )

        print(
            f">>> Smart Prescription loaded: "
            f"{doc.name}"
        )
        print(
            f">>> Workflow state: "
            f"{doc.workflow_state}"
        )

        patient_appointment = doc.patient_appointment

        if not patient_appointment:
            raise Exception(
                "Smart Prescription has no Patient Appointment."
            )

        print(
            f">>> Patient Appointment: "
            f"{patient_appointment}"
        )

        file_doc = frappe.db.get_value(
            "File",
            {
                "file_url": file_url,
            },
            [
                "name",
                "file_url",
                "is_private",
            ],
            as_dict=True,
        )

        if not file_doc:
            raise Exception(
                f"Uploaded prescription file not found: {file_url}"
            )

        print(
            f">>> File found: "
            f"{file_doc.name}"
        )
        print(
            f">>> File privacy: "
            f"{'Private' if file_doc.is_private else 'Public'}"
        )

        if file_doc.is_private:
            file_path = frappe.get_site_path(
                "private",
                "files",
                file_url.split("/private/files/")[-1],
            )
        else:
            file_path = frappe.get_site_path(
                "public",
                "files",
                file_url.split("/files/")[-1],
            )

        print(
            f">>> Resolved file path: "
            f"{file_path}"
        )

        print(">>> Reading prescription file...")

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        print(
            f">>> Prescription file loaded successfully "
            f"({len(image_bytes)} bytes)"
        )

        print(">>> Starting OCR processing...")

        result = process_prescription(
            image_bytes,
            prescription,
        )

        if not result or not result.get("success"):
            reason = (
                result.get("reason")
                if result
                else "unknown"
            )

            print(
                f">>> OCR PROCESSING FAILED: "
                f"{reason}"
            )

            doc = frappe.get_doc(
                "Smart Prescription",
                prescription,
            )

            doc.workflow_state = "Failed"
            doc.save(ignore_permissions=True)

            frappe.db.commit()

            print(
                f">>> Smart Prescription marked as Failed: "
                f"{doc.name}"
            )

            _publish_prescription_event(
                patient_appointment,
                "failed",
                (
                    "The uploaded image could not be "
                    "identified as a prescription."
                ),
            )

            print(">>> PRESCRIPTION OCR JOB END - FAILED")
            print("=" * 80 + "\n")

            return

        print(
            f">>> OCR processing completed successfully: "
            f"{prescription}"
        )

        file_doc = frappe.get_doc(
            "File",
            file_doc.name,
        )

        file_doc.attached_to_doctype = "Smart Prescription"
        file_doc.attached_to_name = prescription
        file_doc.save(ignore_permissions=True)

        frappe.db.commit()

        print(
            f">>> Uploaded prescription file attached to: "
            f"{prescription}"
        )

        _publish_prescription_event(
            patient_appointment,
            "completed",
            (
                "Prescription processed successfully. "
                "Please review and edit before publishing."
            ),
        )

        print(
            ">>> PRESCRIPTION OCR JOB COMPLETED SUCCESSFULLY"
        )
        print(f">>> Smart Prescription: {prescription}")
        print("=" * 80 + "\n")

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Prescription OCR Attempt Failed",
        )

        print("\n" + "!" * 80)
        print(">>> PRESCRIPTION OCR ATTEMPT FAILED")
        print(f">>> Smart Prescription: {prescription}")

        job = get_current_job()
        retries_left = getattr(job, "retries_left", None)

        print(f">>> RQ retries left: {retries_left}")

        if retries_left == 0:
            print(">>> NO RQ RETRIES LEFT")
            print(">>> Marking Smart Prescription as Failed")

            try:
                doc = frappe.get_doc(
                    "Smart Prescription",
                    prescription,
                )

                if doc.workflow_state == "Processing":
                    doc.workflow_state = "Failed"
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()

                    print(
                        f">>> Smart Prescription marked as Failed: "
                        f"{doc.name}"
                    )

                _publish_prescription_event(
                    patient_appointment,
                    "failed",
                    (
                        "Prescription processing failed after multiple "
                        "attempts. Please upload the prescription again."
                    ),
                )

            except Exception:
               frappe.log_error(
                   frappe.get_traceback(),
                   "Failed to mark prescription OCR as Failed",
                )

        else:
            print(
                ">>> RQ will retry this job according to "
                "the configured retry policy."
            )

        print("!" * 80)

        raise


def _publish_prescription_event(
    patient_appointment,
    status,
    message,
):
    practitioner = frappe.db.get_value(
        "Patient Appointment",
        patient_appointment,
        "practitioner",
    )

    doctor_user = None

    if practitioner:
        doctor_user = frappe.db.get_value(
            "Practitioner",
            practitioner,
            "user_id",
        )

    event_data = {
        "patient_appointment": patient_appointment,
        "status": status,
        "message": message,
    }

    if doctor_user:
        frappe.publish_realtime(
            "prescription_ocr_completed",
            event_data,
            user=doctor_user,
        )
    else:
        frappe.publish_realtime(
            "prescription_ocr_completed",
            event_data,
        )

def handle_prescription_ocr_failure(
    job,
    connection,
    exc_type,
    exc_value,
    traceback,
):
    """
    Called by RQ only when the OCR job reaches its final failure
    after all configured retries.
    """

    retries_left = getattr(job, "retries_left", None)

    if retries_left is not None and retries_left > 0:
        print(
            f">>> OCR job failed, but {retries_left} "
            f"retries remain. Leaving prescription as Processing."
        )
        return

    kwargs = job.kwargs.get("kwargs", {})
    prescription = kwargs.get("prescription")

    if not prescription:
        return

    site = job.kwargs.get("site")
    user = job.kwargs.get("user")

    try:
        frappe.init(site=site, force=True, is_job=True)
        frappe.connect()

        if user:
            frappe.set_user(user)

        doc = frappe.get_doc(
            "Smart Prescription",
            prescription,
        )

        if doc.workflow_state == "Processing":
            doc.workflow_state = "Failed"
            doc.save(ignore_permissions=True)
            frappe.db.commit()

        patient_appointment = doc.patient_appointment

        if patient_appointment:
            _publish_prescription_event(
                patient_appointment,
                "failed",
                (
                    "Prescription processing failed after multiple "
                    "attempts. Please upload the prescription again."
                ),
            )

        frappe.log_error(
            (
                f"Smart Prescription: {prescription}\n"
                f"Error: {exc_type.__name__ if exc_type else 'Unknown'}: "
                f"{exc_value}\n\n"
                f"{traceback}"
            ),
            "Prescription OCR Job Failed",
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Failed to mark prescription OCR as Failed",
        )

    finally:
        frappe.destroy()