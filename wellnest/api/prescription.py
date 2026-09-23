import frappe

from wellnest.services.prescription.processor import process_prescription


@frappe.whitelist()
def parse_and_create_prescription(
    file_url=None,
    patient_appointment=None,
):
    print("\n" + "=" * 80)
    print(">>> PRESCRIPTION API START")
    print(f">>> Logged-in user: {frappe.session.user}")
    print(f">>> Appointment: {patient_appointment}")
    print(f">>> File URL: {file_url}")
    print("=" * 80)

    if not patient_appointment:
        print(">>> ERROR: Patient appointment is missing")
        frappe.throw("Patient appointment is required.")

    if not file_url:
        print(">>> ERROR: Prescription file is missing")
        frappe.throw("Prescription file is required.")

    print(">>> Basic validation passed")

    appointment_doc = frappe.get_doc(
        "Patient Appointment",
        patient_appointment,
    )

    print(
        f">>> Appointment loaded successfully: "
        f"{appointment_doc.name}"
    )
    print(f">>> Appointment patient: {appointment_doc.patient}")
    print(
        f">>> Appointment practitioner: "
        f"{appointment_doc.practitioner}"
    )

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    print(f">>> Logged-in practitioner: {practitioner}")

    if not practitioner:
        print(">>> ERROR: No practitioner found for logged-in user")
        frappe.throw("Practitioner not found.")

    if appointment_doc.practitioner != practitioner:
        print(">>> AUTHORIZATION FAILED")
        print(
            f">>> Appointment practitioner: "
            f"{appointment_doc.practitioner}"
        )
        print(
            f">>> Logged-in practitioner: "
            f"{practitioner}"
        )

        frappe.throw(
            "You are not authorized to upload a prescription for this appointment.",
            frappe.PermissionError,
        )

    print(">>> Practitioner authorization passed")

    existing = frappe.db.get_value(
        "Smart Prescription",
        {
            "patient_appointment": patient_appointment,
        },
        ["name", "workflow_state"],
        as_dict=True,
    )

    if existing:
        print(
            f">>> Existing Smart Prescription found: "
            f"{existing.name}"
        )
        print(
            f">>> Existing workflow state: "
            f"{existing.workflow_state}"
        )
    else:
        print(">>> No existing Smart Prescription found")

    if existing and existing.workflow_state == "Processing":
        print(">>> Existing prescription is currently processing")
        print(
            f">>> Returning existing prescription: "
            f"{existing.name}"
        )
        print(
            f">>> Existing state: "
            f"{existing.workflow_state}"
        )
        print(">>> PRESCRIPTION API END - ALREADY PROCESSING")
        print("=" * 80 + "\n")

        return {
            "status": "already_exists",
            "name": existing.name,
            "workflow_state": existing.workflow_state,
            "message": (
                "A prescription is already being "
                "processed for this consultation."
            ),
        }

    if existing and existing.workflow_state in ("Draft", "Failed"):
        print(
            f">>> Reusing previously failed prescription: "
            f"{existing.name}"
        )

        doc = frappe.get_doc(
            "Smart Prescription",
            existing.name,
        )

    else:
        print(">>> Creating new Smart Prescription")

        doc = frappe.new_doc("Smart Prescription")

        doc.patient = appointment_doc.patient
        doc.practitioner = practitioner
        doc.patient_appointment = patient_appointment

        print(
            f">>> New prescription prepared for patient: "
            f"{appointment_doc.patient}"
        )

    doc.workflow_state = "Processing"
    doc.original_uploaded_prescription = file_url

    print(
        f">>> Setting prescription workflow state: "
        f"{doc.workflow_state}"
    )
    print(
        f">>> Original prescription file: "
        f"{doc.original_uploaded_prescription}"
    )

    if doc.is_new():
        doc.insert(ignore_permissions=True)
        print(
            f">>> Smart Prescription CREATED: "
            f"{doc.name}"
        )
    else:
        doc.save(ignore_permissions=True)
        print(
            f">>> Smart Prescription UPDATED: "
            f"{doc.name}"
        )

    frappe.db.commit()

    print(
        f">>> Smart Prescription persisted successfully: "
        f"{doc.name}"
    )
    print(
        f">>> Current workflow state in DB: "
        f"{doc.workflow_state}"
    )

    print(">>> Enqueuing prescription OCR background job...")
    print(f">>> Queue: long")
    print(f">>> Prescription: {doc.name}")
    print(f">>> Appointment: {patient_appointment}")
    print(f">>> Attempt: 1")

    frappe.enqueue(
        "wellnest.services.prescription.processor.process_prescription_job",
        queue="long",
        timeout=1800,
        prescription=doc.name,
        file_url=file_url,
        attempt=1,
    )

    print(">>> PRESCRIPTION OCR JOB QUEUED SUCCESSFULLY")
    print(f">>> Prescription: {doc.name}")
    print(f">>> Queue: long")
    print(f">>> Attempt: 1")
    print(">>> PRESCRIPTION API END")
    print("=" * 80 + "\n")

    return {
        "status": "queued",
        "name": doc.name,
        "workflow_state": doc.workflow_state,
        "message": (
            "Prescription submitted. "
            "Processing has started in the background. "
            "You can continue with the consultation."
        ),
    }


@frappe.whitelist()
def save_ocr_prescription(name, response_data):
    doc = frappe.get_doc("Smart Prescription", name)

    data = frappe.parse_json(response_data)

    doc.advice = data.get("advice") or ""

    doc.set("medicines", [])

    for medicine in data.get("medicines") or []:
        item = doc.append("medicines", {})
        item.medicine_name = (
            medicine.get("medicine_name")
            or medicine.get("name")
            or ""
        )
        item.dosage = medicine.get("dosage") or ""
        item.timing = medicine.get("timing") or ""
        item.duration = medicine.get("duration") or ""
        item.instructions = medicine.get("instructions") or ""

    doc.workflow_state = "Complete"
    doc.save(ignore_permissions=True)

    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
        "medicines": [
            {
                "name": item.name,
                "medicine_name": item.medicine_name,
                "dosage": item.dosage,
                "timing": item.timing,
                "duration": item.duration,
                "instructions": item.instructions,
            }
            for item in doc.medicines
        ],
        "advice": doc.advice or "",
    }


@frappe.whitelist()
def create_consultation_prescription(
    appointment,
    followup_expiry_date=None,
    investigations=None,
    examination=None,
    provisional_diagnosis=None,
    follow_up_duration=None,
    follow_up_advice=None,
    diet_advice=None,
    exercise_advice=None,
    medicines=None,
):
    if not appointment:
        frappe.throw("Appointment is required.")

    appointment_doc = frappe.get_doc(
        "Patient Appointment",
        appointment,
    )

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found.")

    if appointment_doc.practitioner != practitioner:
        frappe.throw(
            "You are not authorized to create a prescription for this appointment.",
            frappe.PermissionError,
        )

    if appointment_doc.consultation_type != "Online":
        frappe.throw(
            "Prescription can only be created for an online consultation."
        )

    existing = frappe.db.exists(
        "Smart Prescription",
        {"patient_appointment": appointment},
    )

    if existing:
        frappe.throw(
            "A prescription already exists for this consultation."
        )

    medicines = frappe.parse_json(medicines or "[]")

    doc = frappe.new_doc("Smart Prescription")

    doc.patient_appointment = appointment
    doc.patient = appointment_doc.patient
    doc.practitioner = appointment_doc.practitioner
    doc.followup_expiry_date = followup_expiry_date
    doc.investigations = investigations or ""
    doc.examination = examination or ""
    doc.provisional_diagnosis = provisional_diagnosis or ""
    doc.follow_up_duration = follow_up_duration or ""
    doc.follow_up_advice = follow_up_advice or ""
    doc.diet_advice = diet_advice or ""
    doc.exercise_advice = exercise_advice or ""
    doc.workflow_state = "Draft"

    for medicine in medicines:
        if not medicine.get("medicine_name"):
            continue

        item = doc.append("medicines", {})

        item.medicine_name = medicine.get("medicine_name") or ""
        item.dosage = medicine.get("dosage") or ""
        item.timing = medicine.get("timing") or ""
        item.instructions = medicine.get("instructions") or ""

    doc.insert(
        ignore_permissions=True,
    )

    return {
        "name": doc.name,
        "patient_appointment": doc.patient_appointment,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
        "followup_expiry_date": doc.followup_expiry_date,
        "workflow_state": doc.workflow_state,
        "investigations": doc.investigations,
        "examination": doc.examination,
        "provisional_diagnosis": doc.provisional_diagnosis,
        "follow_up_duration": doc.follow_up_duration,
        "follow_up_advice": doc.follow_up_advice,
        "medicines": [
            {
                "name": item.name,
                "medicine_name": item.medicine_name,
                "dosage": item.dosage,
                "timing": item.timing,
                "instructions": item.instructions,
            }
            for item in doc.medicines
        ],
    }


@frappe.whitelist()
def save_consultation_prescription_draft(
    name=None,
    appointment=None,
    prescription_date=None,
    followup_expiry_date=None,
    investigations=None,
    follow_up_duration=None,
    follow_up_advice=None,
    examination=None,
    provisional_diagnosis=None,
    medicines=None,
):
    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found.")

    if not name:
        if not appointment:
            frappe.throw("Patient appointment is required.")

        print(
            f">>> Creating prescription draft for appointment: "
            f"{appointment}"
        )
        print(
            f">>> Logged-in practitioner: "
            f"{practitioner}"
        )

        appointment_doc = frappe.get_doc(
            "Patient Appointment",
            appointment,
        )

        print(
            f">>> Appointment practitioner: "
            f"{appointment_doc.practitioner}"
        )

        if appointment_doc.practitioner != practitioner:
            print(
                ">>> DRAFT CREATION AUTHORIZATION FAILED"
            )

            frappe.throw(
                "You are not authorized to create a prescription "
                "for this appointment.",
                frappe.PermissionError,
            )

        print(
            ">>> Draft creation authorization passed"
        )

        doc = frappe.new_doc("Smart Prescription")

        doc.patient_appointment = appointment
        doc.patient = appointment_doc.patient
        doc.practitioner = practitioner
        doc.workflow_state = "Draft"

        print(
            f">>> New Smart Prescription draft prepared "
            f"for patient: {appointment_doc.patient}"
        )

    else:
        doc = frappe.get_doc(
            "Smart Prescription",
            name,
        )

        if doc.practitioner != practitioner:
            frappe.throw(
                "You are not authorized to update this prescription.",
                frappe.PermissionError,
            )

        if doc.workflow_state != "Draft":
            frappe.throw(
                "Prescription can only be saved as draft while in Draft state."
            )

    medicines = frappe.parse_json(
        medicines or "[]"
    )

    doc.followup_expiry_date = followup_expiry_date

    doc.investigations = investigations or ""
    doc.examination = examination or ""
    doc.provisional_diagnosis = provisional_diagnosis or ""

    doc.follow_up_duration = follow_up_duration or ""
    doc.follow_up_advice = follow_up_advice or ""

    doc.set("medicines", [])

    for medicine in medicines:
        if not medicine.get("medicine_name"):
            continue

        item = doc.append(
            "medicines",
            {},
        )

        item.medicine_name = (
            medicine.get("medicine_name") or ""
        )
        item.dosage = (
            medicine.get("dosage") or ""
        )
        item.timing = (
            medicine.get("timing") or ""
        )
        item.instructions = (
            medicine.get("instructions") or ""
        )

    doc.save(ignore_permissions=True)

    print(
        f">>> Smart Prescription draft saved: "
        f"{doc.name}"
    )

    print(
        f">>> Workflow state: "
        f"{doc.workflow_state}"
    )

    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
        "investigations": doc.investigations,
        "examination": doc.examination,
        "provisional_diagnosis": doc.provisional_diagnosis,
        "follow_up_duration": doc.follow_up_duration,
        "follow_up_advice": doc.follow_up_advice,
        "medicines": [
            {
                "name": item.name,
                "medicine_name": item.medicine_name,
                "dosage": item.dosage,
                "timing": item.timing,
                "instructions": item.instructions,
            }
            for item in doc.medicines
        ],
    }


@frappe.whitelist()
def complete_consultation_prescription(name):
    if not name:
        frappe.throw("Prescription name is required.")

    doc = frappe.get_doc("Smart Prescription", name)

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found.")

    if doc.practitioner != practitioner:
        frappe.throw(
            "You are not authorized to complete this prescription.",
            frappe.PermissionError,
        )

    if doc.workflow_state == "Complete":
        return {
            "name": doc.name,
            "workflow_state": doc.workflow_state,
        }

    if doc.workflow_state != "Draft":
        frappe.throw(
            "Only a Draft prescription can be submitted."
        )

    doc.workflow_state = "Complete"

    doc.save(
        ignore_permissions=True,
    )

    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
    }


@frappe.whitelist()
def get_consultation_prescription(appointment):
    if not appointment:
        frappe.throw("Appointment is required.")

    appointment_doc = frappe.get_doc(
        "Patient Appointment",
        appointment,
    )

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"user_id": frappe.session.user},
        "name",
    )

    if not practitioner:
        frappe.throw("Practitioner not found.")

    if appointment_doc.practitioner != practitioner:
        frappe.throw(
            "You are not authorized to access this prescription."
        )

    prescription_name = frappe.db.get_value(
        "Smart Prescription",
        {"patient_appointment": appointment},
        "name",
    )

    if not prescription_name:
        return None

    doc = frappe.get_doc(
        "Smart Prescription",
        prescription_name,
    )

    file_url = doc.original_uploaded_prescription

    print(
        f">>> Prescription original uploaded file: "
        f"{file_url}"
    ) 

    return {
        "name": doc.name,
        "patient_appointment": doc.patient_appointment,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
        "followup_expiry_date": doc.followup_expiry_date,
        "workflow_state": doc.workflow_state,
        "investigations": doc.investigations,
        "examination": doc.examination,
        "provisional_diagnosis": doc.provisional_diagnosis,
        "follow_up_duration": doc.follow_up_duration,
        "follow_up_advice": doc.follow_up_advice,
        "file_url": file_url,
        "medicines": [
            {
                "name": item.name,
                "medicine_name": item.medicine_name,
                "dosage": item.dosage,
                "timing": item.timing,
                "instructions": item.instructions,
            }
            for item in doc.medicines
        ],
    }