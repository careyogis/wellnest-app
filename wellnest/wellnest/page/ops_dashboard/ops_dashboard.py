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

    # Optimize lookups using dictionaries
    total_accrued_amounts_dict = {item['caregiver_name']: item['total_accrued_amount'] for item in total_accrued_amounts}
    invoice_raised_data_dict = {item['caregiver_name']: item['invoice_raised'] for item in invoice_raised_data}
    due_amount_data_dict = {item['caregiver_name']: item['due_amount'] for item in due_amount_data}
    paid_amount_data_dict = {item['caregiver_name']: item['paid_amount'] for item in paid_amount_data}

    # Merge caregiver data
    for caregiver in caregivers:
        caregiver_name = caregiver['caregiver_name']
        caregiver['total_accrued_amount'] = total_accrued_amounts_dict.get(caregiver_name, 0)
        caregiver['invoice_raised'] = invoice_raised_data_dict.get(caregiver_name, 0)
        caregiver['due_amount'] = due_amount_data_dict.get(caregiver_name, 0)
        caregiver['paid_amount'] = paid_amount_data_dict.get(caregiver_name, 0)

    # Fetch customer-specific amounts
    invoice_totals = {item['customer_name']: item['invoice_raised'] for item in fetch_customer_invoice_raised()}
    paid_totals = {item['customer_name']: item['paid_amount'] for item in fetch_customer_paid_amount()}
    outstanding_totals = {item['customer_name']: item['outstanding_total'] for item in fetch_customer_outstanding()}

    # Merge invoice raised dates
    invoice_raised_dates_dict = {item['customer_name']: item['invoice_raised_date'] for item in fetch_invoice_raised_dates()}

    # Merge customer data
    for customer in customers:
        customer_name = customer['customer_name']
        customer['invoice_total'] = invoice_totals.get(customer_name, 0)
        customer['paid_total'] = paid_totals.get(customer_name, 0)
        customer['outstanding_total'] = outstanding_totals.get(customer_name, 0)
        customer['invoice_raised_date'] = invoice_raised_dates_dict.get(customer_name, None)

    has_more_caregivers = len(caregivers) == limit
    has_more_customers = len(customers) == limit
    

    return {
    "caregivers": caregivers,
    "customers": customers,
    "has_more": has_more_caregivers or has_more_customers  # Combine both flags
}


def fetch_invoice_raised_dates():
    query = """
        SELECT 
            si.customer AS customer_name, 
            MAX(si.posting_date) AS invoice_raised_date
        FROM `tabSales Invoice` si
        WHERE si.customer IS NOT NULL 
            AND si.docstatus = 1  -- Only submitted invoices
        GROUP BY si.customer
    """
    invoice_raised_dates = frappe.db.sql(query, as_dict=True)
    return invoice_raised_dates

@frappe.whitelist()
def get_assigned_caregivers(customer_name):
    try:
        frappe.logger().info(f"Fetching assigned caregivers for customer: {customer_name}")

        # Query to fetch caregiver names assigned to the customer's engagements
        assigned_caregivers = frappe.db.sql("""
            SELECT 
                caregiver.full_name AS caregiver_name
            FROM `tabEngagement` e
            INNER JOIN `tabEngagement Caregiver` ec ON ec.parent = e.name
            INNER JOIN `tabCaregiver` caregiver ON ec.caregiver = caregiver.name
            WHERE e.customer = %s
            ORDER BY caregiver.full_name
        """, (customer_name,), as_dict=True)

        frappe.logger().info(f"Assigned caregivers fetched: {assigned_caregivers}")

        # Return only the names of the assigned caregivers
        return [caregiver['caregiver_name'] for caregiver in assigned_caregivers] or []
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Ops Dashboard: get_assigned_caregivers")
        frappe.throw(_("An error occurred while fetching assigned caregivers for the customer."))


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
            caregiver_name,
            SUM(total_accrued_amount) - SUM(paid_amount) AS due_amount
        FROM (
            -- Fetch total accrued amount per caregiver
            SELECT 
                caregiver.full_name AS caregiver_name,
                SUM((DATEDIFF(ec.end_date, ec.start_date) + 1) * ec.daily_rate) AS total_accrued_amount,
                0 AS paid_amount
            FROM `tabEngagement Caregiver` ec
            LEFT JOIN `tabCaregiver` caregiver ON ec.caregiver = caregiver.name
            WHERE ec.start_date IS NOT NULL AND ec.end_date IS NOT NULL
            GROUP BY caregiver.full_name

            UNION ALL

            -- Fetch paid amount from purchase invoices
            SELECT 
                pi.supplier_name AS caregiver_name,
                0 AS total_accrued_amount,
                SUM(pi.grand_total) - SUM(pi.outstanding_amount) AS paid_amount
            FROM `tabPurchase Invoice` pi
            WHERE pi.docstatus = 1
            AND pi.status = 'Paid'
            GROUP BY pi.supplier_name
        ) AS combined
        GROUP BY caregiver_name
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



# fetching Customer Details
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
                SELECT MAX(e.end_date)  
                FROM `tabEngagement` e
                WHERE e.customer = customer.name
            ) AS last_engagement,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM `tabEngagement` e
                    WHERE e.customer = customer.name
                    AND e.end_date IS NULL
                ) THEN 'Engaged'
                ELSE 'Not Engaged'
            END AS status,
            (
                SELECT SUM(invoice.grand_total)
                FROM `tabSales Invoice` invoice
                WHERE invoice.customer = customer.name
                AND invoice.status IN ('Unpaid', 'Overdue')
            ) AS invoice_raised,
            (
                SELECT SUM(invoice.grand_total) - SUM(invoice.outstanding_amount)
                FROM `tabSales Invoice` invoice
                WHERE invoice.customer = customer.name
                AND invoice.status = 'Paid'
            ) AS paid_amount,
            (
                SELECT SUM(invoice.outstanding_amount)
                FROM `tabSales Invoice` invoice
                WHERE invoice.customer = customer.name
                AND invoice.status IN ('Unpaid', 'Overdue')
            ) AS outstanding_total,
            (
                SELECT GROUP_CONCAT(DISTINCT caregiver.full_name SEPARATOR ', ')
                FROM `tabEngagement` e
                INNER JOIN `tabEngagement Caregiver` ec ON ec.parent = e.name
                INNER JOIN `tabCaregiver` caregiver ON ec.caregiver = caregiver.name
                WHERE e.customer = customer.name
            ) AS assigned_caregivers
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



@frappe.whitelist()
def get_engagements_for_caregiver(caregiver_name):
    try:
        frappe.logger().info(f"Fetching engagements, invoices, and payments for caregiver (full name): {caregiver_name}")

        # Engagements Query (unchanged)
        engagements = frappe.db.sql("""
            SELECT 
                e.name AS engagement_id,
                ec.start_date,
                ec.end_date
            FROM `tabEngagement` e
            INNER JOIN `tabEngagement Caregiver` ec ON e.name = ec.parent
            INNER JOIN `tabCaregiver` c ON ec.caregiver = c.name
            WHERE c.full_name = %s
            ORDER BY e.creation DESC
        """, (caregiver_name,), as_dict=True)

        frappe.logger().info(f"Engagements fetched: {engagements}")

        # Invoice Query (grouped by supplier_name)
        invoices = frappe.db.sql("""
            SELECT 
                supplier_name AS caregiver_name,
                SUM(outstanding_amount) AS outstanding_amount
            FROM `tabPurchase Invoice`
            WHERE docstatus = 1
            AND status IN ('Unpaid', 'Overdue')
            AND supplier_name = %s
            GROUP BY supplier_name
        """, (caregiver_name,), as_dict=True)

        frappe.logger().info(f"Invoices fetched: {invoices}")

        # Payments Query (grouped by supplier_name)
        payments = frappe.db.sql("""
            SELECT 
                supplier_name AS caregiver_name,
                SUM(grand_total) AS amount_paid
            FROM `tabPurchase Invoice`
            WHERE docstatus = 1
            AND status = 'Paid'
            AND supplier_name = %s
            GROUP BY supplier_name
        """, (caregiver_name,), as_dict=True)

        frappe.logger().info(f"Payments fetched: {payments}")

        # Return data
        return {
            "engagements": engagements or [],
            "invoices": invoices[0] if invoices else {"caregiver_name": caregiver_name, "outstanding_amount": 0},
            "payments": payments[0] if payments else {"caregiver_name": caregiver_name, "amount_paid": 0},
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Ops Dashboard: get_engagements_for_caregiver")
        frappe.throw(_("An error occurred while fetching engagements, invoices, and payments for the caregiver."))

