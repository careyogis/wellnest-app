import frappe

from wellnest.services.prescription.processor import process_prescription


@frappe.whitelist()
def parse_and_create_prescription(
    patient,
    practitioner,
    file_url,
    teleconsult_appointment=None,
):
    if not patient:
        frappe.throw("Patient is required.")

    if not practitioner:
        frappe.throw("Practitioner is required.")

    if not file_url:
        frappe.throw("Prescription file is required.")

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
        frappe.throw(f"Unsupported file path: {file_url}")

    with open(file_path, "rb") as file:
        image_bytes = file.read()

    if not image_bytes:
        frappe.throw("Prescription file is empty.")

    doc_name = process_prescription(
        image_bytes,
        patient,
        practitioner,
        teleconsult_appointment,
    )

    return {"name": doc_name}

@frappe.whitelist()
def start_doctor_review(name):
    doc = frappe.get_doc("Smart Prescription", name)

    if doc.workflow_state != "Draft":
        frappe.throw(
            f"Prescription must be in Draft state to start doctor review."
        )

    doc.workflow_state = "Doctor Review"
    doc.save(ignore_permissions=True)

    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
    }


@frappe.whitelist()
def confirm_prescription(name):
    doc = frappe.get_doc("Smart Prescription", name)

    if doc.workflow_state != "Doctor Review":
        frappe.throw(
            "Prescription must be in Doctor Review state before confirmation."
        )

    doc.workflow_state = "Confirmed"
    doc.save(ignore_permissions=True)

    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
    }

@frappe.whitelist()
def create_consultation_prescription(
    appointment,
    prescription_date=None,
    followup_expiry_date=None,
    medicines=None,
    followup_advice=None,
    diet_advice=None,
    exercise_advice=None,
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
        {"teleconsult_appointment": appointment},
    )

    if existing:
        frappe.throw(
            "A prescription already exists for this consultation."
        )

    medicines = frappe.parse_json(medicines or "[]")

    doc = frappe.new_doc("Smart Prescription")

    doc.teleconsult_appointment = appointment
    doc.patient = appointment_doc.patient
    doc.practitioner = appointment_doc.practitioner
    doc.prescription_date = (
        prescription_date or frappe.utils.today()
    )
    doc.followup_expiry_date = followup_expiry_date
    doc.workflow_state = "Draft"
    doc.followup_advice = followup_advice
    doc.diet_advice = diet_advice
    doc.exercise_advice = exercise_advice

    for medicine in medicines:
        for field in (
            "medicine_name",
            "dosage",
            "timing",
            "duration",
        ):
            if not medicine.get(field):
                frappe.throw(
                    f"{field.replace('_', ' ').title()} is required."
                )

        item = doc.append("medicines", {})

        item.medicine_name = medicine["medicine_name"]
        item.dosage = medicine["dosage"]
        item.timing = medicine["timing"]
        item.duration = medicine["duration"]
        item.instructions = medicine.get("instructions")

    doc.insert(
    ignore_permissions=True,
)

    return {
        "name": doc.name,
        "teleconsult_appointment": doc.teleconsult_appointment,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
        "prescription_date": doc.prescription_date,
        "followup_expiry_date": doc.followup_expiry_date,
        "workflow_state": doc.workflow_state,
        "followup_advice": doc.followup_advice,
        "diet_advice": doc.diet_advice,
        "exercise_advice": doc.exercise_advice,
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
    }

@frappe.whitelist()
def save_consultation_prescription_draft(
    name,
    prescription_date=None,
    followup_expiry_date=None,
    medicines=None,
    follow_up_advice=None,
    diet_advice=None,
    exercise_advice=None,
):
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
            "You are not authorized to update this prescription.",
            frappe.PermissionError,
        )

    if doc.workflow_state != "Draft":
        frappe.throw(
            "Prescription can only be saved as draft while in Draft state."
        )

    medicines = frappe.parse_json(medicines or "[]")

    doc.prescription_date = (
        prescription_date or frappe.utils.today()
    )
    doc.followup_expiry_date = followup_expiry_date
    doc.follow_up_advice = follow_up_advice
    doc.diet_advice = diet_advice
    doc.exercise_advice = exercise_advice

    doc.set("medicines", [])

    for medicine in medicines:
        for field in (
            "medicine_name",
            "dosage",
            "timing",
            "duration",
        ):
            if not medicine.get(field):
                frappe.throw(
                    f"{field.replace('_', ' ').title()} is required."
                )

        item = doc.append("medicines", {})
        item.medicine_name = medicine["medicine_name"]
        item.dosage = medicine["dosage"]
        item.timing = medicine["timing"]
        item.duration = medicine["duration"]
        item.instructions = medicine.get("instructions")

    doc.save(
        ignore_permissions=True,
    )

    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
        "follow_up_advice": doc.follow_up_advice,
        "diet_advice": doc.diet_advice,
        "exercise_advice": doc.exercise_advice,
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

    if doc.workflow_state == "Confirmed":
         return {
            "name": doc.name,
            "workflow_state": doc.workflow_state,
        }

    if doc.workflow_state != "Draft":
        frappe.throw(
            "Only a Draft prescription can be submitted."
        )

    doc.workflow_state = "Confirmed"

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
        {"teleconsult_appointment": appointment},
        "name",
    )

    if not prescription_name:
        return None

    doc = frappe.get_doc(
        "Smart Prescription",
        prescription_name,
    )

    return {
        "name": doc.name,
        "teleconsult_appointment": doc.teleconsult_appointment,
        "patient": doc.patient,
        "practitioner": doc.practitioner,
        "prescription_date": doc.prescription_date,
        "followup_expiry_date": doc.followup_expiry_date,
        "workflow_state": doc.workflow_state,
        "follow_up_advice": doc.follow_up_advice,
        "diet_advice": doc.diet_advice,
        "exercise_advice": doc.exercise_advice,
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
    }


