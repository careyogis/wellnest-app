import frappe
import json
from frappe.utils import now_datetime, add_days


@frappe.whitelist()
def get_dashboard_data():
    consultations = (
        get_consultation_alerts()
        + get_not_started_consultation_alerts()
            )
    payments = get_payment_alerts()
    doctor_health = get_doctor_onboarding_alerts()
    customer_journey = get_customer_journey_alerts()

    all_alerts = consultations + payments + doctor_health + customer_journey

    summary = {
        "critical": sum(1 for a in all_alerts if a["priority"] == "Critical"),
        "high": sum(1 for a in all_alerts if a["priority"] == "High"),
        "medium": sum(1 for a in all_alerts if a["priority"] == "Medium"),
        "total": len(all_alerts),
    }

    return {
        "summary": summary,
        "alerts": all_alerts,
        "consultations": consultations,
        "payments": payments,
        "doctor_onboarding": doctor_health,
        "customer_journey": customer_journey,
    }


def get_consultation_alerts():
    alerts = []

    # Scenario 1: Prescription Processing Error
    failed_prescriptions = frappe.get_all(
        "Smart Prescription",
        filters={"workflow_state": "Failed"},
        fields=["name", "patient_appointment", "modified"],
        order_by="modified desc",
    )

    for prescription in failed_prescriptions:
        appointment = frappe.db.get_value(
            "Patient Appointment",
            prescription.patient_appointment,
            ["practitioner", "patient"],
            as_dict=True,
        )

        doctor_name = "-"
        customer_name = "-"

        if appointment:
            if appointment.get("practitioner"):
                doctor = frappe.db.get_value(
                    "Practitioner",
                    appointment.practitioner,
                    ["first_name", "last_name"],
                    as_dict=True,
                )
                if doctor:
                    doctor_name = f"{doctor.first_name or ''} {doctor.last_name or ''}".strip()
                else:
                    doctor_name = appointment.practitioner

            if appointment.get("patient"):
                customer_name = (
                    frappe.db.get_value(
                        "Patient",
                        appointment.patient,
                        "full_name",
                    )
                    or appointment.patient
                )

        alerts.append({
            "priority": "High",
            "category": "Consultation",
            "alert": "Prescription Processing Error",
            "doctor": doctor_name,
            "customer": customer_name,
            "time": str(prescription.modified),
            "action": "Retry • Manual review • Escalate to tech team",
            "reference": prescription.name,
        })

    # Scenario 2: Prescription Pending
    threshold = add_days(now_datetime(), -1)

    completed_appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "status": "Completed",
            "scheduled_time": ["<=", threshold],
        },
        fields=["name", "practitioner", "patient", "scheduled_time"],
        order_by="scheduled_time desc",
    )

    for appointment in completed_appointments:

        completed_prescription = frappe.db.exists(
            "Smart Prescription",
            {
                "patient_appointment": appointment.name,
                "workflow_state": "Complete",
            },
        )

        if completed_prescription:
            continue

        doctor_name = "-"
        customer_name = "-"

        if appointment.get("practitioner"):
            doctor = frappe.db.get_value(
                "Practitioner",
                appointment.practitioner,
                ["first_name", "last_name"],
                as_dict=True,
            )
            if doctor:
                doctor_name = f"{doctor.first_name or ''} {doctor.last_name or ''}".strip()
            else:
                doctor_name = appointment.practitioner

        if appointment.get("patient"):
            customer_name = (
                frappe.db.get_value(
                    "Patient",
                    appointment.patient,
                    "full_name",
                )
                or appointment.patient
            )

        alerts.append({
            "priority": "High",
            "category": "Consultation",
            "alert": "Prescription Pending",
            "doctor": doctor_name,
            "customer": customer_name,
            "time": str(appointment.scheduled_time),
            "action": "Contact doctor • Send reminder • Escalate",
            "reference": appointment.name,
        })

    # Scenario 3: Customer Reported Doctor No Show
    no_show_appointments = frappe.get_all(
        "Patient Appointment",
        filters={"status": "No Show"},
        fields=["name", "practitioner", "patient", "modified"],
        order_by="modified desc",
    )

    for appointment in no_show_appointments:
        doctor_name = "-"
        customer_name = "-"

        if appointment.get("practitioner"):
            doctor = frappe.db.get_value(
                "Practitioner",
                appointment.practitioner,
                ["first_name", "last_name"],
                as_dict=True,
            )
            if doctor:
                doctor_name = f"{doctor.first_name or ''} {doctor.last_name or ''}".strip()
            else:
                doctor_name = appointment.practitioner

        if appointment.get("patient"):
            customer_name = (
                frappe.db.get_value(
                    "Patient",
                    appointment.patient,
                    "full_name",
                )
                or appointment.patient
            )

        alerts.append({
            "priority": "Critical",
            "category": "Consultation",
            "alert": "Doctor No Show",
            "doctor": doctor_name,
            "customer": customer_name,
            "time": str(appointment.modified),
            "action": "Call doctor • Reassign consultation • Offer reschedule",
            "reference": appointment.name,
        })

    # Scenario 4: Other Appointment Status Alerts
    status_appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "status": ["in", ["Unverified", "In-Progress", "Cancelled", "Cancelled by Doctor"]]
        },
        fields=["name", "practitioner", "patient", "status", "modified"],
        order_by="modified desc",
    )

    for appointment in status_appointments:
        doctor_name = "-"
        customer_name = "-"

        if appointment.get("practitioner"):
            doctor = frappe.db.get_value(
                "Practitioner",
                appointment.practitioner,
                ["first_name", "last_name"],
                as_dict=True,
            )
            if doctor:
                doctor_name = f"{doctor.first_name or ''} {doctor.last_name or ''}".strip()
            else:
                doctor_name = appointment.practitioner

        if appointment.get("patient"):
            customer_name = (
                frappe.db.get_value(
                    "Patient",
                    appointment.patient,
                    "full_name",
                )
                or appointment.patient
            )

        if appointment.status == "Unverified":
            priority = "Medium"
            alert = "Appointment Pending Verification"
            action = "Verify booking"

        elif appointment.status == "In-Progress":
            priority = "Medium"
            alert = "Consultation In Progress"
            action = "Monitor consultation"

        else:  # Cancelled & Cancelled by Doctor
            priority = "Medium"
            alert = "Consultation Cancelled"
            action = "Contact customer • Offer reschedule"

        alerts.append({
            "priority": priority,
            "category": "Consultation",
            "alert": alert,
            "doctor": doctor_name,
            "customer": customer_name,
            "time": str(appointment.modified),
            "action": action,
            "reference": appointment.name,
        })

    return alerts

def get_not_started_consultation_alerts():
    alerts = []

    appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "status": "Scheduled",
            "scheduled_time": ["<", now_datetime()],
        },
        fields=["name", "patient", "practitioner", "scheduled_time"],
        order_by="scheduled_time desc",
    )

    for appointment in appointments:
        call_activity = frappe.db.exists(
            "Event Log",
            {
                "reference_name": appointment.name,
                "event_category": "Teleconsultation",
                "event_name": ["in", [
                    "doctor_joined_rtc_channel",
                    "patient_joined_rtc_channel",
                    "doctor_left_rtc_channel",
                    "patient_left_rtc_channel",
                    "call_ended",
                ]],
            },
        )

        if call_activity:
            continue

        doctor_name = "-"
        customer_name = "-"

        if appointment.practitioner:
            doctor = frappe.db.get_value(
                "Practitioner",
                appointment.practitioner,
                ["first_name", "last_name"],
                as_dict=True,
            )
            if doctor:
                doctor_name = f"{doctor.first_name or ''} {doctor.last_name or ''}".strip()

        if appointment.patient:
            customer_name = (
                frappe.db.get_value(
                    "Patient",
                    appointment.patient,
                    "full_name",
                )
                or appointment.patient
            )

        alerts.append({
            "priority": "High",
            "category": "Consultation",
            "alert": "Consultation Not Started",
            "doctor": doctor_name,
            "customer": customer_name,
            "time": str(appointment.scheduled_time),
            "action": "Contact customer • Contact doctor",
            "reference": appointment.name,
        })

    return alerts

def get_payment_alerts():
    alerts = []

    unpaid_appointments = frappe.get_all(
        "Patient Appointment",
        filters={"payment_status": "Unpaid"},
        fields=["name", "patient", "payment_status", "modified"],
        order_by="modified desc",
    )

    for appointment in unpaid_appointments:
        customer_name = "-"

        if appointment.get("patient"):
            customer_name = (
                frappe.db.get_value(
                    "Patient",
                    appointment.patient,
                    "full_name",
                )
                or appointment.patient
            )

        alerts.append({
            "priority": "Medium",
            "category": "Payment",
            "alert": "Payment Pending",
            "customer": customer_name,
            "doctor": "-",
            "time": str(appointment.modified),
            "action": "Retry payment • Contact customer",
            "reference": appointment.name,
        })

    return alerts

def get_doctor_onboarding_alerts():
    alerts = []

    practitioners = frappe.get_all(
        "Practitioner",
        fields=[
            "name",
            "first_name",
            "last_name",
            "registration_no",
            "photo",
            "practicing_from",
            "online_charge",
            "is_active",
        ],
    )

    for practitioner in practitioners:
        doctor_name = f"{practitioner.first_name or ''} {practitioner.last_name or ''}".strip()

        missing_fields = []

        if not practitioner.registration_no:
            missing_fields.append("Registration No")

        if not practitioner.photo:
            missing_fields.append("Profile Photo")

        if not practitioner.practicing_from:
            missing_fields.append("Practicing From")

        if not practitioner.online_charge:
            missing_fields.append("Online Consultation Fee")

        # Child table checks
        education_count = frappe.db.count(
            "Practitioner Education",
            {"parent": practitioner.name}
        )

        availability_count = frappe.db.count(
            "Availability Slots",
            {"parent": practitioner.name}
        )

        if education_count == 0:
            missing_fields.append("Qualifications")

        if availability_count == 0:
            missing_fields.append("Availability Slots")

        if missing_fields:
            alerts.append({
                "priority": "High",
                "category": "Doctor Onboarding",
                "alert": "Incomplete Profile",
                "doctor": doctor_name or practitioner.name,
                "details": ", ".join(missing_fields),
                "action": "Contact doctor",
                "reference": practitioner.name,
            })

        # Scenario: Doctor Never Activated
        if practitioner.is_active:
            completed = frappe.db.exists(
                "Patient Appointment",
                {
                    "practitioner": practitioner.name,
                    "status": "Completed",
                },
            )

            if not completed:
                alerts.append({
                    "priority": "Medium",
                    "category": "Doctor Onboarding",
                    "alert": "Doctor Never Activated",
                    "doctor": doctor_name or practitioner.name,
                    "details": "No completed consultation yet.",
                    "action": "Contact doctor",
                    "reference": practitioner.name,
                })

    return alerts


def get_customer_journey_alerts():
    alerts = []

    events = frappe.get_all(
        "Event Log",
        filters={"event_category": "Teleconsultation"},
        fields=["event_name", "reference_name", "creation", "data"],
        order_by="creation desc",
        limit=50,
    )

    for event in events:
        appointment = frappe.db.get_value(
            "Patient Appointment",
            event.reference_name,
            ["patient", "practitioner"],
            as_dict=True,
        )

        customer_name = "-"
        doctor_name = "-"
        details = "-"

        if appointment:
            if appointment.get("patient"):
                customer_name = (
                    frappe.db.get_value("Patient", appointment.patient, "full_name")
                    or appointment.patient
                )

            if appointment.get("practitioner"):
                practitioner = frappe.db.get_value(
                    "Practitioner",
                    appointment.practitioner,
                    ["first_name", "last_name"],
                    as_dict=True,
                )

                if practitioner:
                    doctor_name = f"{practitioner.first_name or ''} {practitioner.last_name or ''}".strip()

        mapping = {
            "patient_reported_noshow": (
                "Critical",
                "Patient No Show",
                "Follow-up call • Reschedule",
            ),
            "network_quality_degraded": (
                "Medium",
                "Consultation Interrupted",
                "Contact customer • Verify completion",
            ),
            "doctor_left_rtc_channel": (
                "Medium",
                "Doctor Left Consultation",
                "Verify consultation completion",
            ),
            "patient_exiting_call": (
                "Medium",
                "Patient Exited Consultation",
                "Verify consultation completion",
            ),
        }

        if event.event_name not in mapping:
            continue

        priority, alert_name, action = mapping[event.event_name]

        if event.data:
            try:
                payload = json.loads(event.data)

                if event.event_name == "doctor_left_rtc_channel":
                    details = f"Duration: {payload.get('duration_seconds', 0)} sec"

                elif event.event_name == "network_quality_degraded":
                    details = f"Quality: {payload.get('quality_level', 'Unknown')}"

                elif event.event_name == "patient_reported_noshow":
                    details = "Reported by customer"

                elif event.event_name == "patient_exiting_call":
                    details = "Patient exited the consultation"

            except Exception:
                details = event.data

        alerts.append(
            {
                "priority": priority,
                "category": "Customer Journey",
                "alert": alert_name,
                "doctor": doctor_name,
                "customer": customer_name,
                "time": str(event.creation),
                "details": details,
                "action": action,
                "reference": event.reference_name,
            }
        )

    return alerts