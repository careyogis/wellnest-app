import frappe  # type: ignore
from datetime import datetime, date
from .utils.sms_service import send_otp_using_twilio, verify_otp_for_phone 

from datetime import datetime, date, timezone
import pytz

@frappe.whitelist()
def dashboard():
    caregiver = frappe.db.get_list(
        "Caregiver", fields=["*"], filters={"user_id": frappe.session.user}
    )[0]

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
                "todaysCheckin": checkinsToday[0] if len(checkinsToday) > 0 else None,
            }
        )

    return {
        "caregiver": caregiver,
        "engagements": engagements,
    }


@frappe.whitelist()
def profile():
    caregiver_name = frappe.db.get_list(
        "Caregiver", fields=["*"], filters={"user_id": frappe.session.user}
    )
    caregiver_data = frappe.get_doc("Caregiver", caregiver_name[0].name)

    # Get customer data for profile pic for Ratings Tab
    customer_data = []
    for rater in caregiver_data.rating:
        customer_data.append(frappe.get_doc("Customer", rater.rater))

    # If Caregiver is Solo and not from an Agency
    if caregiver_name[0].supplier:
        agency = frappe.get_doc("Supplier", caregiver_name[0].supplier)
        agency_contact = frappe.get_doc("Address", agency.supplier_primary_address)
        return {
            "caregiver_name": caregiver_name[0],
            "caregiver_data": caregiver_data,
            "agency_data": agency,
            "agency_contact": agency_contact,
            "customer_data": customer_data,
        }
    else:
        return {
            "caregiver_name": caregiver_name[0],
            "caregiver_data": caregiver_data,
            "customer_data": customer_data,
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
def setActivityData(taskName, data):
    ist_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    frappe.db.set_value(
        "Engagement Daily Activity",
        taskName,
        {
            "activity_data": data,
            "completion_time": ist_time,
        },
    )
    return ist_time

@frappe.whitelist()
def setActivityCompletionTime(taskName, time):
    frappe.db.set_value(
        "Engagement Daily Activity",
        taskName,
        {
            "completion_time": time,
        },
    )


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

    # existing_docs_of_other_caregivers = frappe.db.get_list('Engagement Daily Record', filters={'creation': ['>=', ist_datetime]})

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

    if (contact is None or len(contact) == 0):
        return
    
    customers = frappe.db.get_values("Dynamic Link", {
        'parent' : contact[0].name,
        'parenttype' : 'Contact',
        'link_doctype' : 'Customer',
    }, "link_name as name, link_title as customer_name", as_dict=True)            

    return customers


@frappe.whitelist(allow_guest=True)
def generate_otp(phone):
    payload = {
                "success": False,
                "message": None,
            }

    # Check if a user exists with this phone number
    try:        
        user = frappe.db.get("User", {"mobile_no": phone})
    except Exception as e:
        payload["message"] = "User not found."
        return payload

    return send_otp_using_twilio(phone)
    #return "Your OTP is: 8924"


@frappe.whitelist(allow_guest=True)
def verify_otp(phone, otp):
    # the following method verifies if the OTP is correct
    # if yes, logs in the user and returns the user 
    return verify_otp_for_phone(phone, otp)
