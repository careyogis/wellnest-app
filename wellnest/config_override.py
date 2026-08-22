"""Enables flexible config settings - can be read from both the db and frappe config files"""
import frappe

# Keep a reference to the original get method
_original_conf_get = frappe.conf.get

# Cache for singleton values
_singleton_cache = {}
_SINGLETON_DOCTYPE = "System Settings Extended"

def enable_conf_override():
    """Enable the custom get method globally."""
    frappe.conf.get = custom_conf_get

def custom_conf_get(key, default=None):
    """
    Check site_config/common_site_config or cached values or load singleton from db
    """
    value = _original_conf_get(key, None)
    if value is not None:
        return value

    if key in _singleton_cache:
        return _singleton_cache.get(key) or default

    _load_singleton_cache()
    return _singleton_cache.get(key, default)

# --- Hook handler to refresh cache when singleton is saved ---
def refresh_cache_on_save(doc):
    """Clear and reload cache when singleton is updated."""
    if doc.doctype == _SINGLETON_DOCTYPE:
        _load_singleton_cache()
        frappe.logger().info(f"{_SINGLETON_DOCTYPE} cache refreshed after save")

def _load_singleton_cache():
    """Load all fields from the singleton into memory."""
    global _singleton_cache
    try:
        # Ensure we have an active site context
        if not frappe.local.site:
            return

        # Try fetching the singleton
        doc = frappe.get_single(_SINGLETON_DOCTYPE)
        _singleton_cache = doc.as_dict()

    except frappe.DoesNotExistError:
        _singleton_cache = {}
    except Exception as e:
        frappe.log_error(f"Error loading {_SINGLETON_DOCTYPE} into config cache: {e}")
        _singleton_cache = {}
