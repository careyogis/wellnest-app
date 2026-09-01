"""Injects DB settings into frappe.conf on every request"""
import frappe

def inject_db_settings_into_conf():
    """
    Hooked to `before_request`.
    Fetches the singleton 'System Settings Extended' from Redis and updates frappe.local.conf.
    This ensures that frappe.conf.get("...") works for all keys in the singleton.
    """
    if not getattr(frappe.local, 'site', None):
        return
        
    try:
        # frappe.get_single implicitly uses frappe.cache() so this is a fast Redis read
        settings = frappe.get_single("System Settings Extended").as_dict()
        if settings:
            # Update the current request's frappe.conf with the settings
            frappe.local.conf.update(settings)
    except Exception as e:
        frappe.logger().error(f"Failed to inject System Settings Extended into conf: {e}")
