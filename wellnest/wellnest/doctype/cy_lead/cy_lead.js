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
                        requirement: frm.doc.requirement,
                        language_preferences: language_preferences,
                        service_types: service_types, // For future enhancement, will be ignored for now.
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
                                            <td style="width: 2%;"><input type="checkbox" id="select-all"></td>
                                            <th>Name</th>
                                            <th>City</th>
                                            <th>Pin Code</th>
                                            <th>Caregiver Type</th>
                                            <th>Languages</th>
                                            <th>Availability</th>
                                            <th>Phone</th>
                                        </tr>
                                        <!-- Filter Row. Filters caregivers array to the input -->
                                        <tr>
                                            <th></th>
                                            <td><input type="text" id="name-filter" class="form-control" placeholder="Filter Name"></td>
                                            <td><input type="text" id="city-filter" class="form-control" placeholder="Filter City"></td>
                                            <td><input type="text" id="pin-filter" class="form-control" placeholder="Filter Pin code"></td>
                                            <td><input type="text" id="type-filter" class="form-control" placeholder="Filter Caregiver Type"></td>
                                            <th></th>
                                            <th></th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                        `;

                        caregivers.forEach(caregiver => {
                            popup_content += `
                                <tr>
                                    <td><input type="checkbox" class="caregiver-checkbox" data-phone="${caregiver.phone_number}" data-cg="${caregiver.name}"></td>
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
                                let selected_phones = [];
                                let selected_caregiver_ids = [];
                                $('.caregiver-checkbox:checked').each(function () {
                                    selected_phones.push($(this).data('phone'));
                                    selected_caregiver_ids.push($(this).data('cg'));
                                });

                                if (selected_phones.length === 0) {
                                    frappe.msgprint(__('Please select at least one caregiver.'));
                                    return;
                                }

                                // Call backend to generate WhatsApp message
                                frappe.call({
                                    method: "wellnest.wellnest.doctype.cy_lead.cy_lead.broadcast_lead",
                                    args: {
                                        lead_name: frm.doc.name,
                                        phone_numbers: JSON.stringify(selected_phones),
                                        caregiver_ids: JSON.stringify(selected_caregiver_ids),
                                    },
                                    callback: function (r) {
                                        if (r.message) {
                                            frappe.msgprint(r.message.message);
                                            dialog.hide();
                                        }
                                    }
                                });
                            }
                        });
                        dialog.show();

                        // Filtering logic for caregivers table
                        $(dialog.$wrapper).find('#name-filter, #city-filter, #pin-filter, #type-filter').on('input', function () {
                            let nameVal = $('#name-filter').val().toLowerCase();
                            let cityVal = $('#city-filter').val().toLowerCase();
                            let pinVal = $('#pin-filter').val().toLowerCase();
                            let typeVal = $('#type-filter').val().toLowerCase();

                            $('.caregiver-checkbox').each(function () {
                                let $row = $(this).closest('tr');
                                let name = $row.find('td').eq(1).text().toLowerCase();
                                let city = $row.find('td').eq(2).text().toLowerCase();
                                let pin = $row.find('td').eq(3).text().toLowerCase();
                                let type = $row.find('td').eq(4).text().toLowerCase();

                                let show = true;
                                if (nameVal && !name.includes(nameVal)) show = false;
                                if (cityVal && !city.includes(cityVal)) show = false;
                                if (pinVal && !pin.includes(pinVal)) show = false;
                                if (typeVal && !type.includes(typeVal)) show = false;

                                $row.toggle(show);
                            });
                        });

                        // Select All functionality for filtered rows
                        $(dialog.$wrapper).find('#select-all').on('change', function () {
                            let checked = $(this).is(':checked');
                            // Only select checkboxes in visible rows
                            $(dialog.$wrapper).find('tbody tr:visible .caregiver-checkbox').prop('checked', checked);
                        });

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
             *  - Navigates to the "Caregiver Response" report for the selected lead
             */
            frm.add_custom_button('Show Interests', function () {
                frappe.set_route('Report', 'Caregiver Response', {'cy_lead': frm.doc.name});
            });
        }
    }
});


