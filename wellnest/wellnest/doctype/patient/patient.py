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

    normal_ranges = {
        "BP": "120 systolic",
        "SPO2": "95 - 100 %",
        "Heart Rate": "60 - 100 bpm",
        "Temperature": "97 - 99 °F",
        "Sugar": "80 - 140 mg/dL",
        "Weight": "60 - 75 kg",
        "Respiratory Rate": "12 - 20 breaths/min"
    }

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

    latest_value = None

    for v in vitals:

        doc = frappe.get_doc("Vitals", v.name)

        for row in doc.vital_reading:

            if row.vital_type == vital_type:

                change = "Initial Reading"

                current_value = str(row.value)

                latest_value = current_value

                # -----------------------------------
                # Chart Numeric Value
                # -----------------------------------

                chart_value = 0

                try:

                    if vital_type == "BP":

                        chart_value = float(current_value.split('/')[0])

                    else:

                        chart_value = float(current_value)

                except:

                    chart_value = 0

                # -----------------------------------
                # Change Logic
                # -----------------------------------

                if previous_value:

                    try:

                        if vital_type == "BP":

                            current_num = float(current_value.split('/')[0])
                            previous_num = float(previous_value.split('/')[0])

                        else:

                            current_num = float(current_value)
                            previous_num = float(previous_value)

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
                    "date": str(v.recorded_on),
                    "value": current_value,
                    "chart_value": chart_value,
                    "unit": row.unit,
                    "change": change
                })

                previous_value = current_value

    # -----------------------------------
    # Observation Logic
    # -----------------------------------

    observation = "No significant observation."

    try:

        if vital_type == "Weight":

            latest_num = float(latest_value)

            if latest_num > 75:

                observation = "Weight is above the normal range."

            elif latest_num < 60:

                observation = "Weight is below the normal range."

            else:

                observation = "Weight is within the normal range."

        elif vital_type == "SPO2":

            latest_num = float(latest_value)

            if latest_num < 95:

                observation = "SPO2 is below normal range."

            else:

                observation = "SPO2 is within normal range."

        elif vital_type == "Heart Rate":

            latest_num = float(latest_value)

            if latest_num > 100:

                observation = "Heart rate is elevated."

            elif latest_num < 60:

                observation = "Heart rate is lower than expected."

            else:

                observation = "Heart rate is normal."

        elif vital_type == "Temperature":

            latest_num = float(latest_value)

            if latest_num > 99:

                observation = "Temperature is above normal range."

            elif latest_num < 97:

                observation = "Temperature is below normal range."

            else:

                observation = "Temperature is normal."

        elif vital_type == "Sugar":

            latest_num = float(latest_value)

            if latest_num > 140:

                observation = "Sugar level is above normal range."

            elif latest_num < 80:

                observation = "Sugar level is below normal range."

            else:

                observation = "Sugar level is normal."

        elif vital_type == "Respiratory Rate":

            latest_num = float(latest_value)

            if latest_num > 20:

                observation = "Respiratory rate is elevated."

            elif latest_num < 12:

                observation = "Respiratory rate is below normal range."

            else:

                observation = "Respiratory rate is normal."

        elif vital_type == "BP":

            latest_num = float(latest_value.split('/')[0])

            if latest_num > 120:

                observation = "Blood pressure is above normal range."

            elif latest_num < 90:

                observation = "Blood pressure is below normal range."

            else:

                observation = "Blood pressure is within normal range."

    except:
        pass

    return {
        "trend_data": trend_data,
        "normal_range": normal_ranges.get(vital_type, "-"),
        "observation": observation
    }