# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TermsAcceptance(Document):
    def before_save(self):
        # Ensure we only capture the IP when the record is first created
        if self.is_new():
            # Check if there is an active HTTP request (ignores background jobs)
            if hasattr(frappe.local, 'request') and frappe.local.request:
                self.ip_address = getattr(frappe.local, 'request_ip', None)
