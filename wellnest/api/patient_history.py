import frappe


@frappe.whitelist()
def get_patient_history(patient_appointment):
    """Return the patient's historical Smart Prescriptions and Health Vault
    records for the given appointment, latest first.
    """

    if not patient_appointment:
        frappe.throw("Patient appointment is required.")

    appointment_doc = frappe.get_doc(
        "Patient Appointment",
        patient_appointment,
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
            "You are not authorized to access this patient's history.",
            frappe.PermissionError,
        )

    patient = appointment_doc.patient

    if not patient:
        return {
            "patient": None,
            "smart_prescriptions": [],
            "health_vault": [],
        }

    # Previous Smart Prescriptions
    prescriptions = frappe.get_all(
        "Smart Prescription",
        filters={
            "patient": patient,
            "patient_appointment": ["!=", patient_appointment],
        },
        fields=[
            "name",
            "patient_appointment",
            "practitioner",
            "prescription_date",
            "workflow_state",
            "creation",
        ],
        order_by="creation desc",
    )

    practitioner_ids = {
        row.practitioner
        for row in prescriptions
        if row.practitioner
    }

    practitioner_names = {}

    if practitioner_ids:
        for row in frappe.get_all(
            "Practitioner",
            filters={
                "name": ["in", list(practitioner_ids)],
            },
            fields=[
                "name",
                "full_name",
            ],
        ):
            practitioner_names[row.name] = row.full_name

    smart_prescriptions = [
        {
            "name": row.name,
            "patient_appointment": row.patient_appointment,
            "practitioner": row.practitioner,
            "practitioner_name": practitioner_names.get(
                row.practitioner
            ),
            "prescription_date": row.prescription_date,
            "workflow_state": row.workflow_state,
            "creation": row.creation,
        }
        for row in prescriptions
    ]


    health_vault_records = frappe.get_all(
        "Health Vault",
        filters={"patient": patient},
        fields=[
            "name",
            "document_type",
            "document",
            "batch_number",
            "creation",
        ],
        order_by="creation desc",
    )

    health_vault = []

    for record in health_vault_records:
        health_vault.append({
            "name": record.name,
            "document_type": record.document_type,
            "document": record.document,
            "document_url": frappe.utils.get_url(record.document) if record.document else None,
            "batch_number": record.batch_number,
            "creation": record.creation,
        })

    return {
        "patient": patient,
        "smart_prescriptions": smart_prescriptions,
        "health_vault": health_vault,
    }


@frappe.whitelist()
def get_historical_prescription(
    patient_appointment,
    prescription_name,
):
    """Return one historical Smart Prescription in read-only form."""

    if not patient_appointment:
        frappe.throw("Patient appointment is required.")

    if not prescription_name:
        frappe.throw("Prescription name is required.")

    appointment_doc = frappe.get_doc(
        "Patient Appointment",
        patient_appointment,
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
            "You are not authorized to access this patient's history.",
            frappe.PermissionError,
        )

    patient = appointment_doc.patient

    if not patient:
        frappe.throw("Patient not found.")

    prescription = frappe.get_doc(
        "Smart Prescription",
        prescription_name,
    )

    if prescription.patient != patient:
        frappe.throw(
            "You are not authorized to access this prescription.",
            frappe.PermissionError,
        )

    practitioner_name = None

    if prescription.practitioner:
        practitioner_name = frappe.db.get_value(
            "Practitioner",
            prescription.practitioner,
            "full_name",
        )

    # Return read-only prescription data
    return {
        "name": prescription.name,
        "patient": prescription.patient,
        "patient_appointment": prescription.patient_appointment,
        "practitioner": prescription.practitioner,
        "practitioner_name": practitioner_name,
        "prescription_date": prescription.prescription_date,
        "workflow_state": prescription.workflow_state,
        "original_uploaded_prescription": prescription.original_uploaded_prescription,
        "diagnosis": prescription.diagnosis,
        "investigations": prescription.investigations,
        "general_instructions": prescription.general_instructions,
        "examination": prescription.examination,
        "provisional_diagnosis": prescription.provisional_diagnosis,
        "follow_up_duration": prescription.follow_up_duration,
        "follow_up_advice": prescription.follow_up_advice,
        "medicines": [
            {
                "name": item.name,
                "medicine_name": item.medicine_name,
                "dosage": item.dosage,
                "timing": item.timing,
                "instructions": item.instructions,
            }
            for item in prescription.medicines
        ],
    }