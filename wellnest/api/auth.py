import frappe
import requests
import json
import random
import string
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
def login_with_phone(phone, otp_token):
	"""
	Logs a user into Frappe after Firebase OTP has already been verified.
	"""
	cached_token = frappe.cache().get_value(f"otp_verified_{phone}")
	if not cached_token or cached_token != otp_token:
		frappe.throw("Invalid or expired OTP verification")

	user = frappe.db.get_value("User", {"mobile_no": phone}, "name")

	if not user:
		frappe.throw("User not found")

	frappe.set_user(user)

	from frappe.auth import LoginManager

	login_manager = LoginManager()
	login_manager.user = user
	login_manager.post_login()

	frappe.cache().delete_value(f"otp_verified_{phone}")

	return {"success": True, "user": user}


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
def verify_otp(session_info: str, code: str):
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

	_get_firebase_app()
	custom_token = firebase_auth.create_custom_token(uid)

	otp_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
	lookup_phone = phone_number
	if lookup_phone and lookup_phone.startswith("+91"):
		lookup_phone = lookup_phone[3:]
	frappe.cache().set_value(
		f"otp_verified_{lookup_phone}", otp_token, expires_in_sec=300
	)

	return {
		"success": True,
		"custom_token": custom_token.decode("utf-8"),
		"uid": uid,
		"phone_number": phone_number,
		"is_new_user": is_new_user,
		"otp_token": otp_token,
	}
