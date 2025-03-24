# Copyright (c) 2024, www.thewellnest.in and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import now_datetime
from wellnest.whatsapp_brodcast import broadcast_message

class CYLead(Document):
	pass

@frappe.whitelist()
def get_caregivers(lead_name, city, language_preferences, service_types):
    """
    Fetch available caregivers based on:
    - City
    - Language preferences
    - Service types required (from CY Lead's linked Blanket Order Items)

    Matching Criteria:
    - Caregiver city matches lead's city.
    - Caregiver speaks at least one preferred language, if supplied.
    - Caregiver type matches the required services.
    - Caregiver is available (no ongoing engagement).
    """
    try:
        if isinstance(language_preferences, str):
            language_preferences = json.loads(language_preferences)

        if isinstance(service_types, str):
            service_types = json.loads(service_types)

        city_doc = frappe.db.get_value('City', {'city_name': city}, 'name')
        if not city_doc:
            return []

        caregivers = frappe.get_all(
            'Caregiver',
            filters={'city': city_doc},
            fields=['name', 'full_name', 'city', 'pin_code', 'caregiver_type']
        )

        matching_caregivers = []

        for caregiver in caregivers:
            # Fetch caregiver languages
            languages_spoken = frappe.db.sql("""
                SELECT spoken_language_option FROM `tabSpoken Language Option`
                WHERE parent = %s
            """, (caregiver['name'],), as_dict=True)
            caregiver_languages = [lang['spoken_language_option'] for lang in languages_spoken]

            caregiver_type = caregiver.get('caregiver_type')

            # Match caregiver type with required services
            matched_service = False
            for service in service_types:
                if service == "General Duty Attendant" and caregiver_type and caregiver_type.startswith('Attendant'):
                    matched_service = True
                    break
                if service == "Nursing" and caregiver_type and 'Nurse' in caregiver_type:
                    matched_service = True
                    break
                if service == "Child Care" and caregiver_type and 'Child Care' in caregiver_type:
                    matched_service = True
                    break
                if service == "Physiotherapy" and caregiver_type == 'Physiotherapist':
                    matched_service = True
                    break
                if service == "Speech Therapy" and caregiver_type == 'Speech Therapist':
                    matched_service = True
                    break

            if not matched_service:
                continue

            # Match at least one common language
            if not set(language_preferences).intersection(set(caregiver_languages)):
                continue

            # Check caregiver's availability
            today_date = frappe.utils.getdate(frappe.utils.today())
            engagements = frappe.db.sql("""
                SELECT start_date, end_date 
                FROM `tabEngagement Caregiver`
                WHERE caregiver = %s
            """, (caregiver['name'],), as_dict=True)

            caregiver['availability'] = 'Available'
            for engagement in engagements:
                if engagement.get('start_date') and engagement.get('end_date'):
                    if frappe.utils.getdate(engagement['start_date']) <= today_date <= frappe.utils.getdate(engagement['end_date']):
                        caregiver['availability'] = 'Engaged'
                        break

            if caregiver['availability'] == 'Available':
                caregiver['languages'] = ", ".join(caregiver_languages)
                caregiver['service_types'] = ", ".join(service_types)
                matching_caregivers.append(caregiver)

        return matching_caregivers

    except Exception as e:
        frappe.log_error("Error fetching caregivers", str(e))
        return []

@frappe.whitelist()
def get_matching_caregivers(city, service_types, language_preferences):
    # Fetch available caregivers based on:
    # - City
    # - Language preferences
    # - Service types required
    # - Caregiver is available (no ongoing engagement).

    # NOTE:
    # - The first element in service_types should be the primary Service required - e.g Attendant, Nurse, Child Care etc..

    try:
        if isinstance(language_preferences, str):
            language_preferences = json.loads(language_preferences)

        if isinstance(service_types, str):
            service_types = json.loads(service_types)

        query_string = """
            SELECT 
                c.name, c.full_name, c.city, c.pin_code, c.caregiver_type, c.phone_number,
                IF(engmnt.end_date IS NULL, 'Available', 'Engaged') as availability,
                COALESCE(l.spoken_language_option, 'Not Matching') as languages
            FROM 
                `tabCaregiver` c 
            LEFT JOIN
                (SELECT caregiver, end_date FROM `tabEngagement Caregiver` WHERE end_date >= CURDATE()) engmnt
            ON
                c.name = engmnt.caregiver
            LEFT JOIN `tabSpoken Language Option` l 
            ON 
                c.name = l.parent AND l.spoken_language_option = '{}'
            WHERE c.city LIKE '{}%' 
            """

        match service_types[0]:
            case "General Duty Attendant":
                query_string += """ AND c.caregiver_type LIKE 'Attendant%' """
            case "Nursing Care at Home":
                query_string += """ AND c.caregiver_type LIKE '%Nurse%' """
            case "Baby Care":
                query_string += """ AND c.caregiver_type LIKE '%Child Care%' """
            case "Physiotherapy at Home":
                query_string += """ AND c.caregiver_type = 'Physiotherapist' """
            case "SPEECH":
                query_string += """ AND c.caregiver_type = 'Speech Therapist' """
        
        caregivers = frappe.db.sql(query_string.format(language_preferences[0], city), as_dict=True)
 
        return caregivers

    except Exception as e:
        frappe.log_error("Error fetching caregivers", str(e))
        return []

@frappe.whitelist()
def broadcast_lead(lead_name, phone_numbers):
    # Generate WhatsApp message data to be broadcasted
    try:
        lead = frappe.get_doc("CY Lead", lead_name)

        requirement = lead.get("services_required")[0].item_name
        medical_conditions = [d.medical_conditon_option for d in lead.get("medical_condition") if d.medical_conditon_option]
        patient_condition = ", ".join(medical_conditions) if medical_conditions else "Not specified"
        responsibilities = [d.activity for d in lead.get("service_details") if d.activity]
        responsibilities_str = ", ".join(responsibilities) if responsibilities else "Not specified"
        base_url = frappe.utils.get_url()
        # response_form_link = f"{base_url}/caregiver-response-form?lead={lead.name}"
        response_form_link = f"https://127.0.0.1:8000/caregiver-response-form?lead={lead.name}"
        
        data = {
            "requirement": requirement,
            "location": lead.city,
            "condition": patient_condition,
            "responsibility": responsibilities_str,
            "phoneNumbers": phone_numbers,
            "responseUrl": response_form_link
        }

        result = broadcast_message(data)
        return result
    except Exception as e:
        frappe.log_error(f"Error generating WhatsApp message: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def record_caregiver_broadcast(lead_name, caregivers):
    """
    Create 'Caregiver Response' records to track broadcasted caregivers.
    """
    try:
        caregivers_list = json.loads(caregivers) if isinstance(caregivers, str) else caregivers
        if not isinstance(caregivers_list, list) or not caregivers_list:
            return {"error": "Invalid caregivers list"}

        for caregiver_full_name in caregivers_list:
            caregiver_id = frappe.get_value("Caregiver", {"full_name": caregiver_full_name}, "name")
            if not caregiver_id:
                continue

            # Avoid duplicate response records
            existing_entry = frappe.get_all(
                "Caregiver Response",
                filters={"cy_lead": lead_name, "caregiver_name": caregiver_id},
                fields=["name"]
            )

            if not existing_entry:
                new_entry = frappe.get_doc({
                    "doctype": "Caregiver Response",
                    "cy_lead": lead_name,
                    "caregiver_name": caregiver_id,
                    "status": "Pending",
                    "broadcast_time": now_datetime()
                })
                new_entry.insert(ignore_permissions=True)
                frappe.db.commit()

        return {"message": "success"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "record_caregiver_broadcast Error")
        return {"error": str(e)}

@frappe.whitelist()
def create_caregiver_responses(lead_name, caregivers):
    """
    Create 'Lead Query Response' records for each selected caregiver.
    """
    try:
        caregivers = frappe.parse_json(caregivers)
        for caregiver_name in caregivers:
            doc = frappe.get_doc({
                "doctype": "Lead Query Response",
                "lead": lead_name,
                "caregiver_name": caregiver_name,
                "status": "Pending"
            })
            doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "message": "Caregiver responses recorded."}
    except Exception as e:
        frappe.log_error(f"Error creating caregiver responses: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_caregiver_responses():
    """
    Fetch all caregiver responses with caregiver full names and response statuses.
    """
    try:
        responses = frappe.get_all(
            "Caregiver Response",
            fields=["caregiver_name", "status", "response_time"]
        )

        for response in responses:
            caregiver_full_name = frappe.db.get_value("Caregiver", response["caregiver_name"], "full_name")
            response["caregiver_name"] = caregiver_full_name or "Unknown"

        return responses
    except Exception as e:
        frappe.log_error(f"Error in get_caregiver_responses: {str(e)}")
        return []
