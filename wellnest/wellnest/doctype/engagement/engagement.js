// Copyright (c) 2024, www.thewellnest.in and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Engagement", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Required Activity', {
    // this is fired when a new row is added in the child table field
    required_activity_add(frm, cdt, cdn) { 
        // set the customer same as parent doctype customer
        frappe.model.set_value(cdt, cdn, 'customer', frm.doc.customer);
    }
});
