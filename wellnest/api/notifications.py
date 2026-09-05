import frappe
import requests
from frappe.utils import now_datetime
from frappe.utils import get_site_name

@frappe.whitelist(allow_guest=False)
def get_app_notifications(patient_id):
	now = now_datetime()
	
	# Fetch Global
	global_notifs = frappe.get_all(
		"App Notification",
		filters={
			"target_audience": "Global Broadcast",
			"scheduled_time": ["<=", now]
		},
		fields=["name", "title", "body", "action_type", "action_url", "creation"],
		order_by="creation desc",
		limit=20
	)

	# Fetch Specific
	specific_notifs = frappe.get_all(
		"App Notification",
		filters={
			"target_audience": "Specific Patient",
			"patient": patient_id,
			"scheduled_time": ["<=", now]
		},
		fields=["name", "title", "body", "action_type", "action_url", "creation"],
		order_by="creation desc",
		limit=20
	)

	all_notifs = global_notifs + specific_notifs
	# Sort by creation descending
	all_notifs.sort(key=lambda x: x["creation"], reverse=True)
	
	return all_notifs[:30]


def send_doctor_whatsapp_alert():
	from frappe.utils import now_datetime
	from datetime import timedelta

	minutes_before = frappe.conf.get('DOCTOR_REMINDER_MINUTES_BEFORE') or 10  # Set the time before the appointment to send the alert

	_logInfo(f"Initiating WhatsApp alerts to the doctors")

	try:
		all_upcoming_appointments = frappe.get_all(
			"Patient Appointment",
			filters={
				"status": "Scheduled",
				"scheduled_time": [">=", now_datetime()],
				"scheduled_time": ["<=", now_datetime() + timedelta(minutes=minutes_before)],
			},
			fields=["name", "practitioner", "patient", "scheduled_time", "consultation_type", "main_complaints"],
			ignore_permissions=True,
		)

		for appointment in all_upcoming_appointments:
			doctor = frappe.get_doc("Practitioner", appointment.practitioner)
			patient = frappe.get_doc("Patient", appointment.patient)
			doctor_phone = doctor.mobile
			if not doctor_phone:
				frappe.log_error(f"Doctor {doctor.name} does not have a mobile number. Cannot send WhatsApp alert.", "Doctor WhatsApp Alert Error")
				continue

			if not doctor_phone.startswith("+91"):
				doctor_phone = "+91" + doctor_phone
							
			doctor_name = doctor.full_name
			patient_name = patient.full_name
			age = now_datetime().year - patient.date_of_birth.year if patient.date_of_birth else "N/A"
			reason = appointment.main_complaints or "N/A"
			time = appointment.scheduled_time.strftime("%I:%M %p")
			mode = appointment.consultation_type
			appointment_id = appointment.name
			_send_whatsapp_message(doctor_phone, doctor_name, patient_name, age, reason, time, mode, appointment_id)
	except Exception as exp:
		frappe.log_error("Error Occurred while sending WhatsApp alert to doctors", str(exp))
		_logInfo(f"Check the error: {str(exp)}")

	_logInfo(f"Finished sending WhatsApp alerts")


def _send_whatsapp_message(doctor_phone, doctor_name, patient_name, age, reason, time, mode, appointment_id):	
	import requests

	_logInfo(f"Sending WhatsApp message to {doctor_name} ({doctor_phone}) for appointment {appointment_id} with patient {patient_name}, Aged {age}, Reason: {reason}, Time: {time}, Mode: {mode}")

	access_token = frappe.conf.get('ACCESS_TOKEN')
	phone_number_id = frappe.conf.get('PHONE_NUMBER_ID')
	version = frappe.conf.get('VERSION')
	site_url = frappe.utils.get_url()


	url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"

	headers = {
		"Authorization": f"Bearer {access_token}",
		"Content-Type": "application/json"
	}

	payload = {
        "messaging_product": "whatsapp",
        "to": doctor_phone,
        "type": "template",
        "template": {
            "name": "doctor_video_consultation_reminder_today",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": doctor_name},
                        {"type": "text", "text": patient_name},
                        {"type": "text", "text": age},
                        {"type": "text", "text": reason},
                        {"type": "text", "text": time},
                        {"type": "text", "text": mode},
                        {"type": "text", "text": f"{site_url}/doctor-app/consultations/{appointment_id}"}
                    ]
                }
            ]
        }
	}

	response = requests.post(url, json=payload, headers=headers)
	return response.json()

def _logInfo(message):
	import logging

	# Initialize a custom logger for your app or module
	logger = frappe.logger("Health", allow_site=True, file_count=5, max_size=250000)

	# Explicitly set the logging level to INFO
	logger.setLevel(logging.INFO)

	# Log your info message
	logger.info(message)