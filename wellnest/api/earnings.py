# Copyright (c) 2026, CareYogi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, getdate, nowdate
from frappe.utils.pdf import get_pdf



@frappe.whitelist()
def get_doctor_earnings_summary():
    """
    Returns summary metrics for the Doctor App Earnings dashboard:
    - Accrued (unbilled) earnings
    - Last payout details
    - Lifetime earnings & consultations count
    - Linked bank account status
    """
    practitioner_id = get_current_practitioner()
    practitioner = frappe.get_doc("Practitioner", practitioner_id)
    online_charge = flt(practitioner.online_charge or 0.0)

    # 1. Accrued / Unbilled consultations
    unbilled_query = """
		SELECT
			name, scheduled_time, consultation_fee, practitioner_payout_rate
		FROM `tabPatient Appointment`
		WHERE
			practitioner = %(practitioner)s
			AND status = 'Completed'
			AND consultation_type = 'Online'
			AND payment_status = 'Paid'
			AND (payout_status = 'Accrued' OR payout_status IS NULL OR payout_status = '')
			AND (practitioner_payout IS NULL OR practitioner_payout = '')
		ORDER BY scheduled_time DESC
	"""
    unbilled_appts = frappe.db.sql(unbilled_query, {"practitioner": practitioner_id}, as_dict=True)
    accrued_count = len(unbilled_appts)
    accrued_amount = sum(
        flt(a.practitioner_payout_rate) if flt(a.practitioner_payout_rate) > 0 else online_charge
        for a in unbilled_appts
    )

    # 2. Payouts metrics (Lifetime & Last Payout)
    payouts = frappe.get_all(
        "Practitioner Payout",
        filters={"practitioner": practitioner_id, "status": "Paid"},
        fields=[
            "name",
            "net_payable_amount",
            "payout_date",
            "payment_reference",
            "payment_method",
            "cycle_start_date",
            "cycle_end_date",
            "consultation_count",
        ],
        order_by="payout_date desc, modified desc",
    )

    lifetime_earnings = sum(flt(p.net_payable_amount) for p in payouts)
    last_payout = payouts[0] if payouts else None

    # Lifetime completed consultations
    lifetime_consultations = frappe.db.count(
        "Patient Appointment",
        filters={
            "practitioner": practitioner_id,
            "status": "Completed",
            "consultation_type": "Online",
        },
    )

    # 3. Bank Account lookup via Supplier
    bank_account_info = None
    supplier = practitioner.supplier
    if supplier:
        # Check for default or linked Bank Account in ERPNext
        bank_accounts = frappe.get_all(
            "Bank Account",
            filters={"party_type": "Supplier", "party": supplier},
            fields=["name", "bank", "bank_account_no", "branch_code", "is_default"],
            order_by="is_default desc, modified desc",
            limit=1,
        )
        if bank_accounts:
            ba = bank_accounts[0]
            raw_acc = str(ba.bank_account_no or "").strip()
            masked = f"•••• {raw_acc[-4:]}" if len(raw_acc) >= 4 else raw_acc
            bank_account_info = {
                "name": ba.name,
                "bank_name": ba.bank or "Linked Bank",
                "account_number_masked": masked,
                "ifsc": ba.branch_code or "",
                "is_default": bool(ba.is_default),
            }

    return {
        "practitioner": {
            "name": practitioner.name,
            "full_name": practitioner.full_name,
            "online_charge": online_charge,
            "has_supplier": bool(supplier),
        },
        "accrued_amount": accrued_amount,
        "accrued_count": accrued_count,
        "last_payout": last_payout,
        "lifetime_earnings": lifetime_earnings,
        "lifetime_consultations": lifetime_consultations,
        "bank_account": bank_account_info,
    }


@frappe.whitelist()
def get_doctor_payout_history(page=1, page_length=20):
    """
    Returns paginated list of payout cycles for the logged-in doctor.
    """
    practitioner_id = get_current_practitioner()
    page = max(1, int(page))
    page_length = min(100, max(1, int(page_length)))
    start = (page - 1) * page_length

    payouts = frappe.get_all(
        "Practitioner Payout",
        filters={"practitioner": practitioner_id},
        fields=[
            "name",
            "cycle_start_date",
            "cycle_end_date",
            "status",
            "consultation_count",
            "gross_amount",
            "adjustments",
            "net_payable_amount",
            "payout_date",
            "payment_reference",
            "payment_method",
            "remarks",
        ],
        order_by="cycle_start_date desc, modified desc",
        start=start,
        page_length=page_length,
    )

    total_count = frappe.db.count("Practitioner Payout", filters={"practitioner": practitioner_id})

    return {
        "payouts": payouts,
        "total_count": total_count,
        "page": page,
        "page_length": page_length,
    }


@frappe.whitelist()
def get_payout_details(payout_name):
    """
    Returns full detail of a specific payout including consultation line items.
    """
    practitioner_id = get_current_practitioner()
    payout = frappe.get_doc("Practitioner Payout", payout_name)

    if payout.practitioner != practitioner_id:
        frappe.throw("You are not authorized to view this payout", frappe.PermissionError)

    items_query = """
        SELECT
            ppi.name,
            ppi.patient_appointment,
            ppi.payout_rate,
            pa.scheduled_time,
            pa.consultation_fee,
            p.full_name AS patient_name
        FROM `tabPractitioner Payout Item` ppi
        JOIN `tabPatient Appointment` pa ON ppi.patient_appointment = pa.name
        LEFT JOIN `tabPatient` p ON pa.patient = p.name
        WHERE ppi.parent = %(payout_name)s
        ORDER BY pa.scheduled_time ASC
    """
    items = frappe.db.sql(items_query, {"payout_name": payout_name}, as_dict=True)
    for it in items:
        it["consultation_fee"] = flt(it.get("consultation_fee") or 0.0)
        it["payout_rate"] = flt(it.get("payout_rate") or 0.0)

    return {
        "name": payout.name,
        "practitioner": payout.practitioner,
        "practitioner_name": payout.practitioner_name,
        "status": payout.status,
        "cycle_start_date": payout.cycle_start_date,
        "cycle_end_date": payout.cycle_end_date,
        "consultation_count": payout.consultation_count,
        "gross_amount": flt(payout.gross_amount),
        "adjustments": flt(payout.adjustments),
        "adjustment_reason": payout.adjustment_reason,
        "net_payable_amount": flt(payout.net_payable_amount),
        "payout_date": payout.payout_date,
        "payment_method": payout.payment_method,
        "payment_reference": payout.payment_reference,
        "remarks": payout.remarks,
        "items": items,
    }


@frappe.whitelist()
def get_doctor_unbilled_consultations():
    """
    Returns itemized list of completed teleconsultations currently pending payout.
    """
    practitioner_id = get_current_practitioner()
    online_charge = flt(frappe.db.get_value("Practitioner", practitioner_id, "online_charge") or 0.0)

    query = """
		SELECT
			pa.name,
			pa.patient,
			p.full_name AS patient_name,
			pa.scheduled_time,
			pa.consultation_fee,
			pa.practitioner_payout_rate,
			pa.status,
			pa.payout_status
		FROM `tabPatient Appointment` pa
		LEFT JOIN `tabPatient` p ON pa.patient = p.name
		WHERE
			pa.practitioner = %(practitioner)s
			AND pa.status = 'Completed'
			AND pa.consultation_type = 'Online'
			AND pa.payment_status = 'Paid'
			AND (pa.payout_status = 'Accrued' OR pa.payout_status IS NULL OR pa.payout_status = '')
			AND (pa.practitioner_payout IS NULL OR pa.practitioner_payout = '')
		ORDER BY pa.scheduled_time DESC
	"""
    rows = frappe.db.sql(query, {"practitioner": practitioner_id}, as_dict=True)

    for row in rows:
        if not row.practitioner_payout_rate or flt(row.practitioner_payout_rate) == 0:
            row.practitioner_payout_rate = online_charge

    return rows


@frappe.whitelist()
def download_payout_statement(payout_name):
    """
    Renders and streams PDF settlement advice for the payout.
    """
    practitioner_id = get_current_practitioner()
    payout = frappe.get_doc("Practitioner Payout", payout_name)

    if payout.practitioner != practitioner_id and frappe.session.user != "Administrator":
        frappe.throw("You are not authorized to download this statement", frappe.PermissionError)

    try:
        html = frappe.get_print(
            "Practitioner Payout",
            payout_name,
            print_format="Practitioner Payout Settlement Advice",
            as_pdf=False,
        )
    except Exception:
        # Fallback to direct HTML rendering if print format is not yet imported
        html = _render_payout_statement_html(payout)

    pdf_bytes = get_pdf(html)
    frappe.local.response.filename = f"Payout-Statement-{payout.name}.pdf"
    frappe.local.response.filecontent = pdf_bytes
    frappe.local.response.type = "pdf"

def get_current_practitioner():
    """Helper to resolve the Practitioner document for the current session user."""
    user = frappe.session.user
    practitioner = frappe.db.get_value("Practitioner", {"user_id": user}, "name")
    if not practitioner:
        frappe.throw("Practitioner profile not found for the current user", frappe.PermissionError)
    return practitioner


def _render_payout_statement_html(payout):
    """Direct HTML fallback template for settlement advice PDF."""
    items = frappe.db.sql("""
        SELECT
            ppi.patient_appointment,
            ppi.payout_rate,
            pa.scheduled_time,
            pa.consultation_fee,
            p.full_name AS patient_name
        FROM `tabPractitioner Payout Item` ppi
        JOIN `tabPatient Appointment` pa ON ppi.patient_appointment = pa.name
        LEFT JOIN `tabPatient` p ON pa.patient = p.name
        WHERE ppi.parent = %(payout_name)s
        ORDER BY pa.scheduled_time ASC
    """, {"payout_name": payout.name}, as_dict=True)

    items_rows = ""
    for idx, it in enumerate(items, 1):
        items_rows += f"""
			<tr style="border-bottom: 1px solid #e5e7eb;">
				<td style="padding: 8px 10px; color: #6b7280;">{idx}</td>
				<td style="padding: 8px 10px; font-weight: 500; color: #111827;">{it.patient_appointment}</td>
				<td style="padding: 8px 10px; color: #4b5563;">{it.scheduled_time or ""}</td>
				<td style="padding: 8px 10px; color: #111827;">{it.patient_name or ""}</td>
				<td style="padding: 8px 10px; text-align: right; color: #6b7280;">₹{flt(it.consultation_fee):,.2f}</td>
				<td style="padding: 8px 10px; text-align: right; font-weight: bold; color: #111827;">₹{flt(it.payout_rate):,.2f}</td>
			</tr>
		"""

    adjustments_row = ""
    if flt(payout.adjustments) > 0:
        adjustments_row = f"""
			<tr>
				<td style="padding: 6px 10px; color: #dc2626;">Adjustments / Deductions:</td>
				<td style="padding: 6px 10px; text-align: right; font-weight: 600; color: #dc2626;">- ₹{flt(payout.adjustments):,.2f}</td>
			</tr>
		"""

    return f"""
	<html>
	<head><meta charset="utf-8"></head>
	<body style="font-family: Arial, sans-serif; font-size: 12px; color: #333; margin: 20px;">
		<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e5e7eb; padding-bottom: 16px; margin-bottom: 20px;">
			<div>
				<h1 style="margin: 0; font-size: 22px; color: #1f2937; font-weight: bold;">CareYogi</h1>
				<p style="margin: 4px 0 0; color: #6b7280; font-size: 13px;">Practitioner Payout Settlement Advice</p>
			</div>
			<div style="text-align: right;">
				<div style="font-size: 16px; font-weight: bold; color: #111827;">{payout.name}</div>
				<div style="color: #6b7280; font-size: 12px; margin-top: 4px;">Status: <strong>{payout.status}</strong></div>
			</div>
		</div>

		<table style="width: 100%; margin-bottom: 24px; border-collapse: collapse;">
			<tr>
				<td style="width: 50%; vertical-align: top; padding-right: 12px;">
					<div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px;">
						<div style="font-size: 11px; font-weight: bold; text-transform: uppercase; color: #9ca3af; margin-bottom: 6px;">Doctor Details</div>
						<div style="font-size: 14px; font-weight: bold; color: #111827;">{payout.practitioner_name}</div>
						<div style="color: #6b7280; font-size: 11px; margin-top: 4px;">Practitioner ID: {payout.practitioner}</div>
					</div>
				</td>
				<td style="width: 50%; vertical-align: top; padding-left: 12px;">
					<div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px;">
						<div style="font-size: 11px; font-weight: bold; text-transform: uppercase; color: #9ca3af; margin-bottom: 6px;">Payout Cycle & Payment</div>
						<div style="font-size: 13px; color: #111827;">Period: <strong>{payout.cycle_start_date}</strong> to <strong>{payout.cycle_end_date}</strong></div>
						<div style="font-size: 13px; color: #111827; margin-top: 4px;">Disbursed On: <strong>{payout.payout_date or "Pending"}</strong></div>
						<div style="font-size: 12px; color: #047857; margin-top: 4px; font-weight: bold;">UTR / Ref: {payout.payment_reference or "-"}</div>
					</div>
				</td>
			</tr>
		</table>

		<table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
			<thead>
				<tr style="background: #f3f4f6; border-bottom: 2px solid #d1d5db;">
					<th style="padding: 8px 10px; text-align: left; font-size: 11px; font-weight: bold; color: #374151;">#</th>
					<th style="padding: 8px 10px; text-align: left; font-size: 11px; font-weight: bold; color: #374151;">Appointment</th>
					<th style="padding: 8px 10px; text-align: left; font-size: 11px; font-weight: bold; color: #374151;">Date & Time</th>
					<th style="padding: 8px 10px; text-align: left; font-size: 11px; font-weight: bold; color: #374151;">Patient</th>
					<th style="padding: 8px 10px; text-align: right; font-size: 11px; font-weight: bold; color: #374151;">Customer Fee</th>
					<th style="padding: 8px 10px; text-align: right; font-size: 11px; font-weight: bold; color: #374151;">Payout Rate</th>
				</tr>
			</thead>
			<tbody>
				{items_rows}
			</tbody>
		</table>

		<div style="display: flex; justify-content: flex-end;">
			<table style="width: 320px; border-collapse: collapse; margin-left: auto;">
				<tr>
					<td style="padding: 6px 10px; color: #4b5563;">Total Consultations:</td>
					<td style="padding: 6px 10px; text-align: right; font-weight: 600;">{payout.consultation_count}</td>
				</tr>
				<tr>
					<td style="padding: 6px 10px; color: #4b5563;">Gross Amount:</td>
					<td style="padding: 6px 10px; text-align: right; font-weight: 600;">₹{flt(payout.gross_amount):,.2f}</td>
				</tr>
				{adjustments_row}
				<tr style="border-top: 2px solid #111827;">
					<td style="padding: 8px 10px; font-size: 14px; font-weight: bold; color: #111827;">Net Disbursed:</td>
					<td style="padding: 8px 10px; text-align: right; font-size: 14px; font-weight: bold; color: #047857;">₹{flt(payout.net_payable_amount):,.2f}</td>
				</tr>
			</table>
		</div>

		<div style="margin-top: 40px; border-top: 1px solid #e5e7eb; padding-top: 16px; font-size: 11px; color: #9ca3af; text-align: center;">
			This is an official system-generated settlement advice from CareYogi. For any discrepancies, please reach out to CY Operations.
		</div>
	</body>
	</html>
	"""
