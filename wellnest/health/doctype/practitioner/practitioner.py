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
def update_doctor_profile(
        professional_summary=None,
        qualification=None,
        experience_years=None,
        council_name=None,
        registration_no=None,
        languages_known=None,
        gender=None,
        email=None,
        mobile=None,
):
        practitioners = frappe.db.get_list(
                "Practitioner",
                filters={"user_id": frappe.session.user},
        )

        if not practitioners:
                frappe.throw("Practitioner not found")

        practitioner = frappe.get_doc("Practitioner", practitioners[0].name)

        if practitioner.user_id != frappe.session.user:
                frappe.throw("Not authorized to update this profile", frappe.PermissionError)

        if professional_summary is not None:
                practitioner.professional_summary = professional_summary
        if qualification is not None:
                practitioner.qualification = qualification
        if experience_years is not None:
                practitioner.experience_years = experience_years
        if council_name is not None:
                practitioner.council_name = council_name
        if registration_no is not None:
                practitioner.registration_no = registration_no
        if gender is not None:
                practitioner.gender = gender
        if email is not None:
                practitioner.email = email
        if mobile is not None:
                practitioner.mobile = mobile

        if languages_known is not None:
                practitioner.set("languages_known", [])
                for lang in languages_known:
                        practitioner.append("languages_known", {"spoken_language_option": lang})

        practitioner.save(ignore_permissions=True)
        frappe.db.commit()

        return {"doctor": practitioner}