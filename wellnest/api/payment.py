import frappe
from frappe import _
from frappe.utils import now


def _get_or_create_registration_invoice(customer):
	"""
	Finds existing submitted registration invoice for customer, or creates a new one.
	"""
	registration_item_code = frappe.db.get_value(
		"Item", {"item_name": ["like", "%registration%"]}, "name"
	)

	if not registration_item_code:
		return None, "No registration item found."

	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"customer": customer.name, "docstatus": 1},
		order_by="creation desc",
	)

	invoice = None
	for inv in invoices:
		items = frappe.get_all(
			"Sales Invoice Item",
			filters={"parent": inv.name, "item_code": registration_item_code},
		)
		if items:
			invoice = frappe.get_doc("Sales Invoice", inv.name)
			break

	if not invoice:
		invoice = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": customer.name,
				"items": [{"item_code": registration_item_code, "qty": 1}],
			}
		)
		invoice.insert(ignore_permissions=True)
		invoice.submit()

	return invoice, None


def _build_payment_response(customer, invoice):
	"""
	Builds standard payment status & UPI QR response dict.
	"""
	if invoice.outstanding_amount == 0:
		return {
			"success": True,
			"data": {
				"status": "paid",
				"accepted": True,
				"custom_registration_term": customer.custom_registration_term,
				"custom_acceptance_timestamp": customer.custom_acceptance_timestamp,
				"message": "✅ Thank You! Payment already completed.",
				"invoice_number": invoice.name,
				"payment_amount": invoice.rounded_total,
				"customer_name": customer.customer_name,
			},
		}

	upi_id = frappe.db.get_value("Company", invoice.company, "custom_upi_id")
	if not upi_id:
		return {
			"success": False,
			"error": f"UPI ID not configured for {invoice.company}",
		}

	upi_uri = f"upi://pay?pa={upi_id}&pn={customer.customer_name}&am={format(invoice.rounded_total, '.2f')}&cu=INR&tn=Invoice {invoice.name}"

	return {
		"success": True,
		"data": {
			"status": "accepted",
			"accepted": True,
			"custom_registration_term": customer.custom_registration_term,
			"custom_acceptance_timestamp": customer.custom_acceptance_timestamp,
			"customer_id": customer.name,
			"invoice_number": invoice.name,
			"payment_amount": invoice.rounded_total,
			"upi_id": upi_id,
			"upi_uri": upi_uri,
			"customer_name": customer.customer_name,
		},
	}


@frappe.whitelist(allow_guest=True)
def get_terms_content(type=None):
	terms = frappe.db.get_value(
		"Terms and Conditions",
		[{"custom_is_active": 1},{"custom_type": type or "General"}],
		["name", "title", "terms"],
		order_by="modified desc",
		as_dict=True,
	)
	if not terms:
		return {"success": False, "error": "No active Terms & Conditions found"}

	return {"success": True, "content": terms.terms, "title": terms.title}


@frappe.whitelist(allow_guest=True)
def accept_terms():
	"""
	Guest API to accept T&C and handle registration invoice.
	Returns current status:
	  - pending -> T&C not accepted
	  - accepted -> T&C accepted, invoice unpaid (includes QR)
	  - paid -> T&C accepted, invoice paid (Thank You)
	"""
	try:
		data = frappe.request.json or {}
		customer_id = data.get("customer_id")
		engagement_id = data.get("engagement_id")

		if not customer_id and not engagement_id:
			frappe.throw(_("Missing Customer ID or Engagement ID."))

		if not customer_id:
			engagement = frappe.get_doc("Engagement", engagement_id)
			customer_id = engagement.customer

		customer = frappe.get_doc("Customer", customer_id)

		if customer.custom_registration_term in [None, "pending"]:
			latest_terms = frappe.db.get_value(
				"Terms and Conditions",
				{"custom_is_active": 1},
				"name",
				order_by="modified desc",
			)
			customer.custom_registration_term = "accepted"
			customer.custom_acceptance_timestamp = now()
			if latest_terms:
				customer.custom_accepted_term = latest_terms
			customer.save(ignore_permissions=True)
			frappe.db.commit()

		invoice, error = _get_or_create_registration_invoice(customer)
		if error:
			return {"success": False, "error": error}

		return _build_payment_response(customer, invoice)

	except Exception:
		frappe.log_error(frappe.get_traceback(), "accept_terms Error")
		return {"success": False, "error": "Unexpected server error. Check logs."}


@frappe.whitelist(allow_guest=True)
def get_payment_details(customer_id=None, engagement_id=None):
	"""
	Guest API to fetch T&C + registration invoice details.
	Flow:
	1. Check if Terms accepted. If not, return pending.
	2. If accepted, fetch registration invoice (create only if none exists).
	3. If invoice paid -> show Thank You.
	4. If invoice unpaid -> return UPI QR.
	"""
	try:
		if not customer_id and engagement_id:
			engagement = frappe.get_doc("Engagement", engagement_id)
			customer_id = engagement.customer

		if not customer_id:
			return {"success": False, "error": "Missing customer ID."}

		customer = frappe.get_doc("Customer", customer_id)
		status = customer.custom_registration_term or "pending"
		accepted = status in ["accepted", "paid"]
		acceptance_timestamp = customer.custom_acceptance_timestamp

		if not accepted:
			return {
				"success": True,
				"data": {
					"status": "pending",
					"accepted": False,
					"custom_registration_term": status,
					"custom_acceptance_timestamp": acceptance_timestamp,
					"message": "T&C not accepted yet.",
				},
			}

		invoice, error = _get_or_create_registration_invoice(customer)
		if error:
			return {"success": False, "error": error}

		return _build_payment_response(customer, invoice)

	except Exception:
		frappe.log_error(frappe.get_traceback(), "get_payment_details Error")
		return {"success": False, "error": "Unexpected error occurred."}
