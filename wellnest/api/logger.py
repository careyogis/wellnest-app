import frappe                                                                                                                                        


@frappe.whitelist()
def log_call_event(event, appointment_id, **kwargs):
	"""
	Log a teleconsultation call event emitted by the Flutter patient app.

	Called fire-and-forget from the client. Always returns success so
	network errors on the client side are never surfaced to the user.

	Supported events (non-exhaustive):
	  - patient_entered_waiting_room
	  - doctor_initiated_call
	  - patient_joined_rtc_channel
	  - doctor_joined_rtc_channel
	  - call_ended            (includes duration_seconds, doctor_joined)
	  - network_quality_degraded (includes quality level)

	Logs are written to <site>/logs/call_events.log via frappe.logger().
	"""
	import json

	logger = frappe.logger("call_events", allow_site=True, max_size=5, file_count=20)

	payload = {
		"event": event,
		"appointment_id": appointment_id,
		"user": frappe.session.user,
		"timestamp": frappe.utils.now(),
	}
	# Merge any extra metadata fields (duration_seconds, channel, remote_uid, etc.)
	payload.update({k: v for k, v in kwargs.items() if not k.startswith("_")})

	logger.info(json.dumps(payload, default=str))

	return {"status": "ok"}

