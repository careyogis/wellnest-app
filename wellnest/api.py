import frappe  # type: ignore
from datetime import datetime, date, timedelta
from .utils.sms_service import send_otp_using_twilio, verify_otp_for_phone

from datetime import datetime, date, timezone
import pytz
import json
import requests
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

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

            todays_start_time = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            todays_end_time = datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=0
            )

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
def doctor_profile():
    practitioners = frappe.db.get_list(
        "Practitioner",
        filters={"user_id": frappe.session.user},
    )

    if not practitioners:
        frappe.throw("Practitioner not found")

    practitioner = frappe.get_doc(
        "Practitioner",
        practitioners[0].name,
    )

    return {
        "doctor": practitioner,
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


@frappe.whitelist(allow_guest=True, methods=["POST"])
def contactUs():
    data = frappe.form_dict
    email = data.get("email")

    # Check if a CY lead with this email already exists to prevent duplicates
    if email and frappe.db.exists("CY Lead", {"email": email}):
        return {"status": "exists", "message": "You are already on the list!"}    

    new_doc = frappe.get_doc(
        {
            "doctype": "CY Lead",
            "full_name": data.get("full_name"),
            "phone_number": data.get("phone"),
            "email": data.get("email"),
            "city": data.get("city"),
            "requirement": data.get("requirement"),
            "enquiry_details": data.get("enquiry"),
            "source": data.get("source") or "Website",
        }
    )

    # We use ignore_permissions=True so as to avoid giving the 'Guest' user 
    # 'Create' rights on the doctype or in the Role Permissions Manager.    
    new_doc.insert(ignore_permissions=True)
    return {"status": "success"}


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
def lookup_doctor(phone):
    """
    Checks if a doctor exists for the given mobile number.
    Returns success/failure without sending OTP.
    """

    payload = {
        "success": False,
        "message": "No doctor found with this number",
    }

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"mobile": phone},
        "name",
    )

    if practitioner:
        payload["success"] = True
        payload["message"] = "Doctor found"

    return payload

@frappe.whitelist(allow_guest=True)
def login_with_phone(phone):
    """
    Logs a user into Frappe after Firebase OTP has already been verified.
    """

    user = frappe.db.get_value(
        "User",
        {"mobile_no": phone},
        "name"
    )

    if not user:
        frappe.throw("User not found")

    frappe.set_user(user)

    from frappe.auth import LoginManager

    login_manager = LoginManager()

    login_manager.user = user
    login_manager.post_login()

    return {
        "success": True,
        "user": user
    }


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
        frappe.throw(
            f"No Caregiver Response found with ID {response_id}", title="Error"
        )
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


@frappe.whitelist()
def update_fcm_token():
    try:
        data = json.loads(frappe.request.data)
        email_id = data.get("email_id")
        fcm_token = data.get("fcm_token")

        if not email_id or not fcm_token:
            frappe.throw("Missing email or token", title="Validation Error")

        contact = frappe.db.sql(
            """
            SELECT parent FROM `tabContact Email`
            WHERE email_id = %s
            LIMIT 1
        """,
            (email_id,),
            as_dict=True,
        )

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


# ✅ Generate a QR code image from a UPI URI and save it to a temporary path
def generate_upi_qr(upi_uri, file_path="/tmp/upi_qr.png"):
    img = qrcode.make(upi_uri)
    img.save(file_path)
    return file_path


# 🔍 Get the most recent unpaid Sales Invoice for a customer that includes a registration item
def get_unpaid_registration_invoice(customer_name):
    try:
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "customer": customer_name,
                "outstanding_amount": [">", 0],
                "docstatus": 1,
            },
            fields=["name", "rounded_total", "company"],
            order_by="posting_date desc",
        )

        frappe.log_error(
            f"{len(invoices)} unpaid invoices found", "get_unpaid_registration_invoice"
        )

        for inv in invoices:
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": inv.name},
                fields=["item_name", "item_code"],
            )
            for item in items:
                # Check if item's name contains "registration"
                item_name = (item.item_name or "").lower()
                if "registration" in item_name:
                    frappe.log_error(
                        inv.name,
                        "get_unpaid_registration_invoice: Matched by item_name",
                    )
                    return inv

                # Also check linked Item record’s item_name
                linked_name = frappe.db.get_value("Item", item.item_code, "item_name")
                if linked_name and "registration" in linked_name.lower():
                    frappe.log_error(
                        inv.name,
                        "get_unpaid_registration_invoice: Matched by linked Item.item_name",
                    )
                    return inv

        frappe.log_error(
            "No unpaid registration invoice found", "get_unpaid_registration_invoice"
        )
        return None

    except Exception:
        frappe.log_error(
            frappe.get_traceback(), "get_unpaid_registration_invoice: Error"
        )
        return None


@frappe.whitelist(allow_guest=True)
def get_terms_content():
    terms = frappe.db.get_value(
        "Terms and Conditions",
        {"custom_is_active": 1},
        ["name", "title", "terms"],
        order_by="modified desc",
        as_dict=True,
    )
    if not terms:
        return {"success": False, "error": "No active Terms & Conditions found"}

    return {"success": True, "content": terms.terms, "title": terms.title}


@frappe.whitelist(allow_guest=True)
def accept_terms():
    """
    Guest API to accept T&C and handle registration invoice.
    Returns current status:
      - pending → T&C not accepted
      - accepted → T&C accepted, invoice unpaid (includes QR)
      - paid → T&C accepted, invoice paid (Thank You)
    """
    try:
        data = frappe.request.json or {}
        customer_id = data.get("customer_id")
        engagement_id = data.get("engagement_id")

        if not customer_id and not engagement_id:
            frappe.throw(_("Missing Customer ID or Engagement ID."))

        if not customer_id:
            engagement = frappe.get_doc("Engagement", engagement_id)
            customer_id = engagement.customer

        customer = frappe.get_doc("Customer", customer_id)

        # -----------------------
        # Step 1: Capture T&C acceptance
        # -----------------------
        if customer.custom_registration_term in [None, "pending"]:
            latest_terms = frappe.db.get_value(
                "Terms and Conditions",
                {"custom_is_active": 1},
                "name",
                order_by="modified desc"
            )
            customer.custom_registration_term = "accepted"
            customer.custom_acceptance_timestamp = now()
            if latest_terms:
                customer.custom_accepted_term = latest_terms
            customer.save(ignore_permissions=True)
            frappe.db.commit()

        # -----------------------
        # Step 2: Check for existing registration invoice
        # -----------------------
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"customer": customer.name, "docstatus": 1},
            order_by="creation desc"
        )

        registration_item_code = frappe.db.get_value(
            "Item", {"item_name": ["like", "%registration%"]}, "name"
        )
        invoice = None

        for inv in invoices:
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": inv.name, "item_code": registration_item_code}
            )
            if items:
                invoice = frappe.get_doc("Sales Invoice", inv.name)
                break

        # Create invoice if none exists
        if not invoice:
            if not registration_item_code:
                return {"success": False, "error": "No registration item found."}

            invoice = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": customer.name,
                "items": [{"item_code": registration_item_code, "qty": 1}]
            })
            invoice.insert(ignore_permissions=True)
            invoice.submit()

        # -----------------------
        # Step 3: Prepare response
        # -----------------------
        upi_uri = None
        if invoice.outstanding_amount > 0:
            upi_id = frappe.db.get_value("Company", invoice.company, "custom_upi_id")
            if not upi_id:
                return {"success": False, "error": f"UPI ID not configured for {invoice.company}"}
            upi_uri = f"upi://pay?pa={upi_id}&pn={customer.customer_name}&am={format(invoice.rounded_total, '.2f')}&cu=INR&tn=Invoice {invoice.name}"

        status = "paid" if invoice.outstanding_amount == 0 else "accepted"

        return {
            "success": True,
            "data": {
                "status": status,
                "custom_registration_term": customer.custom_registration_term,
                "custom_acceptance_timestamp": customer.custom_acceptance_timestamp,
                "invoice_number": invoice.name,
                "payment_amount": invoice.rounded_total,
                "upi_uri": upi_uri,
                "customer_name": customer.customer_name
            }
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "accept_terms Error")
        return {"success": False, "error": "Unexpected server error. Check logs."}


@frappe.whitelist(allow_guest=True)
def get_payment_details(customer_id=None, engagement_id=None):
    """
    ✅ Guest API to fetch T&C + registration invoice details.
    Flow:
    1. Check if Terms accepted. If not, return pending.
    2. If accepted, fetch registration invoice (create only if none exists).
    3. If invoice paid → show Thank You.
    4. If invoice unpaid → return UPI QR.
    """
    try:
        # --------------------------
        # Resolve customer from engagement
        # --------------------------
        if not customer_id and engagement_id:
            engagement = frappe.get_doc("Engagement", engagement_id)
            customer_id = engagement.customer

        if not customer_id:
            return {"success": False, "error": "Missing customer ID."}

        customer = frappe.get_doc("Customer", customer_id)
        status = customer.custom_registration_term or "pending"
        accepted = status in ["accepted", "paid"]
        acceptance_timestamp = customer.custom_acceptance_timestamp

        # --------------------------
        # Terms not accepted → return pending
        # --------------------------
        if not accepted:
            return {
                "success": True,
                "data": {
                    "status": "pending",
                    "accepted": False,
                    "custom_registration_term": status,
                    "custom_acceptance_timestamp": acceptance_timestamp,
                    "message": "T&C not accepted yet."
                }
            }

        # --------------------------
        # Terms accepted → fetch registration invoice from child table
        # --------------------------
        item_code = frappe.db.get_value("Item", {"item_name": ["like", "%registration%"]}, "name")
        invoice = None

        if item_code:
            invoice_item = frappe.get_all(
                "Sales Invoice Item",
                filters={"item_code": item_code, "parenttype": "Sales Invoice"},
                fields=["parent"],
                order_by="creation desc",
                limit_page_length=1
            )
            if invoice_item:
                invoice = frappe.get_doc("Sales Invoice", invoice_item[0].parent)

        # --------------------------
        # Create invoice only if none exists
        # --------------------------
        if not invoice:
            if not item_code:
                return {"success": False, "error": "No registration item found."}

            new_invoice = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": customer.name,
                "items": [{"item_code": item_code, "qty": 1}]
            })
            new_invoice.insert(ignore_permissions=True)
            new_invoice.submit()
            invoice = new_invoice

        # --------------------------
        # Paid → hide QR, show Thank You
        # --------------------------
        if invoice.outstanding_amount == 0:
            return {
                "success": True,
                "data": {
                    "status": "paid",
                    "accepted": True,
                    "custom_registration_term": customer.custom_registration_term,
                    "custom_acceptance_timestamp": customer.custom_acceptance_timestamp,
                    "message": "✅ Thank You! Payment already completed.",
                    "invoice_number": invoice.name,
                    "payment_amount": invoice.rounded_total,
                    "customer_name": customer.customer_name
                }
            }

        # --------------------------
        # Unpaid → generate QR
        # --------------------------
        upi_id = frappe.db.get_value("Company", invoice.company, "custom_upi_id")
        if not upi_id:
            return {"success": False, "error": f"UPI ID not configured for {invoice.company}"}

        upi_uri = f"upi://pay?pa={upi_id}&pn={customer.customer_name}&am={format(invoice.rounded_total, '.2f')}&cu=INR&tn=Invoice {invoice.name}"

        return {
            "success": True,
            "data": {
                "status": "accepted",
                "accepted": True,
                "custom_registration_term": customer.custom_registration_term,
                "custom_acceptance_timestamp": acceptance_timestamp,
                "customer_id": customer.name,
                "invoice_number": invoice.name,
                "payment_amount": invoice.rounded_total,
                "upi_id": upi_id,
                "upi_uri": upi_uri,
                "customer_name": customer.customer_name
            }
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_payment_details Error")
        return {"success": False, "error": "Unexpected error occurred."}



IDENTITY_TOOLKIT_BASE = "https://identitytoolkit.googleapis.com/v1"

_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        service_account_path = frappe.conf.get("firebase_service_account_path")
        if not service_account_path:
            frappe.throw("firebase_service_account_path not set in site config")
        cred = credentials.Certificate(service_account_path)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def _get_firebase_web_api_key():
    api_key = frappe.conf.get("firebase_web_api_key")
    if not api_key:
        frappe.throw("firebase_web_api_key not set in site config")
    return api_key


@frappe.whitelist(allow_guest=True)
def send_otp(phone: str, recaptcha_token: str):
    if not phone or not recaptcha_token:
        frappe.throw("phone and recaptcha_token are required")

    # Converting +919111111111 -> 9111111111 for database lookup
    lookup_phone = phone

    if lookup_phone.startswith("+91"):
        lookup_phone = lookup_phone[3:]

    practitioner = frappe.db.get_value(
        "Practitioner",
        {"mobile": lookup_phone},
        "name"
    )

    if not practitioner:
        frappe.throw("No doctor found with this number")

    api_key = _get_firebase_web_api_key()
    url = f"{IDENTITY_TOOLKIT_BASE}/accounts:sendVerificationCode?key={api_key}"

    payload = {
        "phoneNumber": phone,          # Keep +91 for Firebase
        "recaptchaToken": recaptcha_token,
    }

    resp = requests.post(url, json=payload, timeout=15)
    data = resp.json()

    if resp.status_code != 200:
        error_message = data.get("error", {}).get("message", "UNKNOWN_ERROR")
        frappe.log_error(
            title="Firebase sendVerificationCode failed",
            message=frappe.as_json(data),
        )
        frappe.throw(f"Failed to send OTP: {error_message}")

    return {
        "success": True,
        "session_info": data["sessionInfo"],
    }

@frappe.whitelist(allow_guest=True)
def verify_otp(session_info: str, code: str):
    if not session_info or not code:
        frappe.throw("session_info and code are required")

    api_key = _get_firebase_web_api_key()
    url = f"{IDENTITY_TOOLKIT_BASE}/accounts:signInWithPhoneNumber?key={api_key}"
    payload = {"sessionInfo": session_info, "code": code}

    resp = requests.post(url, json=payload, timeout=15)
    data = resp.json()

    if resp.status_code != 200:
        error_message = data.get("error", {}).get("message", "UNKNOWN_ERROR")
        frappe.log_error(title="Firebase signInWithPhoneNumber failed", message=frappe.as_json(data))
        frappe.throw(f"Invalid OTP: {error_message}")

    uid = data["localId"]
    phone_number = data.get("phoneNumber")
    is_new_user = data.get("isNewUser", False)

    _get_firebase_app()
    custom_token = firebase_auth.create_custom_token(uid)

    return {
        "success": True,
        "custom_token": custom_token.decode("utf-8"),
        "uid": uid,
        "phone_number": phone_number,
        "is_new_user": is_new_user,
    }
