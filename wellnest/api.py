import frappe


@frappe.whitelist()
# def dashboard():
#     # return frappe.db.get_all('Engagement', fields=['*'])
#     # frappe.db.get_all('Caregier', fields=['*'], filters={'user_id': frappe.user})
#     return frappe.db.get_all(
#         "Engagement Caregiver", fields=["*"], filters={"caregiver": frappe.user}
#     )
#     # caregiver_engagement2 = frappe.db.get_list('Engagement Caregiver', fields=['*'], filters={'caregiver': 'CGVR-000004'})
#     # engagement = caregiver_engagement.parent
#     # return [caregiver_engagement1, caregiver_engagement2]


def profile():
    caregiver_name = frappe.db.get_list(
        "Caregiver", fields=["*"], filters={"user_id": frappe.session.user}
    )
    caregiver_data = frappe.get_doc("Caregiver", caregiver_name[0].name)
    agency = frappe.get_doc("Supplier", caregiver_name[0].supplier)
    agency_contact = frappe.get_doc("Address", agency.supplier_primary_address)
    return {"caregiver_name": caregiver_name, "caregiver_data": caregiver_data, "agency_data": agency, "agency_contact": agency_contact}
    # return agency_contact


