import frappe
from frappe.boot import load_translations

no_cache = 1


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # nosempgrep

	context.csrf_token = csrf_token
	context.boot = get_boot()
	context.site_name = frappe.local.site
	if frappe.session.user and frappe.session.user != "Guest":
		context.session_user = frappe.session.user


@frappe.whitelist(methods=["GET"], allow_guest=True)
def get_context_for_dev():
	if not frappe.conf.developer_mode:
		frappe.throw(frappe._("This method is only meant for developer mode"))
	boot = get_boot()
	boot["csrf_token"] = frappe.sessions.get_csrf_token()
	return boot


def get_boot():
	bootinfo = frappe._dict(
		{
			"site_name": str(frappe.local.site),
			"socketio_port": frappe.conf.get("socketio_port") or 9000,
			"push_relay_server_url": frappe.conf.get("push_relay_server_url") or "",
			"default_route": get_default_route(),
		}
	)

	if frappe.session.user and frappe.session.user != "Guest":
		bootinfo.session_user = str(frappe.session.user)
		bootinfo.user = str(frappe.session.user)

	bootinfo.lang = str(frappe.local.lang or "en")
	load_translations(bootinfo)
	if "lang" in bootinfo:
		bootinfo.lang = str(bootinfo.lang)

	return bootinfo


def get_default_route():
	return "/doctor-app"
