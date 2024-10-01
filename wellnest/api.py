import frappe # type: ignore

# def dashboard():
#     # return frappe.db.get_all('Engagement', fields=['*'])
#     # frappe.db.get_all('Caregier', fields=['*'], filters={'user_id': frappe.user})
#     return frappe.db.get_all(
#         "Engagement Caregiver", fields=["*"], filters={"caregiver": frappe.user}
#     )
#     # caregiver_engagement2 = frappe.db.get_list('Engagement Caregiver', fields=['*'], filters={'caregiver': 'CGVR-000004'})
#     # engagement = caregiver_engagement.parent
#     # return [caregiver_engagement1, caregiver_engagement2]


@frappe.whitelist()
def dashboard():
    caregiver_name = frappe.db.get_list(
        "Caregiver", fields=["*"], filters={"user_id": frappe.session.user}
    )
    # caregiver_data = frappe.get_doc("Caregiver", caregiver_name[0].name)
    engagements = frappe.get_all(
        "Engagement Caregiver",
        fields=["*"],
        filters={"caregiver": caregiver_name[0].name},
    )
    engagementsId = list(
        set([engagementsId["parent"] for engagementsId in engagements])
    )

    engagementDocs = frappe.get_doc("Engagement", engagementsId)

    customer = frappe.get_doc("Customer", engagementDocs.customer)

    return {
        "caregiver": caregiver_name[0],
        "engagement": engagementDocs,
        "customer": customer,
    }


@frappe.whitelist()
def profile():
    caregiver_name = frappe.db.get_list(
        "Caregiver", fields=["*"], filters={"user_id": frappe.session.user}
    )
    caregiver_data = frappe.get_doc("Caregiver", caregiver_name[0].name)
    agency = frappe.get_doc("Supplier", caregiver_name[0].supplier)
    agency_contact = frappe.get_doc("Address", agency.supplier_primary_address)
    return {
        "caregiver_name": caregiver_name[0],
        "caregiver_data": caregiver_data,
        "agency_data": agency,
        "agency_contact": agency_contact,
    }


@frappe.whitelist()
def activity():
    caregiver_name = frappe.db.get_list(
        "Caregiver", fields=["*"], filters={"user_id": frappe.session.user}
    )
    # caregiver_data = frappe.get_doc("Caregiver", caregiver_name[0].name)
    engagements = frappe.get_all(
        "Engagement Caregiver",
        fields=["*"],
        filters={"caregiver": caregiver_name[0].name},
    )
    engagementsId = list(
        set([engagementsId["parent"] for engagementsId in engagements])
    )
    activities = frappe.db.get_list(
        "Caregiver Activity",
        fields=["*"],
        filters={"engagement": engagements[0].parent},
    )
    customerName = frappe.get_doc("Engagement", engagements[0].parent).customer
    customerDoc = frappe.get_doc("Customer", customerName)
    # return activities
    return {"customerDoc": customerDoc, "activities": activities}
