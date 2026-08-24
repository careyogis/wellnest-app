import frappe
import requests
import json
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

IDENTITY_TOOLKIT_BASE = "https://identitytoolkit.googleapis.com/v1"

_firebase_app = None
_customer_firebase_app = None

@frappe.whitelist(allow_guest=True)
def send_otp(phone: str, recaptcha_token: str):
	if not phone or not recaptcha_token:
		frappe.throw("phone and recaptcha_token are required")

	lookup_phone = phone
	if lookup_phone.startswith("+91"):
		lookup_phone = lookup_phone[3:]

	practitioner = frappe.db.get_value(
		"Practitioner", {"mobile": lookup_phone}, "name"
	)

	if not practitioner:
		frappe.throw("No doctor found with this number")

	return _send_firebase_otp(phone, recaptcha_token)

@frappe.whitelist(allow_guest=True)
def send_registration_otp(phone: str, recaptcha_token: str):
	if not phone or not recaptcha_token:
		frappe.throw("phone and recaptcha_token are required")

	# Check if the phone number is already registered
	lookup_phone = phone
	if lookup_phone.startswith("+91"):
		lookup_phone = lookup_phone[3:]

	practitioner = frappe.db.get_value(
		"Practitioner", {"mobile": lookup_phone}, "name"
	)

	if practitioner:
		frappe.throw("This phone is already registered.", frappe.DuplicateEntryError)

	return _send_firebase_otp(phone, recaptcha_token)

@frappe.whitelist(allow_guest=True)
def verify_otp_and_login(session_info: str, phone: str, otp: str):
	firebase_data = _verify_firebase_otp(session_info, otp)

	uid = firebase_data["uid"]
	phone_number = phone
	is_new_user = firebase_data["is_new_user"]

	lookup_phone = phone_number

	if lookup_phone and lookup_phone.startswith("+91"):
		lookup_phone = lookup_phone[3:]

	user = frappe.db.get_value(
		"User",
		{"mobile_no": phone_number},
		"name"
	)

	if not user and lookup_phone:
		user = frappe.db.get_value(
			"User",
			{"mobile_no": lookup_phone},
			"name"
		)

	if not user:
		frappe.throw("User not found for this mobile number")

	frappe.set_user(user)

	from frappe.auth import LoginManager

	login_manager = LoginManager()
	login_manager.user = user
	login_manager.post_login()

	_get_firebase_app()
	custom_token = firebase_auth.create_custom_token(uid)

	return {
		"success": True,
		"user": user,
		"custom_token": custom_token.decode("utf-8"),
		"uid": uid,
		"phone_number": phone_number,
		"is_new_user": is_new_user,
	}

@frappe.whitelist(allow_guest=True)
def verify_customer_firebase_token(id_token: str):
	customer_app = _get_customer_firebase_app()
	try:
		decoded_token = firebase_auth.verify_id_token(id_token, app=customer_app)
	except Exception as e:
		frappe.throw(f"Invalid Token: {str(e)}")

	phone_number = decoded_token.get("phone_number")
	if not phone_number:
		frappe.throw("Phone number not found in token")

	lookup_phone = phone_number
	if lookup_phone.startswith("+91"):
		lookup_phone = lookup_phone[3:]

	patient = frappe.db.get_value("Patient", {"mobile": lookup_phone}, ["name", "full_name", "customer"], as_dict=True)

	if not patient:
		return {"success": True, "needs_registration": True, "phone_number": phone_number}

	user = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
	if not user:
		user = frappe.db.get_value("User", {"mobile_no": lookup_phone}, "name")

	if not user:
		frappe.throw("User account not found. Contact support.")

	frappe.set_user(user)
	from frappe.auth import LoginManager
	login_manager = LoginManager()
	login_manager.user = user
	login_manager.post_login()

	frappe.db.set_value("Patient", patient.name, "is_phone_verified", 1)

	return {
		"success": True,
		"user": user,
		"full_name": patient.full_name,
		"customer": patient.customer,
		"patient": patient.name
	}

@frappe.whitelist(allow_guest=True)
def verify_registration_otp(
	session_info: str,
	code: str,
	first_name: str,
	last_name: str,
	email: str,
	mobile: str,
):
	firebase_data = _verify_firebase_otp(session_info, code)

	uid = firebase_data["uid"]
	phone_number = firebase_data["phone_number"]

	first_name = first_name.strip()
	last_name = last_name.strip()
	email = email.strip().lower()
	mobile = mobile.strip()

	if not first_name or not last_name or not email or not mobile:
		frappe.throw("Registration details are incomplete")

	lookup_mobile = mobile

	if lookup_mobile.startswith("+91"):
		lookup_mobile = lookup_mobile[3:]

	try:
		# manually starting transaction for multi-doctype updates 
		frappe.db.begin()
		user = frappe.get_doc(
			{
				"doctype": "User",
				"first_name": first_name,
				"last_name": last_name,
				"email": email,
				"mobile_no": lookup_mobile,
				"user_type": "Website User",
				"username": email,
				"roles": [{"role": "Doctor"}],
				"send_welcome_email": 1,
			}
		).insert(ignore_permissions=True)

		practitioner = frappe.get_doc(
			{
				"doctype": "Practitioner",
				"first_name": first_name,
				"last_name": last_name,
				"email": email,
				"mobile": lookup_mobile,
				"user_id": user.name,
				"title": "Dr.",
			}
		).insert(ignore_permissions=True)
	except frappe.ValidationError as e:
		frappe.db.rollback()
		frappe.log_error(
			title="Duplicate entry error while creating Practitioner/User account",
			message=frappe.as_json({"error": str(e), "email": email, "mobile": mobile}),
		)
		frappe.throw("Practitioner/user account with this email/mobile already exists. Please login instead.", frappe.DuplicateEntryError)
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(
			title="Error creating Practitioner/User account",
			message=frappe.as_json({"error": str(e), "email": email, "mobile": mobile}),
		)
		frappe.throw("Unexpected error creating user or practitioner. Please contact support.", frappe.DataError)
	else:
		frappe.db.commit()

	frappe.set_user(user.name)

	from frappe.auth import LoginManager

	login_manager = LoginManager()
	login_manager.user = user.name
	login_manager.post_login()

	_get_firebase_app()
	custom_token = firebase_auth.create_custom_token(uid)

	return {
		"success": True,
		"user": user.name,
		"practitioner": practitioner.name,
		"custom_token": custom_token.decode("utf-8"),
		"uid": uid,
		"phone_number": phone_number,
	}

@frappe.whitelist(allow_guest=True)
def register_customer(id_token: str, full_name: str):
	customer_app = _get_customer_firebase_app()
	try:
		decoded_token = firebase_auth.verify_id_token(id_token, app=customer_app)
	except Exception as e:
		frappe.throw(f"Invalid Token: {str(e)}")

	phone_number = decoded_token.get("phone_number")
	if not phone_number:
		frappe.throw("Phone number not found in token")

	lookup_phone = phone_number
	if lookup_phone.startswith("+91"):
		lookup_phone = lookup_phone[3:]

	if frappe.db.exists("Patient", {"mobile": lookup_phone}):
		frappe.throw("Patient already exists with this mobile number")

	# from frappe.utils.password import get_random_password

	email = f"{lookup_phone}@customer.careyogis.com"
	full_name = full_name.strip() if full_name else f"Customer-{lookup_phone}"
	first_name = full_name.split(" ")[0]
	last_name = " ".join(full_name.split(" ")[1:]) if len(full_name.split(" ")) > 1 else ""

	user_doc = frappe.get_doc({
		"doctype": "User",
		"email": email,
		"first_name": first_name,
		"last_name": last_name,
		"mobile_no": phone_number,
		# "new_password": get_random_password(),
		"send_welcome_email": 0,
		"user_type": "Website User"
	})
	user_doc.flags.ignore_permissions = True
	user_doc.insert()
	user_doc.add_roles("Customer")

	patient_doc = frappe.get_doc({
		"doctype": "Patient",
		"full_name": full_name,
		"mobile": lookup_phone,
		"is_phone_verified": 1
	})
	patient_doc.flags.ignore_permissions = True
	patient_doc.insert()

	frappe.db.commit()

	frappe.set_user(user_doc.name)
	from frappe.auth import LoginManager
	login_manager = LoginManager()
	login_manager.user = user_doc.name
	login_manager.post_login()

	return {
		"success": True,
		"user": user_doc.name,
		"full_name": full_name,
		"patient": patient_doc.name
	}

@frappe.whitelist(allow_guest=True)
def register_doctor(
	first_name: str,
	last_name: str,
	email: str,
	mobile: str,
):
	if not first_name or not last_name or not email or not mobile:
		frappe.throw("First name, last name, email and mobile number are required")

	first_name = first_name.strip()
	last_name = last_name.strip()
	email = email.strip().lower()
	mobile = mobile.strip()

	if not first_name or not last_name or not email or not mobile:
		frappe.throw("All registration fields are required")

	lookup_mobile = mobile
	if lookup_mobile.startswith("+91"):
		lookup_mobile = lookup_mobile[3:]

	return {
		"success": True,
		"first_name": first_name,
		"last_name": last_name,
		"email": email,
		"mobile": lookup_mobile,
	}


# Helper/private functions area
def _get_firebase_app():
	global _firebase_app
	if _firebase_app is None:
		service_account_path = frappe.conf.get("firebase_service_principal_cert_path")
		if not service_account_path:
			frappe.throw("firebase_service_principal_cert_path not set in site config")
		cred = credentials.Certificate(service_account_path)
		_firebase_app = firebase_admin.initialize_app(cred)
	return _firebase_app

def _get_customer_firebase_app():
	global _customer_firebase_app
	if _customer_firebase_app is None:
		service_account_path = frappe.conf.get("customer_firebase_service_principal_cert_path")
		if not service_account_path:
			frappe.throw("customer_firebase_service_principal_cert_path not set in site config")
		cred = credentials.Certificate(service_account_path)
		_customer_firebase_app = firebase_admin.initialize_app(cred, name="customer")
	return _customer_firebase_app

def _get_firebase_web_api_key():
	api_key = frappe.conf.get("firebase_web_api_key")
	if not api_key:
		frappe.throw("firebase_web_api_key not set in site config")
	return api_key

def _send_firebase_otp(phone: str, recaptcha_token: str):
	if not phone or not recaptcha_token:
		frappe.throw("phone and recaptcha_token are required")

	api_key = _get_firebase_web_api_key()
	url = f"{IDENTITY_TOOLKIT_BASE}/accounts:sendVerificationCode?key={api_key}"

	payload = {
		"phoneNumber": phone,
		"recaptchaToken": recaptcha_token,
	}

	resp = requests.post(url, json=payload, timeout=15)
	data = resp.json()

	if resp.status_code != 200:
		error_message = data.get("error", {}).get("message", "UNKNOWN_ERROR")

		frappe.log_error(
			title="Firebase sendVerificationCode failed",
			message=frappe.as_json(data),
		)

		frappe.throw(f"Failed to send OTP: {error_message}")

	return {
		"success": True,
		"session_info": data["sessionInfo"],
	}

def _verify_firebase_otp(session_info: str, code: str):
	if not session_info or not code:
		frappe.throw("session_info and code are required")

	api_key = _get_firebase_web_api_key()
	url = f"{IDENTITY_TOOLKIT_BASE}/accounts:signInWithPhoneNumber?key={api_key}"

	payload = {
		"sessionInfo": session_info,
		"code": code,
	}

	resp = requests.post(url, json=payload, timeout=15)
	data = resp.json()

	if resp.status_code != 200:
		error_message = data.get("error", {}).get("message", "UNKNOWN_ERROR")

		frappe.log_error(
			title="Firebase signInWithPhoneNumber failed",
			message=frappe.as_json(data),
		)

		frappe.throw(f"{error_message}", frappe.AuthenticationError)

	return {
		"uid": data["localId"],
		"phone_number": data.get("phoneNumber"),
		"is_new_user": data.get("isNewUser", False),
	}
