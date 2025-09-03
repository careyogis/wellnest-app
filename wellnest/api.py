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
    new_doc = frappe.get_doc(
        {
            "doctype": "CY Lead",
            "full_name": data.get("fullname"),
            "phone_number": data.get("phone"),
            "city": data.get("city"),
            "requirement": data.get("requirement"),
            "enquiry_details": data.get("enquiry"),
            "status": "01-New Request",
            "source": "Website",
        }
    )
    new_doc.insert()
    return frappe.form_dict


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


# ✅ API to accept Terms & Conditions (Guest allowed)
@frappe.whitelist(allow_guest=True)
def accept_terms():
    try:
        data = frappe.request.json or {}
        customer_id = data.get("customer_id")
        engagement_id = data.get("engagement_id")

        frappe.log_error(str(data), "AcceptTerms: Incoming Data")

        # 🔍 Validate inputs
        if not customer_id and not engagement_id:
            frappe.log_error(
                "Missing both customer_id and engagement_id",
                "AcceptTerms: Missing Input",
            )
            frappe.throw(_("Missing Customer ID or Engagement ID."))

        # 🔁 Resolve customer ID from engagement if not provided
        if not customer_id:
            try:
                engagement = frappe.get_doc("Engagement", engagement_id)
                customer_id = engagement.customer
                frappe.log_error(
                    customer_id, "AcceptTerms: Resolved customer from engagement"
                )
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"AcceptTerms: Engagement fetch failed for {engagement_id}",
                )
                return {"success": False, "error": "Engagement not found or invalid."}

        # 🔍 Fetch Customer doc
        try:
            customer = frappe.get_doc("Customer", customer_id)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"AcceptTerms: Failed to fetch Customer {customer_id}",
            )
            return {"success": False, "error": "Customer not found."}

        # 🔄 Return early if already accepted or paid
        if customer.custom_registration_term in ["accepted", "paid"]:
            frappe.log_error(
                customer.custom_registration_term,
                f"AcceptTerms: Already Accepted by {customer.name}",
            )
            return {"success": True, "message": "Already accepted."}

        # ✅ Mark terms as accepted
        customer.custom_registration_term = "accepted"
        customer.custom_acceptance_timestamp = now()

        # ⭐ NEW: Capture which Terms & Conditions were accepted
        latest_terms = frappe.db.get_value(
            "Terms and Conditions",
            {"custom_is_active": 1},
            "name",
            order_by="modified desc",
        )
        if latest_terms:
            customer.custom_accepted_term = latest_terms
            frappe.log_error(
                latest_terms, f"AcceptTerms: Linked Accepted Term for {customer.name}"
            )

        customer.save(ignore_permissions=True)
        frappe.log_error(customer.name, "AcceptTerms: Customer marked as accepted")

        # 🔍 Check for existing unpaid registration invoice
        invoice = get_unpaid_registration_invoice(customer.name)
        if invoice:
            frappe.log_error(invoice.name, "AcceptTerms: Found existing unpaid invoice")
        else:
            frappe.log_error(
                "No unpaid invoice found — proceeding to create one",
                "AcceptTerms: Invoice Creation Triggered",
            )

            # 📦 Get registration item code
            item_code = frappe.db.get_value(
                "Item", {"item_name": ["like", "%registration%"]}, "name"
            )
            if not item_code:
                msg = "No item found with 'registration' in item_name"
                frappe.log_error(msg, "AcceptTerms: Missing Registration Item")
                return {"success": False, "error": msg}

            # 🛒 Check if item is marked as Sales Item
            is_sales_item = frappe.db.get_value("Item", item_code, "is_sales_item")
            if not is_sales_item:
                msg = f"Item {item_code} is not marked as Sales Item"
                frappe.log_error(msg, "AcceptTerms: Item Config Error")
                return {"success": False, "error": msg}

            # 🧾 Create and submit new Sales Invoice
            try:
                invoice = frappe.get_doc(
                    {
                        "doctype": "Sales Invoice",
                        "customer": customer.name,
                        "items": [{"item_code": item_code, "qty": 1}],
                    }
                )
                frappe.log_error(
                    "AcceptTerms: Invoice Doc Before Insert", frappe.as_json(invoice)
                )

                invoice.insert(ignore_permissions=True)
                frappe.log_error(invoice.name, "AcceptTerms: Invoice Inserted")

                invoice.submit()
                frappe.log_error(invoice.name, "AcceptTerms: Invoice Submitted")

                if invoice.docstatus != 1:
                    frappe.log_error(
                        invoice.name, "AcceptTerms: Invoice not submitted successfully"
                    )

            except Exception:
                frappe.log_error(
                    frappe.get_traceback(), "AcceptTerms: Invoice Creation Failed"
                )
                return {
                    "success": False,
                    "error": "Invoice creation failed. Check item setup and logs.",
                }

        # 🏦 Generate UPI URI from company config
        upi_id = frappe.db.get_value("Company", invoice.company, "custom_upi_id")
        if not upi_id:
            msg = f"No UPI ID found for company {invoice.company}"
            frappe.log_error(msg, "AcceptTerms: UPI ID Missing")
            return {"success": False, "error": msg}

        upi_uri = f"upi://pay?pa={upi_id}&pn={customer.customer_name}&am={format(invoice.rounded_total, '.2f')}&cu=INR&tn=Invoice {invoice.name}"

        # 🖨️ Generate QR Code from UPI URI
        try:
            generate_upi_qr(upi_uri)
            frappe.log_error(upi_uri, "AcceptTerms: UPI URI & QR generated")
        except Exception:
            frappe.log_error(
                frappe.get_traceback(), "AcceptTerms: QR Code Generation Failed"
            )

        return {
            "success": True,
            "data": {
                "invoice_number": invoice.name,
                "payment_amount": invoice.rounded_total,
                "upi_id": upi_id,
                "upi_uri": upi_uri,
                "customer_name": customer.customer_name,
            },
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "AcceptTerms: Top-level Error")
        return {
            "success": False,
            "error": "Unexpected server error. Please check Error Logs.",
        }


# ✅ API to fetch T&C acceptance and payment status (Guest allowed)
@frappe.whitelist(allow_guest=True)
def get_payment_details(customer_id=None, engagement_id=None):
    try:
        # 🔁 Resolve customer ID if engagement is provided
        if not customer_id and engagement_id:
            engagement = frappe.get_doc("Engagement", engagement_id)
            customer_id = engagement.customer

        if not customer_id:
            return {"success": False, "error": "Missing customer ID."}

        customer = frappe.get_doc("Customer", customer_id)

        # 🔍 Look for registration invoices (paid or unpaid)
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"customer": customer.name, "docstatus": 1},
            fields=["name", "outstanding_amount", "company"],
            order_by="posting_date desc",
        )

        for inv in invoices:
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": inv.name},
                fields=["item_name", "item_code"],
            )
            for item in items:
                item_name = (item.item_name or "").lower()
                if "registration" in item_name:
                    if inv.outstanding_amount == 0:
                        # ✅ If paid, update customer status if needed
                        if customer.custom_registration_term != "paid":
                            customer.custom_registration_term = "paid"
                            customer.save(ignore_permissions=True)
                            frappe.db.commit()

                        return {
                            "success": True,
                            "data": {"status": "paid", "accepted": True},
                        }

        # 🔍 If not paid, find unpaid registration invoice
        invoice = get_unpaid_registration_invoice(customer.name)
        if not invoice:
            return {
                "success": False,
                "error": "No unpaid registration invoice found.",
                "data": {"status": customer.custom_registration_term or "pending"},
            }

        # 🏦 Get UPI details for QR
        upi_id = frappe.db.get_value("Company", invoice.company, "custom_upi_id")
        if not upi_id:
            return {"success": False, "error": "UPI ID not configured in Company."}

        upi_uri = f"upi://pay?pa={upi_id}&pn={customer.customer_name}&am={format(invoice.rounded_total, '.2f')}&cu=INR&tn=Invoice {invoice.name}"
        generate_upi_qr(upi_uri)

        return {
            "success": True,
            "data": {
                "status": customer.custom_registration_term or "pending",
                "accepted": customer.custom_registration_term in ["accepted", "paid"],
                "customer_id": customer.name,
                "invoice_number": invoice.name,
                "payment_amount": invoice.rounded_total,
                "upi_id": upi_id,
                "upi_uri": upi_uri,
                "customer_name": customer.customer_name,
            },
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_payment_details Error")
        return {"success": False, "error": "Unexpected error occurred."}
