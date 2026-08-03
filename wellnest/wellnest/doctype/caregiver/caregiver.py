# Copyright (c) 2024, www.thewellnest.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Caregiver(Document):
	pass

@frappe.whitelist()
def get_engagements_for_caregiver(caregiver_name):
	# Query to find all Engagements where the caregiver is assigned
	assignedEngagements = frappe.get_all('Engagement Caregiver', 
                                 filters={'caregiver': caregiver_name}, 
                                 fields=['parent'])

	# Extract unique Engagement IDs
	engagement_ids = list(set([engagementId['parent'] for engagementId in assignedEngagements]))

	# engagementDocs = frappe.get_all('Engagement', 
	# 							  		filters={'name': ("in", engagement_ids)},
	# 							  	)

	engagementDocs = frappe.get_doc('Engagement', engagement_ids)

	return engagementDocs

@frappe.whitelist()
def invite_user(caregiver: str):
	caregiver = frappe.get_doc("Caregiver", caregiver)
	caregiver.check_permission()

	if not caregiver.email:
		frappe.throw(("Please set Email Address"))

	user = frappe.get_doc(
		{
			"doctype": "User",
			"first_name": caregiver.full_name,
			"email": caregiver.email,
			"mobile_no": caregiver.phone_number,
			"user_type": "Website User",
			'roles': [ { 'role': 'Caregiver' } ],
			"send_welcome_email": 1,
		}
	).insert()

	return user.name


def calculate_time_window(daily_reporting_time_seconds):
	"""
	Calculate start and end time windows based on a reporting time.
	Switches to next window immediately when previous window's end time is reached.

	Args:
		daily_reporting_time_seconds (int): Reporting time in seconds

	Returns:
		tuple: (start_time, end_time) as datetime objects
	"""
	from datetime import datetime, timedelta

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
	from datetime import datetime, date

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

	if not caregivers:
		frappe.throw('Caregiver not found')

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

	return {
		"customerDoc": customer,
		"dailyEngagementRecord": daily_engagement_record,
		"engagementRecord": engagement,
	}


@frappe.whitelist()
def addActivityToDailyRecord(dailyRecordId, activityName):
	import pytz
	from datetime import datetime

	ist_date = datetime.now(pytz.timezone("Asia/Kolkata")).date()
	ist_time = datetime.now(pytz.timezone("Asia/Kolkata")).time()
	inputTime = str(ist_date) + " " + str(ist_time)

	engagementDailyRecord = frappe.get_doc("Engagement Daily Record", dailyRecordId)

	activity_entry = {
		"activity": activityName,
		"completion_time": inputTime,
	}

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


@frappe.whitelist()
def createDailyRecord(engagement, caregiver):
	import pytz
	from datetime import datetime

	ist_datetime = (
		str(datetime.now(pytz.timezone("Asia/Kolkata")).date())
		+ " "
		+ str(datetime.now(pytz.timezone("Asia/Kolkata")).time())
	)

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
	import pytz
	from datetime import datetime

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


@frappe.whitelist(allow_guest=True)
def update_caregiver_response(response_id):
	"""
	This API endpoint updates the Caregiver Response document
	corresponding to the given response_id. It sets the status to "Accepted"
	and logs the current time in response_time.
	"""
	from frappe.utils import now

	if not response_id:
		frappe.throw("Missing response ID in the URL.", title="Error")

	try:
		doc = frappe.get_doc("Caregiver Response", response_id)
	except frappe.DoesNotExistError:
		frappe.throw(
			f"No Caregiver Response found with ID {response_id}", title="Error"
		)
	except Exception:
		frappe.throw("Something went wrong. Contact support.", title="Error")

	try:
		doc.flags.ignore_permissions = True
		doc.status = "Accepted"
		doc.response_time = now()
		doc.save()
		frappe.db.commit()
	except Exception:
		frappe.throw("Failed to update response.", title="Error")

	return "success"

