import frappe

def create_feedback_doctypes():
    frappe.flags.in_import = True
    
    # 1. Practitioner Feedback Criteria
    if not frappe.db.exists("DocType", "Practitioner Feedback Criteria"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Practitioner Feedback Criteria",
            "module": "Health",
            "custom": 0,
            "naming_rule": "By fieldname",
            "autoname": "field:criteria",
            "fields": [
                {
                    "fieldname": "criteria",
                    "fieldtype": "Data",
                    "label": "Criteria",
                    "reqd": 1,
                    "unique": 1
                }
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        })
        doc.insert(ignore_permissions=True)
        print("Created Practitioner Feedback Criteria")

    # 2. Practitioner Feedback Rating
    if not frappe.db.exists("DocType", "Practitioner Feedback Rating"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Practitioner Feedback Rating",
            "module": "Health",
            "custom": 0,
            "istable": 1,
            "fields": [
                {
                    "fieldname": "criteria",
                    "fieldtype": "Link",
                    "label": "Criteria",
                    "options": "Practitioner Feedback Criteria",
                    "in_list_view": 1,
                    "reqd": 1
                },
                {
                    "fieldname": "rating",
                    "fieldtype": "Float",
                    "label": "Rating",
                    "in_list_view": 1,
                    "reqd": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created Practitioner Feedback Rating")

    # 3. Practitioner Feedback
    if not frappe.db.exists("DocType", "Practitioner Feedback"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Practitioner Feedback",
            "module": "Health",
            "custom": 0,
            "naming_rule": "Expression",
            "autoname": "PFB-.YYYY.-.#####",
            "fields": [
                {"fieldname": "patient", "fieldtype": "Link", "label": "Patient", "options": "Patient", "reqd": 1},
                {"fieldname": "practitioner", "fieldtype": "Link", "label": "Practitioner", "options": "Practitioner", "reqd": 1, "in_list_view": 1},
                {"fieldname": "appointment", "fieldtype": "Link", "label": "Appointment", "options": "Patient Appointment"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "default": "Today"},
                {"fieldname": "average_rating", "fieldtype": "Float", "label": "Average Rating", "read_only": 1, "in_list_view": 1},
                {"fieldname": "section_break_ratings", "fieldtype": "Section Break"},
                {"fieldname": "ratings", "fieldtype": "Table", "label": "Ratings", "options": "Practitioner Feedback Rating"},
                {"fieldname": "comments_section", "fieldtype": "Section Break", "label": "Comments"},
                {"fieldname": "comments", "fieldtype": "Text", "label": "Comments"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Created Practitioner Feedback")

    # Update Practitioner DocType
    practitioner = frappe.get_doc("DocType", "Practitioner")
    fields = [f.fieldname for f in practitioner.fields]
    if "average_rating" not in fields:
        practitioner.append("fields", {
            "fieldname": "feedback_section",
            "fieldtype": "Section Break",
            "label": "Feedback & Ratings"
        })
        practitioner.append("fields", {
            "fieldname": "average_rating",
            "fieldtype": "Float",
            "label": "Average Rating",
            "read_only": 1
        })
        practitioner.append("fields", {
            "fieldname": "total_reviews",
            "fieldtype": "Int",
            "label": "Total Reviews",
            "read_only": 1
        })
        practitioner.save(ignore_permissions=True)
        print("Updated Practitioner DocType")

    frappe.db.commit()

create_feedback_doctypes()
