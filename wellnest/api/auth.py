import frappe
import requests
import json
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

IDENTITY_TOOLKIT_BASE = "https://identitytoolkit.googleapis.com/v1"

_firebase_app = None


def _get_firebase_app():
	global _firebase_app
	if _firebase_app is None:
		service_account_path = frappe.conf.get("firebase_service_account_path")
		if not service_account_path:
			frappe.throw("firebase_service_account_path not set in site config")
		cred = credentials.Certificate(service_account_path)
		_firebase_app = firebase_admin.initialize_app(cred)
	return _firebase_app


def _get_firebase_web_api_key():
	api_key = frappe.conf.get("firebase_web_api_key")
	if not api_key:
		frappe.throw("firebase_web_api_key not set in site config")
	return api_key


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


@frappe.whitelist(allow_guest=True)
def verify_otp_and_login(session_info: str, code: str):
	"""
	Verifies Firebase OTP and logs user into Frappe atomically in one request.
	"""
	if not session_info or not code:
		frappe.throw("session_info and code are required")

	api_key = _get_firebase_web_api_key()
	url = f"{IDENTITY_TOOLKIT_BASE}/accounts:signInWithPhoneNumber?key={api_key}"
	payload = {"sessionInfo": session_info, "code": code}

	resp = requests.post(url, json=payload, timeout=15)
	data = resp.json()

	if resp.status_code != 200:
		error_message = data.get("error", {}).get("message", "UNKNOWN_ERROR")
		frappe.log_error(
			title="Firebase signInWithPhoneNumber failed", message=frappe.as_json(data)
		)
		frappe.throw(f"Invalid OTP: {error_message}")

	uid = data["localId"]
	phone_number = data.get("phoneNumber")
	is_new_user = data.get("isNewUser", False)

	lookup_phone = phone_number
	if lookup_phone and lookup_phone.startswith("+91"):
		lookup_phone = lookup_phone[3:]

	# Find user by full phone number or 10-digit mobile_no
	user = frappe.db.get_value("User", {"mobile_no": phone_number}, "name")
	if not user and lookup_phone:
		user = frappe.db.get_value("User", {"mobile_no": lookup_phone}, "name")

	if not user:
		frappe.throw("User not found for this mobile number")

	# Perform Frappe login
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

	# Check whether the email is already registered
	if frappe.db.exists("User", {"email": email}):
		frappe.throw("An account with this email already exists")

	lookup_mobile = mobile
	if lookup_mobile.startswith("+91"):
		lookup_mobile = lookup_mobile[3:]

	existing_user = frappe.db.get_value(
		"User",
		{"mobile_no": lookup_mobile},
		"name",
	)

	if not existing_user:
		existing_user = frappe.db.get_value(
			"User",
			{"mobile_no": "+91" + lookup_mobile},
			"name",
		)

	if existing_user:
		frappe.throw("An account with this mobile number already exists")

	# Create the Frappe User
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


	# Create an empty Practitioner linked to the newly created User
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

	frappe.db.commit()

	return {
		"success": True,
		"user": user.name,
		"practitioner": practitioner.name,
		"mobile": lookup_mobile,
	}