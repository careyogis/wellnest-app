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
			if not self.scheduled_time or get_datetime(self.scheduled_time) <= now_datetime():
				frappe.enqueue("wellnest.health.doctype.app_notification.app_notification.send_fcm_push", queue="short", notification_name=self.name)

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
				contact_name = frappe.db.get_value("Dynamic Link", {"link_doctype": "Customer", "link_name": customer, "parenttype": "Contact"}, "parent")
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
	"""Called by Frappe Scheduler to send pending notifications."""
	pending_notifications = frappe.get_all(
		"App Notification",
		filters={
			"send_push_notification": 1,
			"push_sent": 0,
			"scheduled_time": ["<=", now_datetime()]
		},
		fields=["name"]
	)
	
	for notif in pending_notifications:
		frappe.enqueue("wellnest.health.doctype.app_notification.app_notification.send_fcm_push", queue="short", notification_name=notif.name)
