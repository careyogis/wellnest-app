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

// frappe.ui.form.on('Engagement', {
//     refresh: function(frm) {
//         if (!frm.doc.__islocal) {
//             frm.add_custom_button('Generate Acceptance Link', () => {
//                 const base_url = window.location.origin;
//                 const link = `${base_url}/accept-engagement?engagement_id=${frm.doc.name}`;
//                 frappe.msgprint(`Share this link: <br><b><a href="${link}" target="_blank">${link}</a></b>`);
//             });
//         }
//     }
// });
