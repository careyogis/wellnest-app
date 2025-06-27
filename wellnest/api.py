import frappe  # type: ignore
from datetime import datetime, date, timedelta
from .utils.sms_service import send_otp_using_twilio, verify_otp_for_phone

from datetime import datetime, date, timezone
import pytz
import json



def calculate_time_window(daily_reporting_time_seconds):
    """
    Calculate start and end time windows based on a reporting time.
    Switches to next window immediately when previous window's end time is reached.

    Args:
        daily_reporting_time_seconds (int): Reporting time in seconds

    Returns:
        tuple: (start_time, end_time) as datetime objects
    """
    current_time = datetime.now()

    # Convert seconds to hours, minutes, seconds
    hours = daily_reporting_time_seconds // 3600
    minutes = (daily_reporting_time_seconds % 3600) // 60
    seconds = daily_reporting_time_seconds % 60

    def get_window_for_date(base_date):
        start_time = base_date.replace(
            hour=hours, minute=minutes, second=seconds, microsecond=0
        )

        # Calculate end time (reporting time + 14 hours)
        total_hours = hours + 14
        ending_hours = total_hours % 24
        crosses_midnight = total_hours >= 24

        end_time = base_date.replace(
            hour=ending_hours, minute=minutes, second=seconds, microsecond=0
        )

        if crosses_midnight:
            end_time += timedelta(days=1)

        return start_time, end_time

    # Get yesterday's and today's windows
    yesterday_start, yesterday_end = get_window_for_date(
        current_time - timedelta(days=1)
    )
    today_start, today_end = get_window_for_date(current_time)

    # First check if we've passed yesterday's end time
    if current_time >= yesterday_end:
        # We've passed yesterday's end time, so return today's window
        return today_start, today_end
    else:
        # We haven't reached yesterday's end time yet, so stay with yesterday's window
        return yesterday_start, yesterday_end


@frappe.whitelist()
def dashboard():
    caregivers = frappe.db.get_list(
        "Caregiver", fields=["*"], filters={"user_id": frappe.session.user}
    )

    if caregivers:
        caregiver = caregivers[0]
    else:
        caregiver = None  # couldn't find caregiver for the logged-in user

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
        if (engagement.start_date > todayDateString) or (
            engagement.end_date and todayDateString > engagement.end_date
        ):
            continue

        for assignedCaregiver in engagement.assigned_caregivers:
            # Skip caregivers that do not match the given caregiver name
            if assignedCaregiver.caregiver != caregiver.name:
                continue

            # Skip caregivers who are not currently active(based on start and end dates)
            if (
                not assignedCaregiver.start_date
                or assignedCaregiver.start_date > todayDateString
                or (
                    assignedCaregiver.end_date
                    and todayDateString > assignedCaregiver.end_date
                )
            ):
                continue
            
            todays_start_time =  datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            todays_end_time = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)

            # if service hour is 24 hours:
            if engagement.service_hours == "24":
                checkinsToday = frappe.get_list(
                    "Engagement Daily Record",
                    fields=["*"],
                    filters=[
                        ["engagement", "=", engagement.name],
                        ["creation", "between", [todayDateString, todayDateString]],
                    ],
                )
            # if service hour is 12 hours:
            else:
                reporting_time_in_seconds = int(
                    engagement.daily_reporting_time.total_seconds()
                )
                todays_start_time, todays_end_time = calculate_time_window(
                    reporting_time_in_seconds
                )

                checkinsToday = frappe.get_list(
                    "Engagement Daily Record",
                    fields=["*"],
                    filters={
                        "engagement": engagement.name,
                        "check_in_date_and_time": [
                            "between",
                            [todays_start_time, todays_end_time],
                        ],
                    },
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
                    "reporting_start_time": todays_start_time,
                    "reporting_end_time": todays_end_time,
                }
            )

    return {
        "caregiver": caregiver,
        "engagements": engagements,
    }


@frappe.whitelist()
def profile():
    caregivers = frappe.db.get_list(
        "Caregiver", filters={"user_id": frappe.session.user}
    )

    caregiver_data = frappe.get_doc("Caregiver", caregivers[0].name)

    # Get customer data for profile pic for Ratings Tab
    customers = []
    for rating in caregiver_data.ratings:
        customers.append(frappe.get_doc("Customer", rating.rater))

    # If Caregiver is Solo and not from an Agency
    if caregiver_data.supplier:
        agency = frappe.get_doc("Supplier", caregiver_data.supplier)
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
    daily_engagement_record = frappe.get_doc("Engagement Daily Record", dailyRecordId)

    engagement = frappe.get_doc("Engagement", daily_engagement_record.engagement)

    customer = frappe.get_doc("Customer", engagement.customer)

    # vital_tasks = []

    # # filter out vital tasks from engagement record and add to vitalTasks array
    # for task in engagement.required_activity:
    #     if task.activity_type == "Vital":
    #         vital_tasks.append(task)
    #         engagement.required_activity.remove(task)

    # # filter out vital tasks from daily engagement record
    # for task in daily_engagement_record.performed_activities:
    #     if task.activity_type == "Vital":
    #         daily_engagement_record.performed_activities.remove(task)

    return {
        "customerDoc": customer,
        "dailyEngagementRecord": daily_engagement_record,
        "engagementRecord": engagement,
        # "vitalTasks": vital_tasks,
    }


@frappe.whitelist()
# def addActivityToDailyRecord(dailyRecordId, activityName, activityData=None):
def addActivityToDailyRecord(dailyRecordId, activityName):
    ist_date = datetime.now(pytz.timezone("Asia/Kolkata")).date()
    ist_time = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    inputTime = str(ist_date) + " " + str(ist_time)

    engagementDailyRecord = frappe.get_doc("Engagement Daily Record", dailyRecordId)

    activity_entry = {
        "activity": activityName,
        "completion_time": inputTime,
    }

    # for vitals we need activity data
    # if activityData:
    #     activity_entry["activity_data"] = activityData
    #     activity_entry["activity_type"] = "Vital"

    engagementDailyRecord.append("performed_activities", activity_entry)
    engagementDailyRecord.save()
    frappe.db.commit()

    updated_performed_activities = frappe.get_doc(
        "Engagement Daily Record", dailyRecordId
    ).performed_activities

    return updated_performed_activities


@frappe.whitelist()
def removeActivityFromDailyRecord(taskName, dailyRecordId):
    frappe.db.delete("Engagement Daily Activity", {"name": taskName})
    frappe.db.commit()
    updated_performed_activities = frappe.get_doc(
        "Engagement Daily Record", dailyRecordId
    ).performed_activities

    return updated_performed_activities


# Not in use anymore
@frappe.whitelist()
def updateActivityToDailyRecord(taskId, activity_data, completion_time):
    ist_date = datetime.now(pytz.timezone("Asia/Kolkata")).date()
    ist_time = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    if completion_time == "default":
        inputTime = str(ist_date) + " " + str(ist_time)
    else:
        inputTime = str(ist_date) + " " + completion_time

    # replace dailyrecordId to the activityId
    frappe.db.set_value(
        "Engagement Daily Activity",
        taskId,
        {
            "activity_data": activity_data,
            "completion_time": inputTime,
        },
    )
    return completion_time if completion_time != "default" else ist_time


# Not in use anymore
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


# Not in use anymore
@frappe.whitelist()
def fetchDailyRecordTasks(dailyRecordId):
    performed_activities = frappe.get_doc(
        "Engagement Daily Record", dailyRecordId
    ).required_activity
    return performed_activities


# Not in use anymore
@frappe.whitelist()
def fetchEngagementTasks(engagementId):
    required_activities = frappe.get_doc("Engagement", engagementId).required_activity
    return required_activities


@frappe.whitelist()
def createDailyRecord(engagement, caregiver):
    ist_datetime = (
        str(datetime.now(pytz.timezone("Asia/Kolkata")).date())
        + " "
        + str(datetime.now(pytz.timezone("Asia/Kolkata")).time())
    )

    # create a new document
    new_doc = frappe.get_doc(
        {
            "doctype": "Engagement Daily Record",
            "engagement": engagement,
            "caregiver": caregiver,
            "check_in_date_and_time": ist_datetime,
        }
    )
    new_doc.insert()
    return new_doc


@frappe.whitelist()
def checkout(record):
    ist_datetime = (
        str(datetime.now(pytz.timezone("Asia/Kolkata")).date())
        + " "
        + str(datetime.now(pytz.timezone("Asia/Kolkata")).time())
    )
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

    # Check if the supplied user is an email or a mobile number. Accordingly set the filter field
    filterField = "user"
    if not "@" in user:
        filterField = "mobile_no"

    contact = frappe.get_all("Contact", fields=["name"], filters={filterField: user})

    customerDocs = list()
    if contact is None or len(contact) == 0:
        return customerDocs

    customers = frappe.db.get_values(
        "Dynamic Link",
        {
            "parent": contact[0].name,
            "parenttype": "Contact",
            "link_doctype": "Customer",
        },
        "link_name as name",
        as_dict=True,
    )

    # if no customer found associated for the contact, return
    if customers is None or len(customers) == 0:
        return customerDocs

    for customer in customers:
        customerDocs.append(frappe.get_doc("Customer", customers[0].name))

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

    if user is None:
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

from frappe.utils import now

@frappe.whitelist(allow_guest=True)
def update_caregiver_response(response_id):
    """
    This API endpoint updates the Caregiver Response document
    corresponding to the given response_id. It sets the status to "Accepted"
    and logs the current time in response_time.

    This function is guest-accessible and used when a caregiver clicks
    a response link (typically from WhatsApp).
    """

    # Ensure response_id is provided in the URL
    if not response_id:
        frappe.throw("Missing response ID in the URL.", title="Error")

    # Attempt to fetch the Caregiver Response document
    try:
        doc = frappe.get_doc("Caregiver Response", response_id)
    except frappe.DoesNotExistError:
        frappe.throw(f"No Caregiver Response found with ID {response_id}", title="Error")
    except Exception:
        frappe.throw("Something went wrong. Contact support.", title="Error")

    # Allow update as guest by bypassing permission check
    try:
        doc.flags.ignore_permissions = True
        doc.status = "Accepted"
        doc.response_time = now()
        doc.save()
        frappe.db.commit()
    except Exception:
        frappe.throw("Failed to update response.", title="Error")

    return "success"



@frappe.whitelist(allow_guest=True)
def update_fcm_token():
    try:
        data = json.loads(frappe.request.data)
        email_id = data.get("email_id")
        fcm_token = data.get("fcm_token")

        if not email_id or not fcm_token:
            frappe.throw("Missing email or token", title="Validation Error")

        contact = frappe.db.sql("""
            SELECT parent FROM `tabContact Email`
            WHERE email_id = %s
            LIMIT 1
        """, (email_id,), as_dict=True)

        if contact:
            contact_doc = frappe.get_doc("Contact", contact[0]["parent"])
            contact_doc.custom_fcm_token = fcm_token
            contact_doc.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.logger().info(f"✅ FCM Token updated for: {email_id}")
            return {"status": "success", "message": "FCM Token updated successfully"}
        else:
            frappe.throw(f"Contact not found for {email_id}", title="Not Found")

    except Exception as e:
        frappe.log_error(f"Exception: {str(e)}", "update_fcm_token")
        return {"status": "error", "message": str(e)}


import frappe
from frappe import _
from frappe.utils import now
import qrcode

# Generate a QR code from a given UPI URI
def generate_upi_qr(upi_uri, file_path="/tmp/upi_qr.png"):
    img = qrcode.make(upi_uri)
    img.save(file_path)
    return file_path


@frappe.whitelist(allow_guest=True)
def accept_terms():
    """
    Called from frontend when customer accepts terms and conditions.
    Marks the Customer record with acceptance flag and timestamp.
    """
    try:
        data = frappe.request.json or {}

        customer_id = data.get('customer_id')
        engagement_id = data.get('engagement_id')

        if not customer_id and not engagement_id:
            frappe.throw(_("Missing Customer ID or Engagement ID."))

        # Fallback to resolve customer from engagement if not directly provided
        if not customer_id:
            engagement = frappe.get_doc("Engagement", engagement_id)
            customer_id = engagement.customer

        customer = frappe.get_doc("Customer", customer_id)
        customer.custom_terms_accepted = 1
        customer.custom_acceptance_timestamp = now()
        customer.save(ignore_permissions=True)

        return {"success": True}

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Customer Accept Terms Error")
        return {"success": False}

@frappe.whitelist(allow_guest=True)
def get_terms_status(customer_id):
    try:
        if not customer_id:
            return {"success": False, "error": "Missing customer_id"}

        # Fetch the value from Customer doctype
        accepted = frappe.db.get_value("Customer", customer_id, "custom_terms_accepted")

        return {
            "success": True,
            "accepted": bool(accepted)
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_terms_status Error")
        return {
            "success": False,
            "error": "Server error"
        }


@frappe.whitelist(allow_guest=True)
def get_payment_details(customer_id=None, engagement_id=None):
    """
    Fetches latest unpaid invoice for the customer and returns
    payment info + UPI QR string for frontend rendering.
    """
    try:
        if not customer_id and not engagement_id:
            return {
                "success": False,
                "error": "Missing customer_id or engagement_id."
            }

        if not customer_id:
            engagement = frappe.get_doc("Engagement", engagement_id)
            customer_id = engagement.customer

        customer = frappe.get_doc("Customer", customer_id)

        # Get the latest unpaid Sales Invoices for the customer
        invoices = frappe.db.get_all(
            "Sales Invoice",
            filters={
                "customer": customer.name,
                "outstanding_amount": [">", 0],
                "docstatus": 1
            },
            fields=["name", "rounded_total", "company"],
            order_by="posting_date desc"
        )

        invoice = None

        for inv in invoices:
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": inv.name},
                fields=["item_name", "item_code"]
            )
            for item in items:
                if "registration" in (item.item_name or "").lower():
                    invoice = inv
                    break
                linked_item_name = frappe.db.get_value("Item", item.item_code, "item_name")
                if linked_item_name and "registration" in linked_item_name.lower():
                    invoice = inv
                    break
            if invoice:
                break

        if not invoice:
            return {
                "success": False,
                "error": "No unpaid registration invoice found for this customer."
            }

        # Fetch UPI ID from Company
        upi_id = frappe.db.get_value("Company", invoice.company, "custom_upi_id")
        if not upi_id:
            return {
                "success": False,
                "error": "UPI ID not configured in Company settings."
            }

        # Construct UPI URI for QR Code
        upi_uri = (
            f"upi://pay?"
            f"pa={upi_id}"
            f"&pn={customer.customer_name}"
            f"&am={format(invoice.rounded_total, '.2f')}"
            f"&cu=INR"
            f"&tn=Invoice {invoice.name}"
        )

        # Generate QR code image (not returned in backend — frontend uses URI)
        generate_upi_qr(upi_uri)

        return {
            "success": True,
            "data": {
                "customer_id": customer.name,
                "invoice_number": invoice.name,
                "payment_amount": invoice.rounded_total or 0,
                "upi_id": upi_id,
                "customer_name": customer.customer_name,
                "upi_uri": upi_uri
            }
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error in get_payment_details")
        return {
            "success": False,
            "error": "Unexpected error occurred."
        }




