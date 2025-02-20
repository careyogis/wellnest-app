# Copyright (c) 2025, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CaregiverResponse(Document):
	pass

import frappe
from frappe.model.document import Document
from datetime import datetime

class CaregiverResponse(Document):
    def before_insert(self):
        # Set both timestamps before saving
        # self.broadcast_time = datetime.now()  # Capture the broadcast time
        self.response_time = datetime.now()  # Capture the response time

