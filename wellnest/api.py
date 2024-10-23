import frappe  # type: ignore
from datetime import datetime

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
    # If Caregiver is Solo and not from an Agency
    if caregiver_name[0].supplier:
        agency = frappe.get_doc("Supplier", caregiver_name[0].supplier)
        agency_contact = frappe.get_doc("Address", agency.supplier_primary_address)
        return {
            "caregiver_name": caregiver_name[0],
            "caregiver_data": caregiver_data,
            "agency_data": agency,
            "agency_contact": agency_contact,
        }
    else:
        return {
            "caregiver_name": caregiver_name[0],
            "caregiver_data": caregiver_data,
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
    # activities = frappe.db.get_list(
    #     "Caregiver Activity",
    #     fields=["*"],
    #     filters={"engagement": engagements[0].parent},
    # )
    customerName = frappe.get_doc("Engagement", engagements[0].parent).customer
    customerDoc = frappe.get_doc("Customer", customerName)
    # return activities

    engagementDailyRecordId = frappe.get_all(
        "Engagement Daily Record",
        fields=["*"],
        filters={"engagement": engagements[0].parent},
    )[0].name

    engagementDailyRecord = frappe.get_doc(
        "Engagement Daily Record", engagementDailyRecordId
    )

    return {
        "customerDoc": customerDoc,
        # "activities": activities,
        "engagementRecord": engagementDailyRecord,
    }


@frappe.whitelist()
def setActivityData(taskName, data):
    currentTime = datetime.now().time()
    frappe.db.set_value(
        "Engagement Daily Activity",
        taskName,
        {
            "activity_data": data,
            "completion_time": currentTime,
        },
    )
    return currentTime


@frappe.whitelist()
def setActivityCompletionTime(taskName, time):
    frappe.db.set_value(
        "Engagement Daily Activity",
        taskName,
        {
            "completion_time": time,
        },
    )


@frappe.whitelist()
def setFilePath(taskName, fileURL):
    frappe.db.set_value(
        "Engagement Daily Activity",
        taskName,
        {
            "proof": fileURL,
        },
    )


@frappe.whitelist()
def createDailyRecord(engagement, caregiver, time):
    # fetch activities data from engagement
    required_activities = frappe.get_doc("Engagement", engagement).required_activity
    # create a new document
    doc = frappe.get_doc(
        {
            "doctype": "Engagement Daily Record",
            "engagement": engagement,
            "caregiver": caregiver,
            "check_in_date_and_time": time,
        }
    )
    for activity in required_activities:
        doc.append(
            "performed_activities",
            {
                "activity": activity.activity,
                "prescribed_time": activity.prescribed_time,
                "notes": activity.notes,
            },
        )
    doc.insert()
    return doc


# @frappe.whitelist()
# def checkin(record, time):
#     frappe.db.set_value(
#         "Engagement Daily Record",
#         record,
#         {
#             "check_in_date_and_time": time,
#         },
#     )

@frappe.whitelist()
def checkout(record, time):
    frappe.db.set_value(
        "Engagement Daily Record",
        record,
        {
            "check_out_date_and_time": time,
        },
    )
