import frappe

@frappe.whitelist()
def get_dashboard_data():
    caregivers_data = []
    customers_data = []

    # Fetch Caregiver Details
    caregivers = frappe.db.sql("""
        SELECT 
            caregiver.name AS caregiver_name,
            caregiver.caregiver_type AS caregiver_type
        FROM `tabCaregiver` caregiver
    """, as_dict=True)

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

        # Fetch payments for this caregiver (from Purchase Invoices)
        paid_amount = frappe.db.sql("""
            SELECT SUM(purchase_invoice.paid_amount) AS paid_amount
            FROM `tabPurchase Invoice` purchase_invoice
            WHERE purchase_invoice.supplier_name = %s
            AND purchase_invoice.status = 'Paid'
        """, (caregiver['caregiver_name']), as_dict=True)

        paid_amount_value = paid_amount[0]['paid_amount'] if paid_amount and paid_amount[0]['paid_amount'] else 0

        # Fetch due amounts (unpaid)
        due_amount = frappe.db.sql("""
            SELECT SUM(purchase_invoice.grand_total - purchase_invoice.paid_amount) AS due_amount
            FROM `tabPurchase Invoice` purchase_invoice
            WHERE purchase_invoice.supplier_name = %s
            AND purchase_invoice.status = 'Unpaid'
        """, (caregiver['caregiver_name']), as_dict=True)

        due_amount_value = due_amount[0]['due_amount'] if due_amount and due_amount[0]['due_amount'] else 0

        # Add caregiver data to the list
        caregivers_data.append({
            'caregiver_name': caregiver['caregiver_name'],
            'caregiver_type': caregiver['caregiver_type'],
            'last_engagement': last_engagement_date,
            'due_amount': due_amount_value,
            'paid_amount': paid_amount_value,
        })

    # Fetch Customer Details
    customers = frappe.db.sql("""
        SELECT 
            customer.name AS customer_name
        FROM `tabCustomer` customer
    """, as_dict=True)

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

        # Fetch payments made by the customer
        paid_amount = frappe.db.sql("""
            SELECT SUM(sales_invoice.paid_amount) AS paid_amount
            FROM `tabSales Invoice` sales_invoice
            WHERE sales_invoice.customer = %s
            AND sales_invoice.status = 'Paid'
        """, (customer['customer_name']), as_dict=True)

        paid_amount_value = paid_amount[0]['paid_amount'] if paid_amount and paid_amount[0]['paid_amount'] else 0

        # Fetch due amounts (unpaid)
        due_amount = frappe.db.sql("""
            SELECT SUM(sales_invoice.grand_total - sales_invoice.paid_amount) AS due_amount
            FROM `tabSales Invoice` sales_invoice
            WHERE sales_invoice.customer = %s
            AND sales_invoice.status = 'Unpaid'
        """, (customer['customer_name']), as_dict=True)

        due_amount_value = due_amount[0]['due_amount'] if due_amount and due_amount[0]['due_amount'] else 0

        # Add customer data to the list
        customers_data.append({
            'customer_name': customer['customer_name'],
            'engaged_caregivers': engaged_caregivers_count,
            'due_amount': due_amount_value,
            'paid_amount': paid_amount_value,
        })

    return {
        'caregivers': caregivers_data,
        'customers': customers_data
    }
