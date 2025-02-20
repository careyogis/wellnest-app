# Copyright (c) 2024, www.thewellnest.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CYLead(Document):
	pass


import frappe
import json
from frappe.model.document import Document
from frappe.utils import now_datetime

@frappe.whitelist()
def get_caregivers(city, service_pincode, language_preferences, service_types):
    """
    Fetch available caregivers based on city, pincode, language, and service type.
    
    :param city: City name (string)
    :param service_pincode: Pincode (string or integer)
    :param language_preferences: JSON list of preferred languages
    :param service_types: JSON list of required services
    :return: List of matching caregivers
    """
    try:
        # Ensure JSON strings are converted to lists
        if isinstance(language_preferences, str):
            language_preferences = json.loads(language_preferences)
        if isinstance(service_types, str):
            service_types = json.loads(service_types)

        # Fetch City ID from City doctype
        city_doc = frappe.db.get_value('City', {'city_name': city}, 'name')
        if not city_doc:
            return []

        # Validate pincode as integer
        try:
            service_pincode = int(service_pincode)
        except ValueError:
            return []

        # Fetch caregivers matching city and pincode
        caregivers = frappe.get_all(
            'Caregiver',
            filters={'city': city_doc, 'pin_code': service_pincode},
            fields=['name', 'full_name', 'city', 'pin_code']
        )

        matching_caregivers = []

        for caregiver in caregivers:
            # Fetch caregiver's spoken languages
            languages_spoken = frappe.db.sql("""
                SELECT spoken_language_option FROM `tabSpoken Language Option`
                WHERE parent = %s
            """, (caregiver['name'],), as_dict=True)
            caregiver_languages = [lang['spoken_language_option'] for lang in languages_spoken]

            # Fetch caregiver's proficient activities
            service_activities = frappe.db.sql("""
                SELECT ia.description 
                FROM `tabCaregiver Proficient Activity` cpa
                JOIN `tabItem Activity` ia ON cpa.activity = ia.name
                WHERE cpa.parent = %s
            """, (caregiver['name'],), as_dict=True)
            caregiver_services = [service['description'] for service in service_activities]

            # Filter caregivers based on language and service type
            if not set(language_preferences).intersection(set(caregiver_languages)):
                continue
            if not set(service_types).intersection(set(caregiver_services)):
                continue

            # Check caregiver availability based on latest engagement
            engagement = frappe.db.sql("""
                SELECT e.end_date FROM `tabEngagement` e
                JOIN `tabEngagement Caregiver` ec ON e.name = ec.parent
                WHERE ec.caregiver = %s
                ORDER BY e.end_date DESC LIMIT 1
            """, (caregiver['name'],), as_dict=True)

            caregiver['availability'] = 'Available' if (not engagement or engagement[0]['end_date']) else 'Engaged'

            if caregiver['availability'] == 'Available':
                caregiver['languages'] = ", ".join(caregiver_languages)
                caregiver['service_types'] = ", ".join(caregiver_services)
                matching_caregivers.append(caregiver)

        return matching_caregivers
    except Exception as e:
        frappe.log_error(f"Error fetching caregivers: {str(e)}")
        return []


@frappe.whitelist()
def create_caregiver_responses(lead_name, caregivers):
    """
    Create caregiver response records for a given lead.
    
    :param lead_name: CY Lead name (string)
    :param caregivers: JSON list of caregiver names
    :return: Success or error message
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
    Record caregiver broadcast activity for a given lead.
    
    :param lead_name: CY Lead name (string)
    :param caregivers: JSON list of caregiver full names
    :return: Success or error message
    """
    try:
        caregivers_list = json.loads(caregivers) if isinstance(caregivers, str) else caregivers
        if not isinstance(caregivers_list, list) or not caregivers_list:
            return {"error": "Invalid caregivers list"}

        for caregiver_full_name in caregivers_list:
            caregiver_id = frappe.get_value("Caregiver", {"full_name": caregiver_full_name}, "name")
            if not caregiver_id:
                continue

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
    Fetch all caregiver responses with their statuses.
    
    :return: List of caregiver responses
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















