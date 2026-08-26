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
