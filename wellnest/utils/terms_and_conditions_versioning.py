import frappe
from frappe import _

def validate_terms_immutability(doc, method):
    if not doc.is_new():
        # If any acceptance record references this version, do not allow changes to the terms text
        has_acceptances = frappe.db.exists(
            "Terms Acceptance", 
            {"terms_version": doc.name}
        )
        if has_acceptances and doc.has_value_changed("terms"):
            frappe.throw(
                _("This Terms and Conditions version has already been signed by parties and cannot be modified. Please create a new version instead.")
            )
