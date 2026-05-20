# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Patient(Document):
    pass


@frappe.whitelist()
def get_patient_timeline(patient):

    # -----------------------------------
    # Vitals
    # -----------------------------------

    vitals_docs = frappe.get_all(
        "Vitals",
        filters={"patient": patient},
        fields=[
            "name",
            "recorded_on",
            "recorded_by"
        ],
        order_by="recorded_on desc",
        limit_page_length=10
    )

    vitals = []

    for vital in vitals_docs:

        vital_doc = frappe.get_doc("Vitals", vital.name)

        vitals.append({
            "recorded_on": vital_doc.recorded_on,
            "recorded_by": vital_doc.recorded_by,
            "vital_reading": vital_doc.vital_reading
        })
    

    # -----------------------------------
    # Medical History
    # -----------------------------------

    medical_history = frappe.get_all(
        "Medical History",
        filters={"patient": patient},
        fields=[
            "condition_name",
            "icd_10_code",
            "onset_date",
            "status",
            "chronic",
            "notes",
            "allergies"
        ]
    )

    # -----------------------------------
    # Risk Flags
    # -----------------------------------

    risk_flags = frappe.get_all(
        "Risk Flag",
        filters={"patient": patient},
        fields=[
            "flag_type",
            "severity",
            "status",
            "description",
            "created_at",
            "resolved_at"
        ]
    )

    # -----------------------------------
    # Nurse Visits
    # -----------------------------------

    nurse_visits = frappe.get_all(
        "Nurse Visit",
        filters={"patient": patient},
        fields=[
            "visit_date",
            "nurse_id",
            "concerns",
            "vitals_summary",
            "mobility_observation",
            "next_actions"
        ],
        order_by="visit_date desc",
        limit_page_length=10
    )

    # -----------------------------------
    # Geriatric Reviews
    # -----------------------------------

    reviews = frappe.get_all(
        "Geriatric Review",
        filters={"patient": patient},
        fields=[
            "review_date",
            "reviewer_hpr",
            "summary",
            "recommendations",
            "risk_flags"
        ],
        order_by="review_date desc",
        limit_page_length=10
    )

    # -----------------------------------
    # Medications
    # -----------------------------------

    medication_docs = frappe.get_all(
        "Medication",
        filters={"patient": patient},
        fields=[
            "name",
            "prescribed_by",
            "adherence_status",
            "notes",
            "creation"
        ],
        order_by="creation desc",
        limit_page_length=10
    )

    medications = []

    for med in medication_docs:

        med_doc = frappe.get_doc("Medication", med.name)

        medications.append({
            "prescribed_by": med_doc.prescribed_by,
            "adherence_status": med_doc.adherence_status,
            "notes": med_doc.notes,
            "creation": med_doc.creation,
            "medication_items": med_doc.medication_items
        })

    # -----------------------------------
    # Medical Documents
    # -----------------------------------

    medical_documents = frappe.get_all(
        "Medical Document",
        filters={"patient": patient},
        fields=[
            "document_type",
            "loinc_code",
            "file",
            "uploader"
        ],
        limit_page_length=10
    )



    return {
        "vitals": vitals,
        "medical_history": medical_history,
        "risk_flags": risk_flags,
        "nurse_visits": nurse_visits,
        "reviews": reviews,
        "medications": medications,
        "medical_documents": medical_documents
    }

# =========================================
# Vital Trend API
# =========================================

@frappe.whitelist()
def get_vital_trend(patient, vital_type):

    vitals = frappe.get_all(
        "Vitals",
        filters={"patient": patient},
        fields=[
            "name",
            "recorded_on"
        ],
        order_by="recorded_on asc"
    )

    trend_data = []

    previous_value = None

    for v in vitals:

        doc = frappe.get_doc("Vitals", v.name)

        for row in doc.vital_reading:

            if row.vital_type == vital_type:

                change = "Initial Reading"

                current_value = str(row.value)

                if previous_value:

                    try:

                        current_num = float(current_value.split('/')[0])
                        previous_num = float(previous_value.split('/')[0])

                        if current_num > previous_num:
                            change = f"Increased from {previous_value} to {current_value}"

                        elif current_num < previous_num:
                            change = f"Decreased from {previous_value} to {current_value}"

                        else:
                            change = "No Change"

                    except:

                        if current_value != previous_value:
                            change = f"Changed from {previous_value} to {current_value}"

                        else:
                            change = "No Change"

                trend_data.append({
                    "date": v.recorded_on,
                    "value": current_value,
                    "unit": row.unit,
                    "change": change
                })

                previous_value = current_value

    return trend_data