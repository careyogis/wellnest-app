import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime

class AppNotification(Document):
	def on_update(self):
		self.check_and_send_push()

	def after_insert(self):
		self.check_and_send_push()

	def check_and_send_push(self):
		if self.send_push_notification and not self.push_sent:
			# get_datetime() can return the raw string if the value is not a
			# recognised datetime format (e.g. a bare date "2026-09-04" from the
			# desk form).  Always parse through frappe.utils.get_datetime() and
			# handle the case where it comes back as a string gracefully.
			scheduled = None
			if self.scheduled_time:
				try:
					scheduled = get_datetime(self.scheduled_time)
				except Exception:
					frappe.log_error(frappe.get_traceback(), f"Invalid scheduled_time on AppNotification {self.name}")
					scheduled = None

			if not scheduled or scheduled <= now_datetime():
				frappe.enqueue(
					"wellnest.health.doctype.app_notification.app_notification.send_fcm_push",
					queue="default",
					# Idempotent job_id prevents duplicate jobs when the doc is
					# re-saved before the worker has a chance to run.
					job_id=f"fcm_push_{self.name}",
					notification_name=self.name,
				)

def create_consultation_cancellation_notification(appointment, doctor_name):
	scheduled_time = get_datetime(appointment.scheduled_time)

	app_notification = frappe.get_doc({
        "doctype": "App Notification",
        "title": "Consultation Cancelled",
        "body": (
            f"Your consultation with {doctor_name} scheduled for "
            f"{scheduled_time.strftime('%d-%m-%Y %I:%M %p')} "
            f"has been cancelled by the doctor."
        ),
        "target_audience": "Specific Patient",
        "patient": appointment.patient,
        "scheduled_time": now_datetime(),
        "send_push_notification": 1,
	})

	app_notification.insert(ignore_permissions=True)

def send_fcm_push(notification_name):
	doc = frappe.get_doc("App Notification", notification_name)
	if doc.push_sent:
		return

	try:
		from wellnest.api.auth import _get_customer_firebase_app
		from firebase_admin import messaging
		from firebase_admin.exceptions import NotFoundError as FCMNotFoundError

		app = _get_customer_firebase_app()

		notification = messaging.Notification(
			title=doc.title,
			body=doc.body,
			image=doc.image if doc.image else None,
		)

		data = {
			"notification_name": str(doc.name),
			"action_type": str(doc.action_type or "None"),
			"action_url": str(doc.action_url or ""),
		}

		# Platform-specific sound configuration
		android_config = messaging.AndroidConfig(
			notification=messaging.AndroidNotification(
				default_sound=True,
			)
		)
		apns_config = messaging.APNSConfig(
			payload=messaging.APNSPayload(
				aps=messaging.Aps(sound="default")
			)
		)

		if doc.target_audience == "Global Broadcast":
			message = messaging.Message(
				notification=notification,
				data=data,
				topic="all_users",
				android=android_config,
				apns=apns_config,
			)
			messaging.send(message, app=app)

			# Mark as sent
			frappe.db.set_value("App Notification", doc.name, "push_sent", 1)

		elif doc.target_audience == "Specific Patient" and doc.patient:
			customer = frappe.db.get_value("Patient", doc.patient, "customer")
			if customer:
				contact_name = frappe.db.get_value(
					"Dynamic Link",
					{"link_doctype": "Customer", "link_name": customer, "parenttype": "Contact"},
					"parent"
				)
				if contact_name:
					token = frappe.db.get_value("Contact", contact_name, "custom_fcm_token")
					if token:
						message = messaging.Message(
							notification=notification,
							data=data,
							token=token,
							android=android_config,
							apns=apns_config,
						)
						try:
							messaging.send(message, app=app)
						except FCMNotFoundError:
							# Token is no longer registered on the device; clear it so
							# future sends aren't wasted on a dead registration.
							frappe.db.set_value("Contact", contact_name, "custom_fcm_token", None)
							frappe.logger().warning(
								f"Cleared stale FCM token for contact {contact_name} (patient {doc.patient})"
							)
							return

						# Mark as sent
						frappe.db.set_value("App Notification", doc.name, "push_sent", 1)
					else:
						frappe.logger().info(f"No FCM token for patient {doc.patient}")

	except Exception as e:
		frappe.log_error(f"FCM Push failed: {str(e)}", "App Notification Push")

def send_scheduled_pushes():
	"""Called by Frappe Scheduler (every ~5 min) to dispatch pending notifications.

	Uses raw SQL so that both NULL and past scheduled_time values are picked up.
	Each job carries an idempotent job_id so RQ silently drops duplicate enqueues
	— this prevents the queue from growing unboundedly across repeated scheduler
	ticks while a notification is still waiting for a worker.
	"""
	pending_notifications = frappe.db.sql(
		"""
		SELECT name
		FROM `tabApp Notification`
		WHERE send_push_notification = 1
		  AND push_sent = 0
		  AND (scheduled_time IS NULL OR scheduled_time <= %(now)s)
		""",
		{"now": now_datetime()},
		as_dict=True,
	)

	for notif in pending_notifications:
		frappe.enqueue(
			"wellnest.health.doctype.app_notification.app_notification.send_fcm_push",
			queue="default",
			# Idempotent: RQ drops this silently if the job is already queued or
			# running, preventing the queue from accumulating duplicate entries.
			job_id=f"fcm_push_{notif.name}",
			notification_name=notif.name,
		)
