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

    # Determine if more data exists for pagination
    has_more_caregivers = len(caregivers) == limit
    has_more_customers = len(customers) == limit

    return {
        "caregivers": caregivers,
        "customers": customers,
        "has_more": has_more_caregivers or has_more_customers
    }

def fetch_caregivers(caregiver_name_filter, limit, offset):
    """
    Fetch caregivers with payments calculated from the Purchase Invoice doctype.
    Status: 'Engaged' if service dates are current, else 'Not Engaged'.
    """
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
            COALESCE(SUM(CASE 
                WHEN pi.outstanding_amount = 0 THEN pi.grand_total
                ELSE 0
            END), 0) AS paid_amount,
            COALESCE(SUM(CASE 
                WHEN pi.outstanding_amount > 0 THEN pi.outstanding_amount
                ELSE 0
            END), 0) AS due_amount
        FROM `tabCaregiver` caregiver
        LEFT JOIN `tabEngagement Caregiver` ec ON ec.caregiver = caregiver.name
        LEFT JOIN `tabEngagement` engagement ON ec.parent = engagement.name
        LEFT JOIN `tabPurchase Invoice` pi 
            ON pi.supplier_name = caregiver.full_name 
            AND pi.status IN ('Paid', 'Overdue', 'Unpaid')
        WHERE {conditions}
        GROUP BY caregiver.full_name, caregiver.caregiver_type
        LIMIT %(limit)s OFFSET %(offset)s
    """
    return frappe.db.sql(query, params, as_dict=True)

def fetch_customers(customer_name_filter, limit, offset):
    """
    Fetch customers with caregiver count, payments, and status.
    Status: 'Engaged' if there are active caregivers, else 'Not Engaged'.
    """
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
            COALESCE(SUM(CASE 
                WHEN si.outstanding_amount = 0 THEN si.grand_total
                ELSE 0
            END), 0) AS paid_amount,
            COALESCE(SUM(CASE 
                WHEN si.outstanding_amount > 0 THEN si.outstanding_amount
                ELSE 0
            END), 0) AS due_amount
        FROM `tabCustomer` customer
        LEFT JOIN `tabSales Invoice` si 
            ON si.customer = customer.name 
            AND si.status IN ('Paid', 'Overdue', 'Unpaid')
        WHERE {conditions}
        GROUP BY customer.name
        LIMIT %(limit)s OFFSET %(offset)s
    """
    return frappe.db.sql(query, params, as_dict=True)
