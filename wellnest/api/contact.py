import json
import frappe
from frappe.rate_limiter import rate_limit


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=300)
def contactUs():
	data = frappe.form_dict
	email = data.get("email")

	if email and frappe.db.exists("CY Lead", {"email": email}):
		return {"status": "exists", "message": "You are already on the list!"}

	new_doc = frappe.get_doc(
		{
			"doctype": "CY Lead",
			"full_name": data.get("full_name"),
			"phone_number": data.get("phone"),
			"email": data.get("email"),
			"city": data.get("city"),
			"requirement": data.get("requirement"),
			"enquiry_details": data.get("enquiry"),
			"source": data.get("source") or "Website",
		}
	)

	new_doc.insert(ignore_permissions=True)
	return {"status": "success"}


@frappe.whitelist()
def get_customer_for_user(user):
	customer_name = None
	# Checks if supplied user is an email or mobile number
	if "@" in user:
		contact_name = frappe.db.get_value(
			"Contact Email", {"email_id": user}, "parent"
		)
	else:
		# fix phone number for proper 'Contact Phone' lookup
		if not user.startswith("+91"):
			user = "+91" + user
		contact_name = frappe.db.get_value(
			"Contact Phone", {"phone": user}, "parent"
		)
		
	if contact_name:
		customer_name = frappe.db.get_value(
			"Dynamic Link",
			{"link_doctype": "Customer", "parenttype": "Contact", "parent": contact_name},
			"link_name"
		)

	return customer_name


@frappe.whitelist()
def update_fcm_token():
	try:
		data = json.loads(frappe.request.data)
		fcm_token = data.get("fcm_token")

		if not fcm_token:
			frappe.throw("Missing fcm_token", title="Validation Error")

		# Use the session user's email so the client never needs to supply it,
		# and there is no risk of one user overwriting another's token.
		email_id = frappe.session.user

		contact_name = frappe.db.get_value(
			"Contact Email", {"email_id": email_id}, "parent"
		)

		if not contact_name:
			frappe.throw(f"Contact not found for {email_id}", title="Not Found")

		# Targeted single-field update — no need to load the full Contact doc.
		frappe.db.set_value("Contact", contact_name, "custom_fcm_token", fcm_token)

		frappe.logger().info(f"FCM Token updated for: {email_id}")
		return {"status": "success", "message": "FCM Token updated successfully"}

	except Exception as e:
		frappe.log_error(f"Exception: {str(e)}", "update_fcm_token")
		return {"status": "error", "message": str(e)}
