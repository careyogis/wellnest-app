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
def get_matching_caregivers(city, requirement, language_preferences, service_types = None):
    # Fetch available caregivers based on:
    # - City
    # - Language preferences
    # - Service types required
    # - Caregiver is available (no ongoing engagement).

    # NOTE:
    # - 13-05-25: Changing temp implementation to use requirement field instead of service_types
    # - The first element in service_types should be the primary Service required - e.g Attendant, Nurse, Child Care etc..

    try:
        if isinstance(language_preferences, str):
            language_preferences = json.loads(language_preferences)

        if isinstance(service_types, str):
            service_types = json.loads(service_types)

        if len(language_preferences) == 0:
            language_preferences = [""]     # no preference

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

        match requirement:
            case "Attendant at Home":
                query_string += """ AND c.caregiver_type LIKE 'Attendant%' """
            case "Nursing Care" | "ICU at Home":
                query_string += """ AND c.caregiver_type LIKE '%Nurse%' """
            case "Physiotherapy":
                query_string += """ AND c.caregiver_type = 'Physiotherapist' """
            case "Speech Therapy":
                query_string += """ AND c.caregiver_type = 'Speech Therapist' """
            case "Baby Care":
                query_string += """ AND c.caregiver_type LIKE '%Child Care%' """

        caregivers = frappe.db.sql(query_string.format(language_preferences[0], city), as_dict=True)
 
        return caregivers

    except Exception as e:
        frappe.log_error("Error fetching caregivers", str(e))
        return []



@frappe.whitelist()
def broadcast_lead(lead_name, phone_numbers, caregiver_ids):
    # Generate WhatsApp message data to be broadcasted
    try:
        if isinstance(phone_numbers, str):
            phone_numbers = json.loads(phone_numbers)
        if isinstance(caregiver_ids, str):
            caregiver_ids = json.loads(caregiver_ids)
        
        lead = frappe.get_doc("CY Lead", lead_name)

        requirement = lead.get("requirement")
        medical_conditions = [d.medical_conditon_option for d in lead.get("medical_condition") if d.medical_conditon_option]
        patient_condition = ", ".join(medical_conditions) if medical_conditions else "Not specified"
        responsibilities = [d.activity for d in lead.get("service_details") if d.activity]
        responsibilities_str = ", ".join(responsibilities) if responsibilities else "Not specified"
        base_url = frappe.utils.get_url()

        response_form_links = []
        for i in range(len(phone_numbers)):
            caregiverId = caregiver_ids[i]

            caregiver_response = frappe.db.get_value(
                "Caregiver Response",
                {"caregiver_name": caregiverId, "cy_lead": lead.name},
                "name"
            )

            if not caregiver_response:
                frappe.log_error(f"No Caregiver Response found for {caregiverId} and lead {lead.name}", "Broadcast Lead")
                continue

            response_url = f"{base_url}/caregiver-interest?response_id={caregiver_response}"
            response_form_links.append(response_url)
            
        if len(response_form_links) == 0:
            return {"error": "Couldn't broadcast message to any caregivers."}
        
        data = {
            "requirement": requirement,
            "location": lead.city,
            "condition": patient_condition,
            "responsibility": responsibilities_str,
            "phoneNumbers": phone_numbers,
            "responseUrls": response_form_links,
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
