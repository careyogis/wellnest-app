# Facade init module for backward compatibility with existing Frappe whitelisted endpoints (wellnest.api.<fn>).
# Function implementations are organized by domain:
#   - Practitioner/Doctor: wellnest.health.doctype.practitioner.practitioner
#   - Caregiver: wellnest.wellnest.doctype.caregiver.caregiver
#   - Auth: wellnest.api.auth
#   - Payment: wellnest.api.payment
#   - Contact: wellnest.api.contact

from wellnest.health.doctype.practitioner.practitioner import (
	doctor_profile,
	update_doctor_profile,
	lookup_doctor,
)

from wellnest.wellnest.doctype.caregiver.caregiver import (
	calculate_time_window,
	dashboard,
	profile,
	activity,
	addActivityToDailyRecord,
	removeActivityFromDailyRecord,
	createDailyRecord,
	checkout,
	update_caregiver_response,
)

from wellnest.api.auth import (
	_get_firebase_app,
	_get_firebase_web_api_key,
	send_otp,
	verify_otp_and_login,
)

from wellnest.api.payment import (
	get_terms_content,
	accept_terms,
	get_payment_details,
)

from wellnest.api.contact import (
	contactUs,
	get_customer_for_user,
	update_fcm_token,
)

__all__ = [
	"doctor_profile",
	"update_doctor_profile",
	"lookup_doctor",
	"calculate_time_window",
	"dashboard",
	"profile",
	"activity",
	"addActivityToDailyRecord",
	"removeActivityFromDailyRecord",
	"createDailyRecord",
	"checkout",
	"update_caregiver_response",
	"send_otp",
	"verify_otp_and_login",
	"get_terms_content",
	"accept_terms",
	"get_payment_details",
	"contactUs",
	"get_customer_for_user",
	"update_fcm_token",
]
