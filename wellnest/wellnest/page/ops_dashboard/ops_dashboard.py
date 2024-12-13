import frappe

@frappe.whitelist()
def get_dashboard_data(filters=None, limit=10, offset=0):
    caregivers_data = []
    customers_data = []

    # Parse filters if provided
    filters = frappe.parse_json(filters) if filters else {}

    # Fetch Caregiver Details
    caregivers_query = """
        SELECT 
            caregiver.name AS caregiver_name,
            caregiver.caregiver_type AS caregiver_type
        FROM `tabCaregiver` caregiver
        LIMIT %s OFFSET %s
    """ % (limit, offset)

    caregivers = frappe.db.sql(caregivers_query, as_dict=True)

    for caregiver in caregivers:
        # Get the last engagement for each caregiver
        last_engagement = frappe.db.sql("""
            SELECT 
                engagement.start_date AS last_engagement
            FROM `tabEngagement` engagement
            WHERE engagement.name IN (
                SELECT caregiver.parent FROM `tabEngagement Caregiver` caregiver
                WHERE caregiver.caregiver = %s
            )
            ORDER BY engagement.start_date DESC
            LIMIT 1
        """, (caregiver['caregiver_name']), as_dict=True)

        last_engagement_date = last_engagement[0]['last_engagement'] if last_engagement else '-'

        # Determine engagement status
        engagement_status = 'Engaged' if last_engagement else 'Not Engaged'

        # Fetch payments for this caregiver
        paid_amount = frappe.db.sql("""
            SELECT SUM(IFNULL(paid_amount, 0)) AS paid_amount
            FROM `tabPurchase Invoice`
            WHERE supplier_name = %s
              AND docstatus = 1
        """, (caregiver['caregiver_name']), as_dict=True)

        paid_amount_value = paid_amount[0]['paid_amount'] if paid_amount else 0

        # Fetch due amounts
        due_amount = frappe.db.sql("""
            SELECT SUM(grand_total - IFNULL(paid_amount, 0)) AS due_amount
            FROM `tabPurchase Invoice`
            WHERE supplier_name = %s
              AND docstatus = 1
              AND status != 'Paid'
        """, (caregiver['caregiver_name']), as_dict=True)

        due_amount_value = due_amount[0]['due_amount'] if due_amount else 0

        caregivers_data.append({
            'caregiver_name': caregiver['caregiver_name'],
            'caregiver_type': caregiver['caregiver_type'],
            'last_engagement': last_engagement_date,
            'engagement_status': engagement_status,
            'due_amount': due_amount_value,
            'paid_amount': paid_amount_value,
        })

    # Fetch Customer Details
    customers_query = """
        SELECT 
            customer.name AS customer_name
        FROM `tabCustomer` customer
        LIMIT %s OFFSET %s
    """ % (limit, offset)

    customers = frappe.db.sql(customers_query, as_dict=True)

    for customer in customers:
        # Fetch engaged caregivers for each customer
        engaged_caregivers = frappe.db.sql("""
            SELECT COUNT(DISTINCT caregiver.name) AS engaged_caregivers
            FROM `tabEngagement Caregiver` caregiver
            INNER JOIN `tabEngagement` engagement
                ON caregiver.parent = engagement.name
            WHERE engagement.customer = %s
        """, (customer['customer_name']), as_dict=True)

        engaged_caregivers_count = engaged_caregivers[0]['engaged_caregivers'] if engaged_caregivers else 0

        # Determine engagement status
        customer_engagement_status = 'Engaged' if engaged_caregivers_count > 0 else 'Not Engaged'

        # Fetch payments made by the customer
        paid_amount = frappe.db.sql("""
            SELECT SUM(IFNULL(paid_amount, 0)) AS paid_amount
            FROM `tabSales Invoice`
            WHERE customer = %s
              AND docstatus = 1
        """, (customer['customer_name']), as_dict=True)

        paid_amount_value = paid_amount[0]['paid_amount'] if paid_amount else 0

        # Fetch due amounts
        due_amount = frappe.db.sql("""
            SELECT SUM(grand_total - IFNULL(paid_amount, 0)) AS due_amount
            FROM `tabSales Invoice`
            WHERE customer = %s
              AND docstatus = 1
              AND status != 'Paid'
        """, (customer['customer_name']), as_dict=True)

        due_amount_value = due_amount[0]['due_amount'] if due_amount else 0

        customers_data.append({
            'customer_name': customer['customer_name'],
            'engaged_caregivers': engaged_caregivers_count,
            'engagement_status': customer_engagement_status,
            'due_amount': due_amount_value,
            'paid_amount': paid_amount_value,
        })

    return {
        'caregivers': caregivers_data,
        'customers': customers_data,
        'total_items': max(len(caregivers_data), len(customers_data))
    }
