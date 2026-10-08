# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta
import frappe
from frappe.tests.utils import FrappeTestCase
from wellnest.services.payout import get_preceding_week_dates, get_eligible_appointments


class TestPractitionerPayout(FrappeTestCase):
    def test_preceding_week_dates(self):
        # Given a fixed reference date, e.g. Monday 2026-10-12
        start, end = get_preceding_week_dates("2026-10-12")
        # Preceding Monday should be 2026-10-05 and Sunday 2026-10-11
        self.assertEqual(start, "2026-10-05")
        self.assertEqual(end, "2026-10-11")

    def test_payout_calculations(self):
        payout = frappe.new_doc("Practitioner Payout")
        payout.cycle_start_date = "2026-10-01"
        payout.cycle_end_date = "2026-10-07"
        payout.status = "Draft"

        # Add items
        payout.append(
            "items",
            {
                "payout_rate": 500,
            },
        )
        payout.append(
            "items",
            {
                "payout_rate": 600,
            },
        )

        payout.calculate_totals()
        self.assertEqual(payout.consultation_count, 2)
        self.assertEqual(payout.gross_amount, 1100.0)
        self.assertEqual(payout.net_payable_amount, 1100.0)

        # Add adjustments
        payout.adjustments = 100
        payout.calculate_totals()
        self.assertEqual(payout.net_payable_amount, 1000.0)

    def test_date_validation(self):
        payout = frappe.new_doc("Practitioner Payout")
        payout.cycle_start_date = "2026-10-10"
        payout.cycle_end_date = "2026-10-05"  # End before start

        self.assertRaises(frappe.ValidationError, payout.validate_dates)

    def test_payment_reference_required_on_paid(self):
        payout = frappe.new_doc("Practitioner Payout")
        payout.cycle_start_date = "2026-10-01"
        payout.cycle_end_date = "2026-10-07"
        payout.status = "Paid"
        payout.payment_reference = None

        self.assertRaises(frappe.ValidationError, payout.validate_payment_info)
