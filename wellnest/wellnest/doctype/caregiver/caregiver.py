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
