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
def book_appointment(practitioner, patient, customer, scheduled_time, consultation_type, consultation_fee):                                           
	"""                                                                                                                                               
	Creates a Patient Appointment and a corresponding Sales Order.                                                                                    
	Stamps the Sales Order ID on the Patient Appointment.                                                                                             
	"""                                                                                                                                               
	# 1. Create Patient Appointment                                                                                                                   
	appointment = frappe.get_doc({                                                                                                                    
		"doctype": "Patient Appointment",                                                                                                             
		"practitioner": practitioner,                                                                                                                 
		"patient": patient,                                                                                                                           
		"scheduled_time": scheduled_time,                                                                                                             
		"appointment_type": consultation_type, # Or "consultation_type" depending on your field name
		"consultation_fee": consultation_fee,
	})                                                                                                                                                
	appointment.insert(ignore_permissions=True)                                                                                                       
																																						
	# 2. Get Default Company (Required for Sales Order)                                                                                               
	company = frappe.db.get_single_value('Global Defaults', 'default_company')                                                                        
	if not company:                                                                                                                                   
		company = frappe.get_all("Company", limit=1)[0].name                                                                                          
																																						
	# 3. Create the Sales Order                                                                                                                       
	sales_order = frappe.get_doc({                                                                                                                    
		"doctype": "Sales Order",                                                                                                                     
		"customer": customer,                                                                                                                         
		"company": company,                                                                                                                           
		"transaction_date": today(),                                                                                                                  
		"delivery_date": today(),                                                                                                                     
		"order_type": "Sales",                                                                                                                        
		"items": [                                                                                                                                    
			{                                                                                                                                         
				# IMPORTANT: Replace "Teleconsultation" with your actual Service Item Code from ERPNext                                               
				"item_code": "Teleconsultation",                                                                                                      
				"qty": 1,                                                                                                                             
				"rate": float(consultation_fee),                                                                                                      
			}                                                                                                                                         
		]                                                                                                                                             
	})                                                                            
																																						
	# Save and submit the Sales Order                                                                                                    
	sales_order.insert(ignore_permissions=True)                                                                                                       
	sales_order.submit()                                                                     

	# 4. Stamp the Sales Order on the Patient Appointment                                                                                             
	frappe.db.set_value("Patient Appointment", appointment.name, "sales_order", sales_order.name)                                              
																																						
	# 5. Return the appointment details to the Flutter app                                                                                            
	return {                                                                                                                                          
		"name": appointment.name                                                                                                                      
	}
