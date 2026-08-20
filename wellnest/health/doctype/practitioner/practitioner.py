# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

from datetime import datetime
from select import select

import frappe
from frappe.website.website_generator import WebsiteGenerator
from collections.abc import Iterable
from frappe.utils.data import comma_and


class Practitioner(WebsiteGenerator):
	def get_context(self, context):
		context.charge_multiplier = 1.25
		if (self.practicing_from):
			context.experience = (datetime.now().date() - self.practicing_from).days // 365

		return context

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
    
    # 2. Hide the Breadcrumbs (My Account > List).
    context.no_breadcrumbs = 1
    context.base_template_path = "templates/wellnest_web.html"
    # Add education_list to the context for each practitioner
    # for practitioner in context:
    #     education_list = [edu.degree for edu in practitioner.education_history]
    #     practitioner.education_list = education_list    

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


def get_current_practitioner(docname=None):
    if docname:
        practitioner = frappe.get_doc("Practitioner", docname)
    else:
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

    if practitioner.user_id != frappe.session.user:
        frappe.throw(
            "Not authorized to access this profile",
            frappe.PermissionError,
        )

    return practitioner


@frappe.whitelist()
def doctor_profile():
    practitioner = get_current_practitioner()

    doctor = practitioner.as_dict()

    if practitioner.specialty:
        doctor["specialty_name"] = frappe.db.get_value(
            "Medical Specialty",
            practitioner.specialty,
            "specialty_name",
        )

    if practitioner.super_specialty:
        doctor["super_specialty_name"] = frappe.db.get_value(
            "Medical Super Specialty",
            practitioner.super_specialty,
            "super_specialty_name",
        )

    if practitioner.primary_facility:
        doctor["primary_facility_name"] = frappe.db.get_value(
            "Hospital",
            practitioner.primary_facility,
            "hospital_name",
       )

    return {
        "doctor": doctor,
    }


@frappe.whitelist()
def update_doctor_profile(docname=None, updates=None):
    practitioner = get_current_practitioner(docname)

    if not updates:
        updates = {}

    excluded_fields = {
        "name",
        "owner",
        "creation",
        "modified",
        "modified_by",
        "docstatus",
        "doctype",
        "user_id",
        "supplier",
        "sales_partner",
        "full_name",
        "account_status",
        "abdm_council_code",
        "abdm_specialty_code",
        "route",
        "languages_known",
        "availability_days",
        "education_history",
    }

    for fieldname, value in updates.items():
        if fieldname in excluded_fields:
            continue

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

                
    if "education_history" in updates:
       education_history = updates.get("education_history") or []
       practitioner.set("education_history", [])

       for education in education_history:
           if isinstance(education, dict):
              practitioner.append(
                  "education_history",
                  {
                      "degree": education.get("degree"),
                      "institution": education.get("institution"),
                      "year_of_completion": education.get("year_of_completion"),
                  },
              )


    practitioner.save(ignore_permissions=True)
    frappe.db.commit()

    return {"doctor": practitioner}


@frappe.whitelist()
def doctor_documents(docname=None):
    practitioner = get_current_practitioner(docname)

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
    if not file_name:
       frappe.throw("File name is required")

    practitioner = get_current_practitioner(docname)

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