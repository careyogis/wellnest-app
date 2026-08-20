# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Hospital(Document):
	pass

@frappe.whitelist()
def create_hospital(hospital_name):
    hospital_name = (hospital_name or "").strip()

    if not hospital_name:
        frappe.throw("Hospital Name is required")

    count = frappe.db.count("Hospital") + 1
    hospital_code = f"HS-{count:06d}"

    while frappe.db.exists("Hospital", {"hospital_code": hospital_code}):
        count += 1
        hospital_code = f"HS-{count:06d}"

    hospital = frappe.get_doc({
        "doctype": "Hospital",
        "hospital_code": hospital_code,
        "hospital_name": hospital_name,
        "is_active": 1,
    })

    hospital.insert()

    return {
        "name": hospital.name,
        "hospital_code": hospital.hospital_code,
        "hospital_name": hospital.hospital_name,
    }
