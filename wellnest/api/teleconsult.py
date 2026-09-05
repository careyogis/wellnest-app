import time                                                                                                                                          
import frappe                                                                                                                                        
from frappe.utils import today                                                                                                                        
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
																																						
	# 2. Return the appointment details to the Flutter app                                                                                            
	return {                                                                                                                                          
		"name": appointment.name                                                                                                                      
	}
