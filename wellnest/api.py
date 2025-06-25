import frappe  # type: ignore
from datetime import datetime, date, timedelta
from .utils.sms_service import send_otp_using_twilio, verify_otp_for_phone

from datetime import datetime, date, timezone
import pytz



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

        # # Checking for active engagements by comparing today to the start and end dates
        # if (engagement.start_date > todayDateString) or (
        #     engagement.end_date and todayDateString > engagement.end_date
        # ):

        #     continue


            # This will prevent the comparison from being evaluated if the field is None.
        if (engagement.start_date and engagement.start_date > todayDateString) or (
             engagement.end_date and engagement.end_date < todayDateString
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


# @frappe.whitelist()

# def activity(dailyRecordId):
#     frappe.log_error(title="Activity API Debug", message=f"Called with dailyRecordId: {daily_record_id}")


#     daily_engagement_record = frappe.get_doc("Engagement Daily Record", dailyRecordId)

#     engagement = frappe.get_doc("Engagement", daily_engagement_record.engagement)

#     customer = frappe.get_doc("Customer", engagement.customer)

#     vital_tasks = []

#     # filter out vital tasks from engagement record and add to vitalTasks array
#     for task in engagement.required_activity:
#         if task.activity_type == "Vital":
#             vital_tasks.append(task)
#             engagement.required_activity.remove(task)

#     # filter out vital tasks from daily engagement record
#     for task in daily_engagement_record.performed_activities:
#         if task.activity_type == "Vital":
#             daily_engagement_record.performed_activities.remove(task)

#     return {
#         "customerDoc": customer,
#         "dailyEngagementRecord": daily_engagement_record,
#         "engagementRecord": engagement,
#         "vitalTasks": vital_tasks,
#     }



@frappe.whitelist(allow_guest=True)
def activity(dailyRecordId=None):
    """
    API to fetch caregiver dashboard data for a specific day's engagement,
    including customer info, engagement details, and latest vitals performed.

    Parameters:
    - dailyRecordId: ID of the Engagement Daily Record to fetch context for.

    Returns:
    - customerDoc: Customer document linked to the engagement.
    - dailyEngagementRecord: The Engagement Daily Record document.
    - engagementRecord: The full Engagement document.
    - vitalTasks: A list of latest completed vital tasks (if available).
    """
    try:
        frappe.log_error("Activity API Called", f"Received dailyRecordId: {dailyRecordId}")

        if not dailyRecordId:
            return {"error": "dailyRecordId is required"}

        # Fetch documents
        daily_engagement_record = frappe.get_doc("Engagement Daily Record", dailyRecordId)
        engagement = frappe.get_doc("Engagement", daily_engagement_record.engagement)
        customer = frappe.get_doc("Customer", engagement.customer)

        # Define supported vital types
        vital_names = [
            "Body temperature", "Pulse rate", "Respiratory rate",
            "Blood pressure", "Oxygen saturation", "Heart rate"
        ]

        # Extract the latest reading for each vital type
        latest_vitals = {}
        sorted_tasks = sorted(
            daily_engagement_record.performed_activities,
            key=lambda x: x.completion_time or "",
            reverse=True
        )

        for task in sorted_tasks:
            if task.activity in vital_names and task.activity not in latest_vitals:
                latest_vitals[task.activity] = {
                    "activity": task.activity,
                    "completion_time": task.completion_time,
                    "activity_data": task.activity_data
                }

        # Return as a list of latest unique vital readings
        vital_tasks = list(latest_vitals.values())

        return {
            "customerDoc": customer,
            "dailyEngagementRecord": daily_engagement_record,
            "engagementRecord": engagement,
            "vitalTasks": vital_tasks
        }

    except Exception as e:
        frappe.log_error("Activity API Error", frappe.get_traceback())
        return {"error": str(e)}

    

@frappe.whitelist(allow_guest=False)
def submit_vital_reading(engagement, vital_type, value, recorded_on=None):
    """
    API to record a new vital reading against an Engagement.

    Parameters:
    - engagement: Engagement ID to which this reading is linked.
    - vital_type: The name/type of the vital being recorded (e.g., Heart Rate).
    - value: The measured value entered by caregiver.
    - recorded_on (optional): Timestamp of when it was recorded. Defaults to now().

    Behavior:
    - Also sets the `date` field (date only) in addition to `recorded_on` (datetime).
    - Records the current session user as `recorded_by`.

    Returns:
    - Success message with the Vital Reading document name.
    """
    try:
        # Basic validation
        if not (engagement and vital_type and value):
            frappe.throw("Missing required fields: engagement, vital_type, value")

        # Create new Vital Reading document
        vital_doc = frappe.new_doc("Vital Reading")
        vital_doc.engagement = engagement
        vital_doc.vital_type = vital_type
        vital_doc.value = value
        vital_doc.recorded_on = recorded_on or frappe.utils.now()
        vital_doc.date = frappe.utils.today()  # Explicitly set the date field
        vital_doc.recorded_by = frappe.session.user

        # Save to database
        vital_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"message": "Vital reading saved", "vital": vital_doc.name}

    except Exception as e:
        # Log and return error
        frappe.log_error(frappe.get_traceback(), "submit_vital_reading error")
        frappe.throw(f"Failed to save vital reading: {str(e)}")





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










