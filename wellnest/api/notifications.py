import frappe
from frappe.utils import now_datetime

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
