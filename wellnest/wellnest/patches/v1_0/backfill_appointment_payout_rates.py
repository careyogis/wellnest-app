# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute():
    """
    Backfill existing completed teleconsultations with their doctor's online_charge
    and set payout_status to 'Accrued' so they become eligible for payout cycles.
    """
    appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "status": "Completed",
            "consultation_type": "Online",
            "payment_status": "Paid",
        },
        fields=["name", "practitioner", "practitioner_payout_rate", "payout_status"],
    )

    for appt in appointments:
        if not appt.payout_status:
            online_charge = frappe.db.get_value("Practitioner", appt.practitioner, "online_charge") or 0.0
            frappe.db.set_value(
                "Patient Appointment",
                appt.name,
                {
                    "practitioner_payout_rate": flt(appt.practitioner_payout_rate or online_charge),
                    "payout_status": "Accrued",
                },
                update_modified=False,
            )

    frappe.db.commit()
