// Copyright (c) 2024, www.thewellnest.in and contributors
// For license information, please see license.txt

frappe.ui.form.on("Caregiver", {
	refresh(frm) {
		if (
			!frm.doc.user_id &&
			!frm.is_new() &&
			frm.perm[0].write &&
			frappe.boot.user.can_create.includes("User")
		) {
			frm.add_custom_button(__("Invite as User"), function () {
				return frappe.call({
					method: "wellnest.wellnest.doctype.caregiver.caregiver.invite_user",
					args: {
						caregiver: frm.doc.name,
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
