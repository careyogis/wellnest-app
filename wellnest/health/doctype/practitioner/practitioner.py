# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from collections.abc import Iterable
from frappe.utils.data import comma_and


class Practitioner(WebsiteGenerator):
	def before_save(self):		
		self.full_name = f"{self.title} {self.first_name} {self.last_name}";

	def validate(self):
		super().validate()
		self.validate_availability_days();

	def validate_availability_days(self):
		availability_days = self.get_availability_days()
		if len(set(availability_days)) != len(availability_days):
			frappe.throw(
				("The following Availability Days have been repeated: {0}. Remove duplicates.").format(
					comma_and([(day) for day in get_repeated(availability_days)], add_quotes=False)
				)
			)

	def get_availability_days(self):
		return [d.day for d in self.get("availability_days", [])]


def get_list_context(context):
    # 1. Change the "List" heading
    context.title = "Our Doctors" 
    
    # 2. Hide the Breadcrumbs (My Account > List). navbar and footer can't be hidden from here.
    context.no_breadcrumbs = 1
    

def get_repeated(values: Iterable) -> list:
	unique = set()
	repeated = set()

	for value in values:
		if value in unique:
			repeated.add(value)
		else:
			unique.add(value)

	return [str(x) for x in repeated]
	

@frappe.whitelist()
def invite_user(practitioner: str):
	practitioner = frappe.get_doc("Practitioner", practitioner)
	practitioner.check_permission()

	if not practitioner.email:
		frappe.throw(("Please enter Email, it is mandatory to create a user"))

	user = frappe.get_doc(
		{
			"doctype": "User",
			"first_name": practitioner.full_name,
			"email": practitioner.email,
			"mobile_no": practitioner.mobile,
			"user_type": "Website User",
			'roles': [ { 'role': 'Doctor' } ],
			"send_welcome_email": 1,
		}
	).insert()

	return user.name

@frappe.whitelist()
def add_as_supplier(practitioner: str):
	practitioner = frappe.get_doc("Practitioner", practitioner)
	practitioner.check_permission()

	supplier = frappe.get_doc(
		{
			"doctype": "Supplier",
			"supplier_name": practitioner.full_name,
			"supplier_type": "Individual",
		}
	).insert()

	return supplier.name


@frappe.whitelist()
def doctor_profile():
	practitioners = frappe.db.get_list(
		"Practitioner",
		filters={"user_id": frappe.session.user},
	)

	if not practitioners:
		frappe.throw("Practitioner not found")

	practitioner = frappe.get_doc(
		"Practitioner",
		practitioners[0].name,
	)

	return {
		"doctor": practitioner,
	}


@frappe.whitelist()
def update_doctor_profile(docname=None, updates=None):
    if not docname:
        frappe.throw("docname is required")

    if not updates:
        updates = {}

    practitioner = frappe.get_doc("Practitioner", docname)

    if practitioner.user_id != frappe.session.user:
        frappe.throw(
            "Not authorized to update this profile",
            frappe.PermissionError,
        )

    editable_fields = [
        "professional_summary",
        "qualification",
        "experience_years",
        "council_name",
        "registration_no",
        "gender",
        "email",
        "mobile",
        "title",
        "first_name",
        "middle_name",
        "last_name",
        "dob",
        "nationality",
        "photo",
        "address_line1",
        "city",
        "state",
        "pincode",
        "additional_qualification",
        "designation",
        "super_specialty",
        "registration_valid_upto",
        "registration_letter",
        "digital_signature_url",
        "primary_facility",
        "telemedicine_certified",
        "hpr_verified",
        "doctor_type",
        "abdm_council_code",
        "abdm_specialty_code",
        "currency",
        "normal_charge",
        "emergency_charge",
        "priority_charge",
        "home_visit_charge",
        "in_clinic_charge",
        "teleconsultation_charge",
        "is_active",
        "available_from",
        "available_till",
        "available_in_emergency_from",
        "available_in_emergency_till",
        "is_published",
    ]

    for fieldname, value in updates.items():
        if fieldname in editable_fields:
            practitioner.set(fieldname, value)

    if "languages_known" in updates:
        languages_known = updates.get("languages_known") or []
        practitioner.set("languages_known", [])

        for lang in languages_known:
            if isinstance(lang, str):
                practitioner.append(
                    "languages_known",
                    {"spoken_language_option": lang},
                )
            elif isinstance(lang, dict):
                practitioner.append(
                    "languages_known",
                    lang,
                )

    if "availability_days" in updates:
        availability_days = updates.get("availability_days") or []
        practitioner.set("availability_days", [])

        for availability_day in availability_days:
            if isinstance(availability_day, str):
                practitioner.append(
                    "availability_days",
                    {"day": availability_day},
                )
            elif isinstance(availability_day, dict):
                practitioner.append(
                    "availability_days",
                    {
                        "day": availability_day.get("day"),
                        "custom_from_time": availability_day.get("from_time"),
                        "custom_to_time": availability_day.get("to_time"),
                        "custom_emergency_from": availability_day.get("emergency_from"),
                        "custom_emergency_to": availability_day.get("emergency_to"),
                    },
                )

    practitioner.save(ignore_permissions=True)
    frappe.db.commit()

    return {"doctor": practitioner}


@frappe.whitelist()
def doctor_documents(docname=None):
    if not docname:
        frappe.throw("docname is required")

    practitioner = frappe.get_doc("Practitioner", docname)

    if practitioner.user_id != frappe.session.user:
        frappe.throw(
            "Not authorized to view these documents",
            frappe.PermissionError,
        )

    files = frappe.get_all(
        "File",
        filters=[
            ["attached_to_doctype", "=", "Practitioner"],
            ["attached_to_name", "=", practitioner.name],
            ["attached_to_field", "!=", "photo"],
        ],
        fields=[
            "name",
            "file_name",
            "file_url",
            "is_private",
            "attached_to_field",
            "creation",
        ],
        order_by="creation desc",
    )

    # Avoiding duplicate File records
    unique_files = []
    seen_urls = set()

    for file in files:
        if file.file_url in seen_urls:
            continue

        seen_urls.add(file.file_url)
        unique_files.append(file)

    return {
        "documents": unique_files,
    }


@frappe.whitelist()
def delete_doctor_document(docname=None, file_name=None):
    if not docname:
        frappe.throw("docname is required")

    if not file_name:
        frappe.throw("File name is required")

    practitioner = frappe.get_doc("Practitioner", docname)

    if practitioner.user_id != frappe.session.user:
        frappe.throw(
            "Not authorized to delete this document",
            frappe.PermissionError,
        )

    file_doc = frappe.get_doc("File", file_name)

    if (
        file_doc.attached_to_doctype != "Practitioner"
        or file_doc.attached_to_name != practitioner.name
    ):
        frappe.throw(
            "Not authorized to delete this document",
            frappe.PermissionError,
        )

    file_url = file_doc.file_url

    if (
        file_doc.attached_to_field == "registration_letter"
        and practitioner.registration_letter == file_url
    ):
        practitioner.registration_letter = None
        practitioner.save(ignore_permissions=True)

    frappe.delete_doc(
        "File",
        file_doc.name,
        ignore_permissions=True,
    )

    frappe.db.commit()

    return {
        "success": True,
        "file_name": file_doc.name,
    }    