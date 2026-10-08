# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta
import frappe
from frappe.utils import getdate, nowdate, flt


def get_preceding_week_dates(reference_date=None):
    """
    Returns (start_date, end_date) representing the preceding week's
    Monday and Sunday.
    """
    ref = getdate(reference_date or nowdate())
    # Monday of the current week: ref - timedelta(days=ref.weekday())
    # Preceding Monday: - 7 days
    current_monday = ref - timedelta(days=ref.weekday())
    prev_monday = current_monday - timedelta(days=7)
    prev_sunday = prev_monday + timedelta(days=6)
    return prev_monday.strftime("%Y-%m-%d"), prev_sunday.strftime("%Y-%m-%d")


def get_eligible_appointments(practitioner=None, start_date=None, end_date=None):
    """
    Queries appointments eligible for doctor payout.
    Eligible criteria:
    - status == 'Completed'
    - consultation_type == 'Online'
    - payment_status == 'Paid'
    - payout_status is 'Accrued' (or empty/None)
    - practitioner_payout is not set
    """
    filters = {
        "status": "Completed",
        "consultation_type": "Online",
        "payment_status": "Paid",
    }

    if practitioner:
        filters["practitioner"] = practitioner

    conditions = [
        "(payout_status = 'Accrued' OR payout_status IS NULL OR payout_status = '')",
        "(practitioner_payout IS NULL OR practitioner_payout = '')",
    ]

    if start_date:
        conditions.append(f"scheduled_time >= '{start_date} 00:00:00'")
    if end_date:
        conditions.append(f"scheduled_time <= '{end_date} 23:59:59'")

    if practitioner:
        conditions.append(f"practitioner = '{practitioner}'")

    conditions.append("status = 'Completed'")
    conditions.append("consultation_type = 'Online'")
    conditions.append("payment_status = 'Paid'")

    where_clause = " AND ".join(conditions)
    query = f"""
		SELECT
			name, practitioner, patient, scheduled_time,
			consultation_fee, practitioner_payout_rate
		FROM `tabPatient Appointment`
		WHERE {where_clause}
		ORDER BY scheduled_time ASC
	"""

    return frappe.db.sql(query, as_dict=True)


def create_payout_for_practitioner(practitioner, start_date, end_date, appointments=None):
    """
    Creates a draft Practitioner Payout document for a doctor for the given period.
    """
    if appointments is None:
        appointments = get_eligible_appointments(
            practitioner=practitioner,
            start_date=start_date,
            end_date=end_date,
        )

    if not appointments:
        return None

    online_charge = flt(frappe.db.get_value("Practitioner", practitioner, "online_charge") or 0.0)

    items = []
    for appt in appointments:
        rate = flt(appt.practitioner_payout_rate) if flt(appt.practitioner_payout_rate) > 0 else online_charge

        items.append(
            {
                "patient_appointment": appt.name,
                "payout_rate": rate,
            }
        )

    payout = frappe.get_doc(
        {
            "doctype": "Practitioner Payout",
            "practitioner": practitioner,
            "cycle_start_date": start_date,
            "cycle_end_date": end_date,
            "status": "Draft",
            "items": items,
        }
    )
    payout.insert(ignore_permissions=True)

    # Mark appointments as In Payout
    appointment_names = [appt.name for appt in appointments]
    frappe.db.set_value(
        "Patient Appointment",
        {"name": ["in", appointment_names]},
        {
            "payout_status": "In Payout",
            "practitioner_payout": payout.name,
            "practitioner_payout_rate": online_charge,
        },
        update_modified=False,
    )

    return payout


@frappe.whitelist()
def generate_weekly_payouts(start_date=None, end_date=None):
    """
    Automated cron and Care Ops callable function to generate
    weekly payouts for all practitioners with unbilled completed appointments.
    """
    if not start_date or not end_date:
        start_date, end_date = get_preceding_week_dates()

    eligible_appts = get_eligible_appointments(start_date=start_date, end_date=end_date)
    if not eligible_appts:
        frappe.logger().info(f"No eligible teleconsultations found for period {start_date} to {end_date}.")
        return {
            "success": True,
            "message": f"No eligible teleconsultations found for period {start_date} to {end_date}.",
            "payouts_created": 0,
            "payout_names": [],
        }

    # Group by practitioner
    appts_by_doctor = {}
    for appt in eligible_appts:
        appts_by_doctor.setdefault(appt.practitioner, []).append(appt)

    created_payouts = []
    for doctor, doctor_appts in appts_by_doctor.items():
        try:
            payout = create_payout_for_practitioner(
                practitioner=doctor,
                start_date=start_date,
                end_date=end_date,
                appointments=doctor_appts,
            )
            if payout:
                created_payouts.append(payout.name)
        except Exception:
            frappe.log_error(
                title=f"Failed to create weekly payout for Practitioner {doctor}",
                message=frappe.get_traceback(),
            )

    frappe.db.commit()
    return {
        "success": True,
        "message": f"Generated {len(created_payouts)} payout batches for period {start_date} to {end_date}.",
        "payouts_created": len(created_payouts),
        "payout_names": created_payouts,
    }
