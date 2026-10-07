# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class SmartPrescription(Document):
    pass

    # Push Notify upon prescription submit
    def after_insert(self):
        # Only proceed if the status changed to "Scheduled"
        if not self.workflow_state == "Complete":
            return

        self.create_new_notification(self.patient)


    # Push Notify upon prescription submit
    def on_update(self):
        # Only proceed if the status changed to "Scheduled"
        if not (self.has_value_changed("workflow_state") and self.workflow_state == "Complete"):
            return

        # Notify users that the prescription is ready
        self.create_new_notification(self.patient)

    def create_new_notification(patient):
        # Notify users that the prescription is ready
        app_notification = frappe.get_doc(
            {
                "doctype": "App Notification",
                "title": "Your Prescription Is Ready",
                "body": "You can view and download your Prescription from Smart Prescription screen",
                "target_audience": "Specific Patient",
                "patient": patient,
                "scheduled_time": now(),
            }
        )
        app_notification.insert(ignore_permissions=True)
        frappe.db.commit()
