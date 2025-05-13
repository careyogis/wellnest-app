// Copyright (c) 2024, www.thewellnest.in and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Lead", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Required Activity', {
    // this is fired when a new row is added in the child table field
    service_details_add(frm, cdt, cdn) { 
        // set the customer same as parent doctype customer
        frappe.model.set_value(cdt, cdn, 'customer', frm.doc.customer);
    }
});


frappe.ui.form.on('CY Lead', {
    refresh: function (frm) {
        // Ensure the form is not new before adding custom buttons
        if (!frm.is_new()) {
            
            /**
             *  Broadcast Button
             *  - Checks mandatory fields (City & Pincode)
             *  - Fetches caregivers based on matching criteria
             *  - Displays a selection popup for broadcasting
             *  - Sends selected caregivers to the backend for recording the broadcast
             */
            frm.add_custom_button('Find Caregivers', function () {
                
                // Validate mandatory fields
                if (!frm.doc.city) {
                    frappe.msgprint(__('Please fill the City field.'));
                    return;
                }

                // Extract caregiver preferences and required services
                let language_preferences = (frm.doc.caregiver_language_preference || [])
                    .map(row => row.spoken_language_option)
                    .filter(Boolean);
                
                let service_types = (frm.doc.services_required || [])
                    .map(row => row.item_code)
                    .filter(Boolean);

                // Call backend to fetch matching caregivers
                frappe.call({
                    method: 'wellnest.wellnest.doctype.cy_lead.cy_lead.get_matching_caregivers',
                    args: {
                        city: frm.doc.city,
                        service_types: service_types,
                        language_preferences: language_preferences
                    },
                    callback: function (response) {
                        if (!response.message || response.message.length === 0) {
                            frappe.msgprint(__('No caregivers found matching the criteria.'));
                            return;
                        }

                        let caregivers = response.message;

                        // Create HTML table for caregiver selection
                        let popup_content = `
                            <div style="max-height: 300px; overflow-y: auto;">
                                <table class="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>Select</th>
                                            <th>Name</th>
                                            <th>City</th>
                                            <th>Pincode</th>
                                            <th>Caregiver Type</th>
                                            <th>Languages</th>
                                            <th>Availability</th>
                                            <th>Phone</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                        `;

                        caregivers.forEach(caregiver => {
                            popup_content += `
                                <tr>
                                    <td><input type="checkbox" class="caregiver-checkbox" data-phone="${caregiver.phone_number}"></td>
                                    <td>${caregiver.full_name}</td>
                                    <td>${caregiver.city}</td>
                                    <td>${caregiver.pin_code || 'N/A'}</td>
                                    <td>${caregiver.caregiver_type || 'N/A'}</td>
                                    <td>${caregiver.languages || 'N/A'}</td>
                                    <td>${caregiver.availability}</td>
                                    <td>${caregiver.phone_number}</td>
                                </tr>
                            `;
                        });

                        popup_content += `</tbody></table></div>`;

                        // Display caregiver selection dialog
                        let dialog = new frappe.ui.Dialog({
                            title: 'Select Caregivers to Broadcast',
                            fields: [{ fieldname: 'caregiver_table', fieldtype: 'HTML', options: popup_content }],
                            primary_action_label: 'Broadcast',
                            primary_action: function () {
                                let selected_caregivers = [];
                                $('.caregiver-checkbox:checked').each(function () {
                                    selected_caregivers.push($(this).data('phone'));
                                });

                                if (selected_caregivers.length === 0) {
                                    frappe.msgprint(__('Please select at least one caregiver.'));
                                    return;
                                }

                                // Call backend to generate WhatsApp message
                                frappe.call({
                                    method: "wellnest.wellnest.doctype.cy_lead.cy_lead.broadcast_lead",
                                    args: {
                                        lead_name: frm.doc.name,
                                        phone_numbers: JSON.stringify(selected_caregivers)
                                    },
                                    callback: function (r) {
                                        if (r.message) {
                                            let whatsapp_message = r.message;

                                            // Call backend to record the broadcasted caregivers
                                            frappe.call({
                                                method: "wellnest.wellnest.doctype.cy_lead.cy_lead.record_caregiver_broadcast",
                                                args: {
                                                    lead_name: frm.doc.name,
                                                    caregivers: JSON.stringify(selected_caregivers),
                                                    whatsapp_message: whatsapp_message
                                                },
                                                callback: function (r) {
                                                    if (r.message && r.message.message === "success") {
                                                        frappe.msgprint("Broadcast Successful!");
                                                        dialog.hide();
                                                    } else {
                                                        frappe.msgprint("Failed to Broadcast: " + JSON.stringify(r.message));
                                                    }
                                                }
                                            });
                                        }
                                    }
                                });
                            }
                        });
                        dialog.show();


                        // Apply styles to center and enlarge the dialog
                        const $dialog = $(dialog.$wrapper).find('.modal-dialog');

                        $dialog.css({
                            "width": "90vw",
                            "max-width": "1200px",
                            "margin": "1.75rem auto" // Center it vertically and horizontally
                        });

                        $dialog.find('.modal-content').css({
                            "height": "80vh",
                            "max-height": "80vh",
                            "overflow-y": "auto"
                        });

                    }
                });
            });

            /**
             *  Show Interests Button
             *  - Fetches caregiver responses
             *  - Displays a table with caregivers who responded and their statuses
             */
            frm.add_custom_button('Show Interests', function () {
                
                // Fetch caregiver responses from the backend
                frappe.call({
                    method: 'wellnest.wellnest.doctype.cy_lead.cy_lead.get_caregiver_responses',
                    args: {
                        lead_name: frm.doc.name
                    },
                    callback: function (response) {
                        if (!response.message || response.message.length === 0) {
                            frappe.msgprint(__('No responses found.'));
                            return;
                        }

                        let caregiver_responses = response.message;

                        // Generate table for displaying caregiver responses
                        let popup_content = `
                            <div style="max-height: 300px; overflow-y: auto;">
                                <table class="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>Caregiver Name</th>
                                            <th>Response Time</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                        `;

                        caregiver_responses.forEach(response => {
                            popup_content += `
                                <tr>
                                    <td>${response.caregiver_name}</td>
                                    <td>${response.response_time || 'N/A'}</td>
                                    <td>${response.status}</td>
                                </tr>
                            `;
                        });

                        popup_content += `</tbody></table></div>`;

                        // Display responses in a message box
                        frappe.msgprint({ title: 'Caregiver Responses', message: popup_content, indicator: 'blue' });
                    }
                });
            });
        }
    }
});


