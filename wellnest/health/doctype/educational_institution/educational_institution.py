# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EducationalInstitution(Document):
	pass


@frappe.whitelist()
def create_institution(institution_name):
    institution_name = (institution_name or "").strip()

    if not institution_name:
        frappe.throw("Institution Name is required")

    existing = frappe.db.get_value(
        "Educational Institution",
        {"institution_name": institution_name},
        "name",
    )

    if existing:
        institution = frappe.get_doc("Educational Institution", existing)
    else:
        institution = frappe.get_doc({
            "doctype": "Educational Institution",
            "institution_name": institution_name,
        })

        institution.insert()

    return {
        "name": institution.name,
        "institution_name": institution.institution_name,
    }