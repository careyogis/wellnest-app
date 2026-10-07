# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate, get_datetime


class PractitionerPayout(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_totals()
        self.validate_payment_info()

    def validate_dates(self):
        if self.cycle_start_date and self.cycle_end_date:
            if getdate(self.cycle_end_date) < getdate(self.cycle_start_date):
                frappe.throw("Cycle End Date cannot be earlier than Cycle Start Date")

    def calculate_totals(self):
        items = self.get("items") or []
        self.consultation_count = len(items)
        self.gross_amount = sum(flt(item.payout_rate) for item in items)
        self.adjustments = flt(self.adjustments or 0)
        self.net_payable_amount = max(0.0, flt(self.gross_amount) - self.adjustments)

    def validate_payment_info(self):
        if self.status == "Paid":
            if not self.payment_reference:
                frappe.throw("Payment Reference / UTR is required when marking a payout as Paid")
            if not self.payout_date:
                self.payout_date = nowdate()

    def on_update(self):
        if self.has_value_changed("status"):
            self.handle_status_change()

    def handle_status_change(self):
        items = self.get("items") or []
        appointment_names = [item.patient_appointment for item in items if item.patient_appointment]
        if not appointment_names:
            return

        if self.status in ["Draft", "Approved"]:
            frappe.db.set_value(
                "Patient Appointment",
                {"name": ["in", appointment_names]},
                {"payout_status": "In Payout", "practitioner_payout": self.name},
            )
        elif self.status == "Paid":
            frappe.db.set_value(
                "Patient Appointment",
                {"name": ["in", appointment_names]},
                {"payout_status": "Settled", "practitioner_payout": self.name},
            )
            # Create ERPNext Purchase Invoice and Payment Entry if Supplier is configured
            self.create_erpnext_accounting_entries()
        elif self.status == "Cancelled":
            frappe.db.set_value(
                "Patient Appointment",
                {"name": ["in", appointment_names]},
                {"payout_status": "Accrued", "practitioner_payout": None},
            )

    def on_trash(self):
        if self.status == "Paid":
            frappe.throw("Cannot delete a Paid Practitioner Payout")

        items = self.get("items") or []
        appointment_names = [item.patient_appointment for item in items if item.patient_appointment]
        if appointment_names:
            frappe.db.set_value(
                "Patient Appointment",
                {"name": ["in", appointment_names]},
                {"payout_status": "Accrued", "practitioner_payout": None},
            )

    @frappe.whitelist()
    def mark_as_paid(self, payment_reference, payout_date=None, payment_method=None):
        if not payment_reference:
            frappe.throw("Please provide the Payment Reference / UTR")

        self.status = "Paid"
        self.payment_reference = payment_reference
        self.payout_date = payout_date or nowdate()
        if payment_method:
            self.payment_method = payment_method

        self.save()
        frappe.db.commit()
        return {"success": True, "message": f"Payout {self.name} marked as Paid"}

    @frappe.whitelist()
    def cancel_payout(self):
        if self.status == "Paid":
            frappe.throw("Paid payouts cannot be directly cancelled. Please handle via adjustment.")

        self.status = "Cancelled"
        self.save()
        frappe.db.commit()
        return {"success": True, "message": f"Payout {self.name} has been cancelled"}

    def create_erpnext_accounting_entries(self):
        """
        Hybrid ERPNext integration:
        Generates Purchase Invoice and Payment Entry if Practitioner has linked Supplier.
        """
        supplier = self.supplier or frappe.db.get_value("Practitioner", self.practitioner, "supplier")
        if not supplier:
            frappe.logger().info(
                f"Practitioner {self.practitioner} has no linked Supplier. Skipping ERPNext accounting entries."
            )
            return

        if self.purchase_invoice:
            # Already created
            return

        try:
            from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_payment_entry

            company = frappe.db.get_single_value("Global Defaults", "default_company")
            if not company:
                companies = frappe.get_all("Company", limit=1, pluck="name")
                company = companies[0] if companies else None

            if not company:
                frappe.logger().warning("No company configured. Skipping ERPNext Purchase Invoice creation.")
                return

            # 1. Create Purchase Invoice
            pi = frappe.get_doc(
                {
                    "doctype": "Purchase Invoice",
                    "supplier": supplier,
                    "company": company,
                    "posting_date": self.payout_date or nowdate(),
                    "bill_no": self.name,
                    "bill_date": self.payout_date or nowdate(),
                    "remarks": f"Teleconsultation Payout batch {self.name} for Dr. {self.practitioner_name} ({self.cycle_start_date} to {self.cycle_end_date})",
                    "items": [
                        {
                            "item_name": "Teleconsultation Services",
                            "description": f"Teleconsultation services ({self.consultation_count} consultations)",
                            "qty": 1,
                            "rate": flt(self.net_payable_amount),
                            "amount": flt(self.net_payable_amount),
                        }
                    ],
                }
            )
            pi.insert(ignore_permissions=True)
            pi.submit()

            self.db_set("purchase_invoice", pi.name)

            # 2. Create Payment Entry against Purchase Invoice
            pe = make_payment_entry(pi.name)
            pe.reference_no = self.payment_reference
            pe.reference_date = self.payout_date or nowdate()
            pe.insert(ignore_permissions=True)
            pe.submit()

            self.db_set("payment_entry", pe.name)
            frappe.logger().info(
                f"Created ERPNext Purchase Invoice {pi.name} and Payment Entry {pe.name} for Payout {self.name}"
            )

        except Exception:
            # Log error without failing payout status
            frappe.log_error(
                title=f"ERPNext Accounting Entry creation failed for Payout {self.name}",
                message=frappe.get_traceback(),
            )
