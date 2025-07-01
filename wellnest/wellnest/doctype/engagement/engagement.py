# Copyright (c) 2024, www.thewellnest.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from frappe import _
# from frappe.utils import now
# import qrcode

class Engagement(Document):
    pass

# # Generate a QR code from a given UPI URI
# def generate_upi_qr(upi_uri, file_path="/tmp/upi_qr.png"):
#     img = qrcode.make(upi_uri)
#     img.save(file_path)
#     return file_path


# @frappe.whitelist(allow_guest=True)

# def accept_terms():
#     """
#     Called from frontend when customer accepts terms and conditions.
#     Marks the engagement as accepted with current timestamp.
#     """
#     try:
#         data = frappe.request.json or {}

#         engagement_id = data.get('engagement_id')
#         if not engagement_id:
#             frappe.throw(_("Missing Engagement ID"))

#         doc = frappe.get_doc("Engagement", engagement_id)
#         doc.terms_accepted = 1
#         doc.acceptance_timestamp = now()
#         doc.save(ignore_permissions=True)

#         return {"success": True}

#     except Exception as e:
#         frappe.log_error(title="Accept Terms Error", message=frappe.get_traceback())
#         raise

# @frappe.whitelist(allow_guest=True)
# def get_engagement_details(engagement_id):
#     """
#     Fetches engagement and latest unpaid invoice details for the customer.
#     Also fetches the UPI ID from the Company and constructs UPI payment URI.
#     Returns required data for rendering the QR and payment interface.
#     """
#     try:
#         if not engagement_id:
#             return {
#                 "success": False,
#                 "error": "Missing engagement_id."
#             }

#         # Check if engagement exists
#         if not frappe.db.exists("Engagement", engagement_id):
#             return {
#                 "success": False,
#                 "error": "Engagement not found."
#             }

#         engagement = frappe.get_doc("Engagement", engagement_id)

#         customer_name = engagement.customer
#         if not customer_name:
#             return {
#                 "success": False,
#                 "error": "Customer not linked to Engagement."
#             }

#         # Get the latest unpaid Sales Invoice for the customer
#         invoice = frappe.db.get_all(
#             "Sales Invoice",
#             filters={
#                 "customer": customer_name,
#                 "outstanding_amount": [">", 0],
#                 "docstatus": 1
#             },
#             fields=["name", "rounded_total", "company"],
#             order_by="posting_date desc",
#             limit=1
#         )

#         if not invoice:
#             return {
#                 "success": False,
#                 "error": "No unpaid or overdue invoice found for this customer."
#             }

#         invoice = invoice[0]

#         # Fetch UPI ID from Company
#         upi_id = frappe.db.get_value("Company", invoice.company, "custom_upi_id")
#         if not upi_id:
#             return {
#                 "success": False,
#                 "error": "UPI ID not configured in Company settings."
#             }

#         # Construct UPI URI for fixed amount and invoice reference
#         upi_uri = (
#             f"upi://pay?"
#             f"pa={upi_id}"
#             f"&pn={customer_name}"
#             f"&am={format(invoice.rounded_total, '.2f')}"
#             f"&cu=INR"
#             f"&tn=Invoice {invoice.name}"
#         )

#         # Generate QR code image (file path not used on frontend currently)
#         generate_upi_qr(upi_uri)

#         return {
#             "success": True,
#             "data": {
#                 "engagement_id": engagement.name,
#                 "invoice_number": invoice.name,
#                 "payment_amount": invoice.rounded_total or 0,
#                 "upi_id": upi_id,
#                 "customer_name": customer_name,
#                 "upi_uri": upi_uri
#             }
#         }

#     except Exception:
#         frappe.log_error(frappe.get_traceback(), "Error in get_engagement_details")
#         return {
#             "success": False,
#             "error": "Unexpected error occurred."
#         }
