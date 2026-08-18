# Copyright (c) 2026, www.careyogis.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MedicalDocument(Document):

    def after_insert(self):
        if self.document_type != "Prescription":
            return

        # Mark the document as queued
        self.db_set("processing_status", "Queued")

        # Send prescription processing to the background worker
        frappe.enqueue(
            "wellnest.services.prescription.processor.process_prescription",
            document_name=self.name,
            queue="long",
            enqueue_after_commit=True,
        )

        frappe.logger().info(
            f"Prescription {self.name} added to processing queue"
        )
