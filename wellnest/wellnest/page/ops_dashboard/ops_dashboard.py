import frappe
from frappe import _

@frappe.whitelist()
def get_dashboard_data(filters=None, limit=10, offset=0):
    """
    API method to fetch caregiver and customer data for Ops Dashboard.
    Filters can include 'caregiver_name' and 'customer_name'.
    """
    filters = frappe.parse_json(filters) if filters else {}
    limit = int(limit)
    offset = int(offset)

    caregivers = fetch_caregivers(filters.get('caregiver_name'), limit, offset)
    customers = fetch_customers(filters.get('customer_name'), limit, offset)

    # Fetch caregiver-specific amounts
    total_accrued_amounts = fetch_total_accrued_amount()
    invoice_raised_data = fetch_invoice_raised_amount()
    due_amount_data = fetch_due_amount()
    paid_amount_data = fetch_paid_amount()

    # Merge caregiver data
    for caregiver in caregivers:
        caregiver_name = caregiver['caregiver_name']

        accrued_amount = next(
            (item['total_accrued_amount'] for item in total_accrued_amounts if item['caregiver_name'] == caregiver_name), 0
        )
        caregiver['total_accrued_amount'] = accrued_amount

        invoice_raised = next(
            (item['invoice_raised'] for item in invoice_raised_data if item['caregiver_name'] == caregiver_name), 0
        )
        caregiver['invoice_raised'] = invoice_raised

        due_amount = next(
            (item['due_amount'] for item in due_amount_data if item['caregiver_name'] == caregiver_name), 0
        )
        caregiver['due_amount'] = due_amount

        paid_amount = next(
            (item['paid_amount'] for item in paid_amount_data if item['caregiver_name'] == caregiver_name), 0
        )
        caregiver['paid_amount'] = paid_amount

    # Fetch customer-specific amounts
    invoice_totals = {item['customer_name']: item['invoice_raised'] for item in fetch_customer_invoice_raised()}
    paid_totals = {item['customer_name']: item['paid_amount'] for item in fetch_customer_paid_amount()}
    outstanding_totals = {item['customer_name']: item['outstanding_total'] for item in fetch_customer_outstanding()}

    # Merge customer data
    for customer in customers:
        customer_name = customer['customer_name']
        customer['invoice_total'] = invoice_totals.get(customer_name, 0)  # Invoice Raised (Unpaid/Overdue)
        customer['paid_total'] = paid_totals.get(customer_name, 0)        # Paid Amount
        customer['outstanding_total'] = outstanding_totals.get(customer_name, 0)  # Outstanding Amount

    has_more_caregivers = len(caregivers) == limit
    has_more_customers = len(customers) == limit

    return {
        "caregivers": caregivers,
        "customers": customers,
        "has_more": has_more_caregivers or has_more_customers
    }

# Caregiver Functions
def fetch_caregivers(caregiver_name_filter, limit, offset):
    conditions = "1=1"
    params = {"limit": limit, "offset": offset}

    if caregiver_name_filter:
        conditions += " AND caregiver.full_name LIKE %(caregiver_name)s"
        params["caregiver_name"] = f"%{caregiver_name_filter}%"

    query = f"""
        SELECT 
            caregiver.full_name AS caregiver_name,
            caregiver.caregiver_type,
            MAX(ec.start_date) AS last_engagement,
            CASE 
                WHEN MAX(ec.end_date) >= CURDATE() THEN 'Engaged'
                ELSE 'Not Engaged'
            END AS status,
            (
                SELECT ec.parent
                FROM `tabEngagement Caregiver` ec
                WHERE ec.caregiver = caregiver.name
                ORDER BY ec.start_date DESC, ec.creation DESC
                LIMIT 1
            ) AS engagement_id
        FROM `tabCaregiver` caregiver
        LEFT JOIN `tabEngagement Caregiver` ec ON ec.caregiver = caregiver.name
        WHERE {conditions}
        GROUP BY caregiver.full_name, caregiver.caregiver_type
        LIMIT %(limit)s OFFSET %(offset)s
    """
    return frappe.db.sql(query, params, as_dict=True)


def fetch_total_accrued_amount():
    query = """
        SELECT 
            caregiver.full_name AS caregiver_name,
            SUM(
                (DATEDIFF(ec.end_date, ec.start_date) + 1) * ec.daily_rate
            ) AS total_accrued_amount
        FROM `tabEngagement Caregiver` ec
        LEFT JOIN `tabCaregiver` caregiver ON ec.caregiver = caregiver.name
        WHERE ec.start_date IS NOT NULL AND ec.end_date IS NOT NULL
        GROUP BY caregiver.full_name
    """
    return frappe.db.sql(query, as_dict=True)

def fetch_invoice_raised_amount():
    query = """
        SELECT 
            supplier_name AS caregiver_name,
            SUM(grand_total) AS invoice_raised
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1
        AND status IN ('Unpaid', 'Overdue')
        GROUP BY supplier_name
    """
    return frappe.db.sql(query, as_dict=True)

def fetch_due_amount():
    query = """
        SELECT 
            supplier_name AS caregiver_name,
            SUM(outstanding_amount) AS due_amount
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1
        AND status IN ('Unpaid', 'Overdue')
        GROUP BY supplier_name
    """
    return frappe.db.sql(query, as_dict=True)

def fetch_paid_amount():
    query = """
        SELECT 
            supplier_name AS caregiver_name,
            SUM(grand_total) - SUM(outstanding_amount) AS paid_amount
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1
        AND status = 'Paid'
        GROUP BY supplier_name
    """
    return frappe.db.sql(query, as_dict=True)

def fetch_customers(customer_name_filter, limit, offset):
    conditions = "1=1"
    params = {"limit": limit, "offset": offset}

    if customer_name_filter:
        conditions += " AND customer.name LIKE %(customer_name)s"
        params["customer_name"] = f"%{customer_name_filter}%"

    query = f"""
        SELECT 
            customer.name AS customer_name,
            (
                SELECT COUNT(DISTINCT ec.caregiver)
                FROM `tabEngagement` engagement
                LEFT JOIN `tabEngagement Caregiver` ec ON ec.parent = engagement.name
                WHERE engagement.customer = customer.name
                AND ec.end_date >= CURDATE()
            ) AS engaged_caregivers,
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM `tabEngagement` engagement
                    LEFT JOIN `tabEngagement Caregiver` ec ON ec.parent = engagement.name
                    WHERE engagement.customer = customer.name
                    AND ec.end_date >= CURDATE()
                ) THEN 'Engaged'
                ELSE 'Not Engaged'
            END AS status,
            (
                SELECT MAX(ec.start_date)
                FROM `tabEngagement` engagement
                LEFT JOIN `tabEngagement Caregiver` ec ON ec.parent = engagement.name
                WHERE engagement.customer = customer.name
                GROUP BY engagement.customer
            ) AS last_engagement,
            (
                SELECT SUM(invoice.grand_total)
                FROM `tabSales Invoice` invoice
                WHERE invoice.customer = customer.name
                AND invoice.status IN ('Unpaid', 'Overdue') -- Include only Unpaid and Overdue statuses
            ) AS invoice_raised,
            (
                SELECT SUM(invoice.grand_total) - SUM(invoice.outstanding_amount)
                FROM `tabSales Invoice` invoice
                WHERE invoice.customer = customer.name
                AND invoice.status = 'Paid' -- Include only Paid invoices
            ) AS paid_amount,
            (
                SELECT SUM(invoice.outstanding_amount)
                FROM `tabSales Invoice` invoice
                WHERE invoice.customer = customer.name
                AND invoice.status IN ('Unpaid', 'Overdue') -- Include only Unpaid and Overdue statuses
            ) AS outstanding_total
        FROM `tabCustomer` customer
        WHERE {conditions}
        LIMIT %(limit)s OFFSET %(offset)s
    """
    return frappe.db.sql(query, params, as_dict=True)


def fetch_customer_invoice_raised():
    query = """
        SELECT 
            customer AS customer_name,
            SUM(grand_total) AS invoice_raised
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND status IN ('Unpaid', 'Overdue') -- Include only Unpaid and Overdue statuses
        GROUP BY customer
    """
    return frappe.db.sql(query, as_dict=True)


def fetch_customer_paid_amount():
    query = """
        SELECT 
            customer AS customer_name,
            SUM(grand_total) - SUM(outstanding_amount) AS paid_amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND status = 'Paid'
        GROUP BY customer
    """
    return frappe.db.sql(query, as_dict=True)

def fetch_customer_outstanding():
    query = """
        SELECT 
            customer AS customer_name,
            SUM(outstanding_amount) AS outstanding_total
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND status IN ('Unpaid', 'Overdue')
        GROUP BY customer
    """
    return frappe.db.sql(query, as_dict=True)