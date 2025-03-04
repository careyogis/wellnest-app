# Copyright (c) 2024, www.thewellnest.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CYLead(Document):
	pass


import frappe
import json
from frappe.utils import now_datetime


@frappe.whitelist()
def get_caregivers(lead_name, city, language_preferences):
    """
    Fetch available caregivers based on:
    - City
    - Language preferences
    - Service types required (from CY Lead's linked Blanket Order Items)

    Matching Criteria:
    - Caregiver city matches lead's city.
    - Caregiver speaks at least one preferred language.
    - Caregiver type matches the required services.
    - Caregiver is available (no ongoing engagement).
    """
    try:
        if isinstance(language_preferences, str):
            language_preferences = json.loads(language_preferences)

        # Fetch required service types from Blanket Order Items linked to the lead
        services_required = frappe.db.sql("""
            SELECT sri.item_code, i.item_name
            FROM `tabBlanket Order Item` sri
            JOIN `tabItem` i ON sri.item_code = i.name
            WHERE sri.parent = %s
        """, (lead_name,), as_dict=True)

        service_types = [service['item_name'] for service in services_required]

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
                if service == "GDA" and caregiver_type and caregiver_type.startswith('Attendant'):
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


@frappe.whitelist()
def generate_whatsapp_message(lead_name):
    """
    Generate a WhatsApp message template for a lead, including:
    - Requirement details
    - Location
    - Patient condition
    - Responsibilities
    - A link to the response form
    """
    try:
        lead = frappe.get_doc("CY Lead", lead_name)

        medical_conditions = [d.medical_condition for d in lead.get("medical_condition") if d.medical_condition]
        patient_condition = ", ".join(medical_conditions) if medical_conditions else "Not specified"

        responsibilities = [d.activity for d in lead.get("service_details") if d.activity]
        responsibilities_str = ", ".join(responsibilities) if responsibilities else "Not specified"

        base_url = frappe.utils.get_url()
        response_form_link = f"{base_url}/caregiver-response-form?lead={lead.name}"

        whatsapp_message = f"""
Greetings from CareYogi™  
🔔 *New Service Alert - Immediate Requirement*  

📌 *Requirement:* {lead.requirement}  
📍 *Location:* {lead.service_area}  
🩺 *Patient Condition:* {patient_condition}  
📝 *Responsibilities:* {responsibilities_str}  

✅ If you're interested, [Click Here]({response_form_link}) to confirm your availability.
"""

        return whatsapp_message.strip()

    except Exception as e:
        frappe.log_error(f"Error generating WhatsApp message: {str(e)}")
        return {"error": str(e)}
















