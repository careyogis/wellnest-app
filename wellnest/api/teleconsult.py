import time                                                                                                                                          
import frappe
import frappe.utils
from agora_token_builder import RtcTokenBuilder                                                                                                      
																																						
@frappe.whitelist()                                                                                                                                  
def get_agora_token(channel_name, uid=1001, role="publisher"):                                                                                       
	# Store certificate in site_config.json                                                                                                          
	app_id = frappe.conf.get("agora_app_id")
	app_cert = frappe.conf.get("agora_app_certificate")

	if not app_cert:                                                                                                                                 
		# If testing mode (certificate disabled in Agora Console)                                                                                    
		return {"rtcToken": "", "appId": app_id}                                                                                                                      

	# 15 mins expiry                                                                                                                                  
	privilege_expired_ts = int(time.time()) + 900                                                     
	role_type = 1 if role == "publisher" else 2                                                                                                      
																																						
	token = RtcTokenBuilder.buildTokenWithUid(                                                                                                       
		app_id, app_cert, channel_name, int(uid), role_type, privilege_expired_ts                                                                    
	)                                                                                                                                                
	return {"rtcToken": token, "appId": app_id}      

                                                                                                                                                          
@frappe.whitelist()                                                                                                                                   
def book_appointment(practitioner, patient, scheduled_time, consultation_type, consultation_fee, main_complaints="Not provided"):
	"""                                                                                                                                               
	Creates a Patient Appointment in Unverified status.                                                                                    
	"""                                                                                                                                               
	# 1. Create Patient Appointment                                                                                                                   
	appointment = frappe.get_doc({                                                                                                                    
		"doctype": "Patient Appointment",                                                                                                             
		"practitioner": practitioner,                                                                                                                 
		"patient": patient,                                                                                                                           
		"scheduled_time": scheduled_time,                                                                                                             
		"appointment_type": consultation_type,
		"consultation_fee": consultation_fee,
		"main_complaints": main_complaints,
		"status": "Unverified"
	})                                                                                                                                                
	appointment.insert(ignore_permissions=True)                                                                                                       

	doctor_full_name = frappe.get_value("Practitioner", practitioner, "full_name")

	# 2. Schedule an App Notification
	app_notification = frappe.get_doc({                                                                                                                 
		"doctype": "App Notification",
		"title": "Upcoming doctor appointment",
		"body": f"You have an upcoming appointment with {doctor_full_name} at {appointment.scheduled_time}.",
		"target_audience": "Specific Patient",
		"patient": patient,
		"scheduled_time": (frappe.utils.add_to_date(scheduled_time, minutes=-15)),
	})                                                                                                                                                
	app_notification.insert(ignore_permissions=True)                                                                                                       
	frappe.db.commit()

	# 3. Return the appointment name  
	return {                                                                                                                                          
		"name": appointment.name                                                                                                                      
	}

@frappe.whitelist()
def report_doctor_noshow(appointment_id):
	"""                                         
	Updates the status of a Patient Appointment to 'No Show' and creates a support ticket for investigating.                                                  
	"""
	appointment = frappe.get_doc("Patient Appointment", appointment_id)
                     
	if appointment.status != "Scheduled":
		frappe.log_error(f"Customer reported 'No Show' for the appointmentId: {appointment_id}, but the status was {appointment.status}")
		return {"message": f"Appointment in {appointment.status} state cannot be marked as 'No Show'."}

	# Do not mark No Show till at least 15 mins passed the scheduled_time
	if frappe.utils.now_datetime() < frappe.utils.add_to_date(appointment.scheduled_time, minutes=15):
		frappe.log_error(f"Customer reported 'No Show' for the appointmentId: {appointment_id}, but inside 15 mins post the secheduled time of: {appointment.scheduled_time}")
		return {"message": f"Cannot mark appointment as 'No Show' until it is at least 15 minutes past the scheduled time of:{appointment.scheduled_time}"}	

	appointment.status = "No Show"                                                                                                                   
	appointment.save(ignore_permissions=True)                                                                                                         
																																		
	# Create an Issue for the support team to investigate
	issue = frappe.get_doc({
		"doctype": "Issue",
		"subject": f"Customer reported 'No Show' for appointment {appointment_id}",
		"description": f"The customer reported that the doctor: {appointment.practitioner} did not show up for the appointment with ID {appointment_id}. Please investigate.",
		"issue_type": "Service",
	})
	issue.insert(ignore_permissions=True)
																																					
	return {"message": "Appointment marked as 'No Show' and the support team have been notified."}
