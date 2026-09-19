# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HealthVault(Document):
    def before_save(self):
        if not self.batch_number and self.patient:
            max_batch = frappe.db.sql("""
                select max(batch_number)
                from `tabHealth Vault`
                where patient = %s
            """, self.patient)
            
            self.batch_number = (max_batch[0][0] or 0) + 1
