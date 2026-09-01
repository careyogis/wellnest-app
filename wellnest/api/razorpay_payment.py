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
def create_payment_order(service_id):
	"""
	Creates a Razorpay order and returns details to the frontend.
	"""	
	# Fetch invoice details 
	patient_appointment = frappe.get_doc("Patient Appointment", service_id)
	sales_order_id = patient_appointment.sales_order or ''
	price_inr = patient_appointment.consultation_fee or 1
	member_id = patient_appointment.patient
	sub_type = "teleconsultation"
	duration_months = 1

	client = get_razorpay_client()
	
	order_data = {
		'receipt': f'RCPT_{int(time.time())}',
		'amount': int(price_inr * 100), # amount in paise
		'currency': 'INR',
		'payment_capture': 1,
		'notes': {
			'sales_order_id': sales_order_id,
			'user_id': member_id,
			'plan_type': f"{sub_type}-{duration_months}",
		}
	}
	
	order = client.order.create(data=order_data)
	
	return {
		"success": True,
		"order_id": order.get('id'),
		"sales_order_id": sales_order_id,
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
def create_payment_link(sales_order_id):
	"""
	Replaces create_payment_link()
	"""
	return f"/payment?sales_invoice={sales_order_id}"
