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
                        "online_from": availability_day.get("online_from") + ":00:00" if availability_day.get("online_from") else '',
                        "online_to": availability_day.get("online_to") + ":00:00" if availability_day.get("online_to") else '',
                        "emergency_from": availability_day.get("emergency_from") + ":00:00" if availability_day.get("emergency_from") else '',
                        "emergency_to": availability_day.get("emergency_to") + ":00:00" if availability_day.get("emergency_to") else '',
                        "clinic_from": availability_day.get("clinic_from") + ":00:00" if availability_day.get("clinic_from") else '',
                        "clinic_to": availability_day.get("clinic_to") + ":00:00" if availability_day.get("clinic_to") else '',
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


@frappe.whitelist()
def get_doctor_timeaway():
    practitioner = get_current_practitioner()

    return frappe.get_all(
        "Practitioner TimeAway",
        filters={
            "practitioner": practitioner.name,
            "status": "Approved",
        },
        fields=[
            "name",
            "from_date",
            "to_date",
            "from_time",
            "to_time",
            "reason",
            "status",
        ],
        order_by="from_date asc, from_time asc",
    )


@frappe.whitelist()
def save_doctor_timeaway(
    from_date,
    to_date=None,
    from_time="00:00:00",
    to_time="23:59:59",
    reason=None,
    name=None,
):
    practitioner = get_current_practitioner()

    to_date = to_date or from_date

    if from_date > to_date:
        frappe.throw("From Date cannot be after To Date.")

    if from_time >= to_time:
        frappe.throw("From Time must be before To Time.")

    if name:
        timeaway = frappe.get_doc("Practitioner TimeAway", name)

        if timeaway.practitioner != practitioner.name:
            frappe.throw(
                "Not authorized to modify this unavailable period",
                frappe.PermissionError,
            )

        timeaway.from_date = from_date
        timeaway.to_date = to_date
        timeaway.from_time = from_time
        timeaway.to_time = to_time
        timeaway.reason = reason

        timeaway.save(ignore_permissions=True)

    else:
        timeaway = frappe.get_doc({
            "doctype": "Practitioner TimeAway",
            "practitioner": practitioner.name,
            "from_date": from_date,
            "to_date": to_date,
            "from_time": from_time,
            "to_time": to_time,
            "reason": reason,
            "status": "Approved",
        })

        timeaway.insert(ignore_permissions=True)

    return {
        "success": True,
        "name": timeaway.name,
        "status": timeaway.status,
    }


@frappe.whitelist()
def cancel_doctor_timeaway(name):
    practitioner = get_current_practitioner()

    timeaway = frappe.get_doc("Practitioner TimeAway", name)

    if timeaway.practitioner != practitioner.name:
        frappe.throw(
            "Not authorized to modify this unavailable period",
            frappe.PermissionError,
        )

    timeaway.status = "Cancelled"
    timeaway.save(ignore_permissions=True)

    return {
        "success": True,
        "name": timeaway.name,
        "status": timeaway.status,
    }


@frappe.whitelist(allow_guest=False)
def search_doctors(query=None, specialty=None):
	"""Search active practitioners by name or specialty.

	Args:
		query (str): Free-text search matched against full_name and specialty.
		specialty (str): Exact specialty filter (applied as OR alongside query filters).

	Returns:
		list[dict]: Practitioner records with education_history and languages_known
		            as nested lists, grouped in Python from 3 bulk DB queries.
	"""
	filters = [["is_active", "=", 1]]

	or_filters = []
	if query:
		or_filters.append(["full_name", "like", f"%{query}%"])
		or_filters.append(["specialty", "like", f"%{query}%"])
	if specialty:
		or_filters.append(["specialty", "=", specialty])

	get_all_kwargs = dict(
		doctype="Practitioner",
		filters=filters,
		fields=[
			"name",
			"full_name",
			"specialty",
			"super_specialty",
			"designation",
			"professional_summary",
			"online_charge",
			"photo",
			"city",
			"practicing_from",
		],
		limit=50,
	)
	if or_filters:
		get_all_kwargs["or_filters"] = or_filters

	practitioners = frappe.db.get_all(**get_all_kwargs)

	if not practitioners:
		return []

	practitioner_names = [p.name for p in practitioners]

	# Bulk fetch child rows — 2 queries regardless of result count
	education_rows = frappe.db.get_all(
		"Practitioner Education",
		filters=[["parent", "in", practitioner_names]],
		fields=["parent", "degree", "year_of_completion"],
	)

	language_rows = frappe.db.get_all(
		"Spoken Language Option",
		filters=[["parent", "in", practitioner_names]],
		fields=["parent", "spoken_language_option"],
	)

	# Group child rows by parent in Python
	education_map = {}
	for row in education_rows:
		education_map.setdefault(row.parent, []).append({
			"degree": row.degree,
			"year_of_completion": row.year_of_completion,
		})

	language_map = {}
	for row in language_rows:
		language_map.setdefault(row.parent, []).append(row.spoken_language_option)

	result = []
	for p in practitioners:
		doc = dict(p)
		doc["education_history"] = education_map.get(p.name, [])
		doc["languages_known"] = language_map.get(p.name, [])
		result.append(doc)

	return result