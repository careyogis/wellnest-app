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
	price_inr = patient_appointment.consultation_fee or 1
	member_id = patient_appointment.patient

	client = get_razorpay_client()
	
	order_data = {
		'receipt': f'RCPT_{int(time.time())}',
		'amount': int(price_inr * 100), # amount in paise
		'currency': 'INR',
		'payment_capture': 1,
		'notes': {
			'appointment_id': patient_appointment.name,
			'patient_id': member_id
		}
	}
	
	order = client.order.create(data=order_data)
	
	return {
		"success": True,
		"order_id": order.get('id'),
		"key_id": frappe.conf.get("razorpay_key_id")
	}

@frappe.whitelist(allow_guest=True)
def payment_verify(razorpay_payment_id, razorpay_order_id, razorpay_signature, appointment_id):
	"""
	Verifies the Razorpay signature, creates Sales Invoice and updates status.
	"""
	client = get_razorpay_client()
	
	try:
		# 1. Verify Signature
		client.utility.verify_payment_signature({
			'razorpay_order_id': razorpay_order_id,
			'razorpay_payment_id': razorpay_payment_id,
			'razorpay_signature': razorpay_signature
		})
		
		# Signature is valid. Elevate privileges to create accounting ledgers.
		frappe.flags.ignore_permissions = True
		
		appointment = frappe.get_doc("Patient Appointment", appointment_id)
		
		# Find the linked customer (Assuming Patient links to Customer)
		customer = frappe.db.get_value("Patient", appointment.patient, "customer") 
		if not customer:
			# Fallback if no direct customer link on Patient
			customer = frappe.db.get_value("Customer", {"customer_name": appointment.patient})
		
		company = frappe.db.get_single_value('Global Defaults', 'default_company')
		if not company:
			company = frappe.get_all("Company", limit=1)[0].name
		
		# 2. Create the Sales Invoice directly
		sales_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"customer": customer or appointment.patient, 
			"company": company,
			"items": [{
				"item_code": "Teleconsultation",
				"qty": 1,
				"rate": float(appointment.consultation_fee or 0),
			}]
		})
		sales_invoice.insert(ignore_permissions=True)
		sales_invoice.submit()
		
		# 3. Create the Payment Entry to mark the Invoice as Paid
		payment = frappe.get_doc({
			"doctype": "Payment Entry",
			"payment_type": "Receive",
			"party_type": "Customer",
			"party": sales_invoice.customer,
			"paid_amount": sales_invoice.grand_total,
			"received_amount": sales_invoice.grand_total,
			"reference_no": razorpay_payment_id,
			"reference_date": frappe.utils.today(),
			"references": [{
				"reference_doctype": "Sales Invoice",
				"reference_name": sales_invoice.name,
				"allocated_amount": sales_invoice.grand_total
			}]
		})
		payment.insert(ignore_permissions=True)
		payment.submit()
		
		# 4. Confirm the Appointment
		frappe.db.set_value("Patient Appointment", appointment.name, "status", "Scheduled")
		
		frappe.db.commit()
		frappe.flags.ignore_permissions = False
		
		return {"success": True, "message": "Payment verified successfully", "redirect_url": "/payment-success"}
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Razorpay Signature Verification Failed")
		return {"success": False, "message": "Payment verification failed", "redirect_url": "/payment-failure"}

@frappe.whitelist(allow_guest=True)
def create_payment_link(sales_order_id):
	"""
	Replaces create_payment_link()
	"""
	return f"/payment?sales_invoice={sales_order_id}"
