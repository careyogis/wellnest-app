import time                                                                                                                                          
import frappe                                                                                                                                        
from agora_token_builder import RtcTokenBuilder                                                                                                      
																																						
@frappe.whitelist()                                                                                                                                  
def get_agora_token(channel_name, uid=1001, role="publisher"):                                                                                       
	# Store certificate in site_config.json                                                                                                          
	app_id = frappe.conf.get("agora_app_id") or "ecf9c8b7c88243f6bb988fafdf3dda44"
	app_cert = frappe.conf.get("agora_app_certificate") or "a073d34bbd5748888e1ba7aea9c00229"

	if not app_cert:                                                                                                                                 
		# If testing mode (certificate disabled in Agora Console)                                                                                    
		return {"rtcToken": ""}                                                                                                                      

	# 15 mins expiry                                                                                                                                  
	privilege_expired_ts = int(time.time()) + 900                                                     
	role_type = 1 if role == "publisher" else 2                                                                                                      
																																						
	token = RtcTokenBuilder.buildTokenWithUid(                                                                                                       
		app_id, app_cert, channel_name, int(uid), role_type, privilege_expired_ts                                                                    
	)                                                                                                                                                
	return {"rtcToken": token}      