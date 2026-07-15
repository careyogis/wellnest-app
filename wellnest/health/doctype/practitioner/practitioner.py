# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Practitioner(Document):
	def before_save(self):		
		self.full_name = f"{self.title} {self.first_name} {self.last_name}";
