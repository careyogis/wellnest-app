#from flask import Flask, request, jsonify
#import os
import requests
import frappe
import json

#from messageHelper import sendMessage

# app = Flask(__name__)
# If using dotenv to load environment variables, uncomment the line below
# from dotenv import load_dotenv
# load_dotenv()

def build_template_message(to, requirement, location, condition, responsibility, responseUrl):
    return {
        "messaging_product": "whatsapp",
        "preview_url": False,
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": "lead_broacast_supplier_form",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": requirement},
                        {"type": "text", "text": location},
                        {"type": "text", "text": condition},
                        {"type": "text", "text": responsibility},
                        {"type": "text", "text": responseUrl},
                    ],
                }
            ],
        },
    }

# @app.route('/', methods=['POST'])
def broadcast_message(data):
    # data = request.get_json()
    requirement = data.get('requirement')
    location = data.get('location')
    condition = data.get('condition')
    responsibility = data.get('responsibility')
    phone_numbers = data.get('phoneNumbers')
    response_urls = data.get('responseUrls')
    
    request_data = {
        "requirements": {
            "requirement": requirement,
            "location": location,
            "condition": condition,
            "responsibility": responsibility,
        },
        "phoneNumbers": phone_numbers
    }

    try:
        # for phone in phone_numbers:
        for i in range(len(phone_numbers)):
            phone = phone_numbers[i]
            response_url = response_urls[i]
            template_msg = build_template_message(phone, requirement, location, condition, responsibility, response_url)
            if template_msg:
                send_message(template_msg)
    except Exception as error:
        return {"error": str(error)}

    return {"message": "Broadcast sent successfully"}

# if __name__ == '__main__':
#     app.run(debug=True)

def send_message(message):
    url = f"https://graph.facebook.com/{frappe.conf.get('VERSION')}/{frappe.conf.get('PHONE_NUMBER_ID')}/messages"
    headers = {
        'Authorization': f"Bearer {frappe.conf.get('ACCESS_TOKEN')}",
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=message, headers=headers)
    return response.json()