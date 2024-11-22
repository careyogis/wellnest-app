import frappe
import string
import random
import requests

from twilio.rest import Client

REDIS_PREFIX = "otp"

def random_string_generator(str_size, allowed_chars):
    return "".join(random.choice(allowed_chars) for x in range(str_size))

def send_otp_using_twilio(to_phone):

    # Your Account SID and Auth Token from twilio.com/console
    account_sid = '[asscount_sid copied from twilio service]'
    auth_token = '[auth_token copied from twilio service]'
    client = Client(account_sid, auth_token)

    # Your Twilio phone number and the recipient's phone number
    twilio_phone_number = '[from number]'

    # The message you want to send
    message_body = 'Hello from Twilio!'

    # Sending the SMS
    message = client.messages.create(
        body=message_body,
        from_=twilio_phone_number,
        to=to_phone
    )

    print(f"Message sent with SID: {message.sid}")


def send_sms(phone, otp, domain):
    # Strip out + when sending SMS
    phone = phone.replace("+", "")
    url = "https://control.msg91.com/api/v5/flow/"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": frappe.conf["msg91_authkey"],
    }
    payload = {
        "template_id": frappe.conf["msg91_template_id"],
        "sender": frappe.conf.get("msg91_sender_id") or "IoTRDY",
        "short_url": "0",
        "mobiles": phone,
        "var1": domain,
        "var2": otp,
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def generate_otp_for_phone(phone, domain):
    payload = {
        "success": False,
        "message": None,
    }
    if phone[0] != "+":
        phone = f"+91{phone}"  # Set India as default
    otp = random_string_generator(4, string.digits)
    frappe.cache().set(f"{REDIS_PREFIX}:{phone}", otp, ex=300)
    try:
        send_sms(phone=phone, otp=otp, domain=domain)
        payload["success"] = True
        payload["message"] = f"OTP sent by SMS sent to {phone}"
    except Exception as e:
        print(str(e))
        payload["message"] = str(e)
    return payload


def verify_otp_for_phone(phone, otp):
    payload = {
        "success": False,
        "message": None,
    }
    if phone[0] != "+":
        phone = f"+91{phone}"  # Set India as default
    key = f"{REDIS_PREFIX}:{phone}"
    stored_otp = frappe.cache().get(key).decode("utf-8")
    if not stored_otp == otp:
        payload["message"] = "Incorrect OTP."
        return payload

    try:
        user = frappe.db.get("User", {"mobile_no": phone})
    except Exception as e:
        payload["message"] = "User not found."
        return payload

    # Delete stored OTP
    frappe.cache().delete_key(key)

    # Now log in as user
    from frappe.auth import CookieManager, LoginManager

    frappe.utils.set_request(path="/")
    frappe.local.cookie_manager = CookieManager()
    frappe.local.login_manager = LoginManager()
    return frappe.local.login_manager.login_as(user.name)