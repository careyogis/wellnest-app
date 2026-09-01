import frappe
from frappe import _
import razorpay
import time

def get_razorpay_client():
	key_id = frappe.conf.get("razorpay_key_id")
	key_secret = frappe.conf.get("razorpay_key_secret")
	if not key_id or not key_secret:
		frappe.throw(_("Razorpay credentials not configured in site config."))
	return razorpay.Client(auth=(key_id, key_secret))

@frappe.whitelist(allow_guest=True)
def create_payment_order(subscription_id):
	"""
	Replaces pay() from _Payments.php
	Creates a Razorpay order and returns details to the frontend.
	"""
	# Decode logic would go here if subscription_id is encrypted
	
	# Fetch subscription details (Replace 'Subscription' with your actual DocType)
	# subscription = frappe.get_doc("Subscription", subscription_id)
	
	# For demonstration, using dummy data based on the PHP script structure
	price_inr = 500
	member_id = "user123"
	sub_type = "premium"
	duration_months = 12

	client = get_razorpay_client()
	
	order_data = {
		'receipt': f'RCPT_{int(time.time())}',
		'amount': int(price_inr * 100), # amount in paise
		'currency': 'INR',
		'payment_capture': 1,
		'notes': {
			'user_subscription_id': subscription_id,
			'user_id': member_id,
			'plan_type': f"{sub_type}-{duration_months}",
		}
	}
	
	order = client.order.create(data=order_data)
	
	return {
		"success": True,
		"order_id": order.get('id'),
		"subscription_id": subscription_id,
		"key_id": frappe.conf.get("razorpay_key_id")
	}

@frappe.whitelist(allow_guest=True)
def payment_verify(razorpay_payment_id, razorpay_order_id, razorpay_signature):
	"""
	Replaces payment_verify() from _Payments.php
	Verifies the Razorpay signature and updates status.
	"""
	client = get_razorpay_client()
	
	try:
		client.utility.verify_payment_signature({
			'razorpay_order_id': razorpay_order_id,
			'razorpay_payment_id': razorpay_payment_id,
			'razorpay_signature': razorpay_signature
		})
		
		# Signature is valid. Update payment status in database here.
		# e.g., frappe.db.set_value('Subscription Payment', order_id, 'status', 'success')
		frappe.db.commit()
		
		return {"success": True, "message": "Payment verified successfully", "redirect_url": "/payment-success"}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Razorpay Signature Verification Failed")
		return {"success": False, "message": "Payment verification failed", "redirect_url": "/payment-failure"}

@frappe.whitelist(allow_guest=True)
def create_payment_link(subscription_id):
	"""
	Replaces create_payment_link()
	"""
	return f"/payment?subscription={subscription_id}"
