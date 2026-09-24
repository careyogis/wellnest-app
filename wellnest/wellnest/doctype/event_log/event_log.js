// Copyright (c) 2026, www.careyogis.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Log", {
	// Event Log records are append-only; disable editing in the form view.
	refresh(frm) {
		frm.disable_save();
	},
});
