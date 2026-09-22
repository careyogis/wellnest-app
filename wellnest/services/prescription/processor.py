import frappe
from datetime import datetime, timedelta
import time
from frappe.utils.background_jobs import execute_job, get_queue

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

    doc.prescription_date = prescription.get("date") or ""

    # Diagnosis
    diagnoses = prescription.get("diagnosis") or []

    doc.diagnosis = "\n".join(
        str(diagnosis)
        for diagnosis in diagnoses
        if diagnosis
    )

    investigations = prescription.get("investigations") or []

    doc.investigations = _format_structured_items(
        investigations,
        "name",
    )

    general_instructions = (
        prescription.get("general_instructions") or []
    )

    doc.general_instructions = _format_structured_items(
        general_instructions,
        "instruction",
    )

    follow_up = prescription.get("follow_up") or {}

    doc.follow_up_duration = (
        follow_up.get("duration") or ""
    )

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
    attempt=1,
):
    MAX_OCR_ATTEMPTS = 5

    print("\n" + "=" * 80)
    print(">>> PRESCRIPTION OCR JOB START")
    print(f">>> Smart Prescription: {prescription}")
    print(f">>> File URL: {file_url}")
    print(f">>> Attempt: {attempt}/{MAX_OCR_ATTEMPTS}")
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
        print(f">>> Attempt: {attempt}")
        print("=" * 80 + "\n")

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Prescription OCR Job Failed",
        )

        print("\n" + "!" * 80)
        print(">>> PRESCRIPTION OCR JOB ERROR")
        print(f">>> Smart Prescription: {prescription}")
        print(f">>> Attempt: {attempt}/{MAX_OCR_ATTEMPTS}")
        print(f">>> Error: {str(e)}")
        print("!" * 80)

        if attempt >= MAX_OCR_ATTEMPTS:
            print(
                f">>> Maximum OCR attempts reached: "
                f"{MAX_OCR_ATTEMPTS}"
            )

            try:
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

            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "Failed to mark prescription as Failed",
                )

            try:
                patient_appointment = frappe.db.get_value(
                    "Smart Prescription",
                    prescription,
                    "patient_appointment",
                )

                if patient_appointment:
                    _publish_prescription_event(
                        patient_appointment,
                        "failed",
                        (
                            "Prescription processing failed "
                            "after multiple attempts. "
                            "Please re-upload the prescription."
                        ),
                    )

            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "Failed to publish prescription failure event",
                )

            print(
                ">>> PRESCRIPTION OCR JOB END - PERMANENT FAILURE"
            )
            print("=" * 80 + "\n")

            return

        delay = min(
            60 * (2 ** (attempt - 1)),
            3600,
        )

        next_attempt = attempt + 1

        print(
            f">>> OCR attempt failed. "
            f"Scheduling retry #{next_attempt}"
        )
        print(
            f">>> Retry delay: {delay} seconds"
        )

        queue = get_queue("long")

        queue.enqueue_in(
            timedelta(seconds=delay),
            execute_job,
            site=frappe.local.site,
            user=frappe.session.user,
            method=(
                "wellnest.services.prescription.processor."
                "process_prescription_job"
            ),
            event=None,
            job_name=(
                "wellnest.services.prescription.processor."
                "process_prescription_job"
            ),
            is_async=True,
            kwargs={
                "prescription": prescription,
                "file_url": file_url,
                "attempt": next_attempt,
            },
            timeout=1800,
        )

        print(
            f">>> RETRY QUEUED SUCCESSFULLY"
        )
        print(
            f">>> Next attempt: {next_attempt}/{MAX_OCR_ATTEMPTS}"
        )
        print(
            f">>> Retry after: {delay} seconds"
        )
        print(
            ">>> PRESCRIPTION OCR JOB END - RETRY SCHEDULED"
        )
        print("=" * 80 + "\n")


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