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

@frappe.whitelist()
def send_fcm_push(notification_name):
	doc = frappe.get_doc("App Notification", notification_name)
	if doc.push_sent:
		return

	try:
		from wellnest.api.auth import _get_customer_firebase_app
		from firebase_admin import messaging

		app = _get_customer_firebase_app()

		notification = messaging.Notification(
			title=doc.title,
			body=doc.body
		)

		data = {
			"action_type": str(doc.action_type or "None"),
			"action_url": str(doc.action_url or "")
		}

		if doc.target_audience == "Global Broadcast":
			message = messaging.Message(
				notification=notification,
				data=data,
				topic="all_users"
			)
			messaging.send(message, app=app)

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
							token=token
						)
						messaging.send(message, app=app)
					else:
						frappe.logger().info(f"No FCM token for patient {doc.patient}")

		# Mark as sent
		frappe.db.set_value("App Notification", doc.name, "push_sent", 1)
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
