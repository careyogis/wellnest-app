// Copyright (c) 2026, www.careyogis.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Practitioner", {
	refresh(frm) {
		if (
			!frm.doc.user_id &&
			!frm.is_new() &&
			frm.perm[0].write &&
			frappe.boot.user.can_create.includes("User")
		) {
			frm.add_custom_button(__("Invite as User"), function () {
				return frappe.call({
					method: "wellnest.health.doctype.practitioner.practitioner.invite_user",
					args: {
						practitioner: frm.doc.name,
					},
					callback: function (r) {
						frm.set_value("user_id", r.message);
						frm.save();
					},
				});
			});
		}
	},
});
