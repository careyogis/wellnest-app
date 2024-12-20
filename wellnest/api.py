import frappe  # type: ignore
from datetime import datetime, date
from .utils.sms_service import send_otp_using_twilio, verify_otp_for_phone 

from datetime import datetime, date, timezone
import pytz

@frappe.whitelist()
def dashboard():
    caregivers = frappe.db.get_list( "Caregiver", fields=["*"], filters={"user_id": frappe.session.user} ) 
    
    if caregivers: 
        caregiver = caregivers[0] 
    else: 
        caregiver = None # couldn't find caregiver for the logged-in user

    if caregiver is None:
        return {"message": "No data to display for you"}

    engagementEdges = frappe.get_all(
        "Engagement Caregiver",
        fields=["*"],
        filters={"caregiver": caregiver.name},
    )

    engagementIds = list(set([edge["parent"] for edge in engagementEdges]))

    todayDateString = date.today()

    engagements = []
    for engagementId in engagementIds:
        engagement = frappe.get_doc("Engagement", engagementId)

        # Checking for active engagements by comparing today to the start and end dates
        if (engagement.start_date > todayDateString) or (engagement.end_date and todayDateString > engagement.end_date):
            continue

        for assignedCaregiver in engagement.assigned_caregivers:
            # Skip caregivers that do not match the given caregiver name
            if assignedCaregiver.caregiver != caregiver.name:
                continue

            # Skip caregivers who are not currently active(based on start and end dates)
            if (not assignedCaregiver.start_date or assignedCaregiver.start_date > todayDateString or (assignedCaregiver.end_date and todayDateString > assignedCaregiver.end_date)):
                continue

            checkinsToday = frappe.get_list(
                "Engagement Daily Record",
                fields=["*"],
                filters=[
                    ["engagement", "=", engagement.name],
                    ["creation", "between", [todayDateString, todayDateString]],
                ],
            )

            engagements.append(
                {
                    "engagement": engagement,
                    "customer": frappe.get_doc("Customer", engagement.customer),
                    "todaysCheckin": (
                        checkinsToday[0] if len(checkinsToday) > 0 else None
                    ),
                    "caregiverStartDate": assignedCaregiver.start_date,
                    "caregiverEndDate": assignedCaregiver.end_date,
                }
            )

    return {
        "caregiver": caregiver,
        "engagements": engagements,
    }


@frappe.whitelist()
def profile():
    caregiver = frappe.db.get_list(
        "Caregiver", filters={"user_id": frappe.session.user}
    )
    
    caregiver_data = frappe.get_doc("Caregiver", caregiver[0].name)
    
    # Get customer data for profile pic for Ratings Tab
    customers = []
    for rating in caregiver_data.ratings:
        customers.append(frappe.get_doc("Customer", rating.rater))

    # If Caregiver is Solo and not from an Agency
    if caregiver_data[0].supplier:
        agency = frappe.get_doc("Supplier", caregiver_data[0].supplier)
        agency_contact = frappe.get_doc("Address", agency.supplier_primary_address)
        return {
            "caregiver": caregiver_data,
            "agency_data": agency,
            "agency_contact": agency_contact,
            "customers": customers,
        }
    else:
        return {
            "caregiver": caregiver_data,
            "customers": customers,
        }


@frappe.whitelist()
def activity(dailyRecordId):
    engagementDailyRecord = frappe.get_doc("Engagement Daily Record", dailyRecordId)

    engagement = frappe.get_doc("Engagement", engagementDailyRecord.engagement)

    customer = frappe.get_doc("Customer", engagement.customer)

    return {
        "customerDoc": customer,
        "engagementRecord": engagementDailyRecord,
    }


@frappe.whitelist()
def setActivityData(taskName, data, time):
    ist_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    ist_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if time == "default":
        inputTime = str(ist_date) + " " + str(ist_time)
    else:
        inputTime = str(ist_date) + " " + time 

    frappe.db.set_value(
        "Engagement Daily Activity",
        taskName,
        {
            "activity_data": data,
            "completion_time": inputTime,
        },
    )
    return time if time != "default" else ist_time

# @frappe.whitelist()
# def setActivityCompletionTime(taskName, time):
#     frappe.db.set_value(
#         "Engagement Daily Activity",
#         taskName,
#         {
#             "completion_time": time,
#         },
#     )


@frappe.whitelist()
def setFilePath(taskName, fileURL):
    frappe.db.set_value(
        "Engagement Daily Activity",
        taskName,
        {
            "proof": fileURL,
        },
    )
    return fileURL


@frappe.whitelist()
def createDailyRecord(engagement, caregiver):
    ist_datetime = str(datetime.now(pytz.timezone('Asia/Kolkata')).date()) + " " + str(datetime.now(pytz.timezone('Asia/Kolkata')).time())
    # fetch activities data from engagement
    required_activities = frappe.get_doc("Engagement", engagement).required_activity
    # create a new document
    new_doc = frappe.get_doc(
        {
            "doctype": "Engagement Daily Record",
            "engagement": engagement,
            "caregiver": caregiver,
            "check_in_date_and_time": ist_datetime,
        }
    )
    for activity in required_activities:
        new_doc.append(
            "performed_activities",
            {
                "activity": activity.activity,
                "prescribed_time": activity.prescribed_time,
                "notes": activity.notes,
            },
        )
    new_doc.insert()
    return new_doc

@frappe.whitelist()
def checkout(record):
    ist_datetime = str(datetime.now(pytz.timezone('Asia/Kolkata')).date()) + " " + str(datetime.now(pytz.timezone('Asia/Kolkata')).time())
    frappe.db.set_value(
        "Engagement Daily Record",
        record,
        {
            "check_out_date_and_time": ist_datetime,
        },
    )

@frappe.whitelist()
def get_customer_for_user(user):
    # This API returns the Customer which the given User is associated withi.
    # Can be used by external apps (like phone app) to get customer for the logged in user
    contact = frappe.get_all('Contact', fields=['name'], filters = {'user' : user})

    customerDocs = list()
    if (contact is None or len(contact) == 0):
        return customerDocs
    
    customers = frappe.db.get_values("Dynamic Link", {
        'parent' : contact[0].name,
        'parenttype' : 'Contact',
        'link_doctype' : 'Customer',
    }, "link_name as name", as_dict=True)

    # if no customer found associated for the contact, return
    if (customers is None or len(customers) == 0):
        return customerDocs
    
    for customer in customers:        
        customerDocs.append (frappe.get_doc("Customer", customers[0].name))
    
    return customerDocs


@frappe.whitelist(allow_guest=True)
def generate_otp(phone):
    payload = {
                "success": False,
                "message": "No user found with this number",
            }

    # Check if a user exists with this phone number
    try:        
        user = frappe.db.get("User", {"mobile_no": phone})
    except Exception as e:
        payload["message"] = e

    if (user is None):
        return payload    

    # if user exists with this phone number, then send an OTP to this number
    send_otp_using_twilio(phone)

    payload["message"] = "OTP has been sent on: " + phone
    payload["success"] = True


    return payload


@frappe.whitelist(allow_guest=True)
def verify_otp(phone, otp):
    # the following method verifies if the OTP is correct
    # if yes, logs in the user and returns the user 
    return verify_otp_for_phone(phone, otp)
