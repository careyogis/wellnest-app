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
        limit_page_length=5
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
            "status"
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
        limit_page_length=5
    )

    # -----------------------------------
    # Geriatric Reviews
    # -----------------------------------

    reviews = frappe.get_all(
        "Geriatric Review",
        filters={"patient": patient},
        fields=[
            "review_date",
            "summary"
        ],
        order_by="review_date desc",
        limit_page_length=5
    )

    return {
        "vitals": vitals,
        "medical_history": medical_history,
        "risk_flags": risk_flags,
        "nurse_visits": nurse_visits,
        "reviews": reviews
    }