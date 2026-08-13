import frappe

def update_website_context(context):
    # System and auth routes that MUST use standard Frappe web.html base template
    system_routes = ("login", "app", "me", "reset-password", "update-password")
    
    path = getattr(context, "path", "") or ""
    if frappe.request and hasattr(frappe.request, "path"):
        req_path = frappe.request.path.strip("/")
        if req_path:
            path = req_path

    # If route is login or system auth page, leave default template
    if any(path.startswith(r) for r in system_routes):
        return

    # Apply wellnest_web.html for public website pages (blog, practitioners, marketing pages)
    context.base_template_path = "templates/wellnest_web.html"
