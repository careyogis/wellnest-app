# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def check_patient_appointment(patient_appointment):
	"""Check if an associated Smart Prescription exists for the given Patient Appointment.

	Returns appointment info and whether a Smart Prescription is already linked.
	"""
	if not patient_appointment:
		return {
			"has_smart_prescription": False,
			"smart_prescriptions": [],
		}

	# Check for existing Smart Prescription linked to this appointment
	existing_prescriptions = frappe.get_all(
		"Smart Prescription",
		filters={"patient_appointment": patient_appointment},
		fields=["name", "workflow_state", "prescription_date", "patient", "practitioner"],
		order_by="creation desc",
	)

	if existing_prescriptions:
		return {
			"has_smart_prescription": True,
			"smart_prescriptions": existing_prescriptions,
		}

	# If no prescription, fetch appointment details to display to the user
	appointment_doc = frappe.get_value("Patient Appointment", patient_appointment, ["patient", "patient.full_name AS patient_name", "practitioner", "practitioner.full_name AS practitioner_name", "scheduled_time", "status"], as_dict=True)

	# if not patient_name and appointment_doc.patient:
	# 	patient_name = frappe.db.get_value("Patient", appointment_doc.patient, "patient_name") or appointment_doc.patient

	return {
		"has_smart_prescription": False,
		"smart_prescriptions": [],
		"patient": appointment_doc.patient,
		"patient_name": appointment_doc.patient_name,
		"practitioner": getattr(appointment_doc, "practitioner", None),
		"practitioner_name": appointment_doc.practitioner_name,
		"appointment_time": str(getattr(appointment_doc, "scheduled_time", "")),
		"status": getattr(appointment_doc, "status", ""),
	}
