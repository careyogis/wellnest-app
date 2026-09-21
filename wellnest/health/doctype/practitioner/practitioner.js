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

		// Setup Supplier record for the Practitioner if not already linked
		if (
			!frm.doc.supplier &&
			!frm.is_new() &&
			frm.perm[0].write &&
			frappe.boot.user.can_create.includes("Supplier")
		) {
			frm.add_custom_button(__("Add as a Supplier"), function () {
				return frappe.call({
					method: "wellnest.health.doctype.practitioner.practitioner.add_as_supplier",
					args: {
						practitioner: frm.doc.name,
					},
					callback: function (r) {
						frm.set_value("supplier", r.message);
						frm.save();
					},
				});
			});
		}
		
		// Setup availability days buttons
		frm.trigger("setup_availability_days_buttons");

		frm.set_query('super_specialty', function() {
            return {
                filters: {
                    specialty: frm.doc.specialty
                }
            };
        });

        // Set column widths for the availaility_days grid
        let grid = frm.get_field('availability_days').grid;
        
        // This forces the grid view to re-evaluate and draw more than 5 columns
        grid.meta.max_columns = 6; 
        
        frm.refresh_field('availability_days');		
	},

setup_availability_days_buttons: function (frm) {
        const grid = frm.fields_dict["availability_days"].grid;

        const labels = ["Weekends", "Weekdays", "All Days"];

        let get_days = (label) => {
                const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
                const weekends = ["Saturday", "Sunday"];

                return {
                        "All Days": weekdays.concat(weekends),
                        Weekdays: weekdays,
                        Weekends: weekends,
                }[label];
        };

        let set_days = (e) => {
                frm.clear_table("availability_days");

                const label = $(e.currentTarget).text();

                get_days(label).forEach((day) =>
                        frm.add_child("availability_days", { day: day })
                );

                frm.refresh_field("availability_days");
        };

        labels.forEach((label) =>
                grid.add_custom_button(label, set_days, "top")
        );

        grid.add_custom_button(
                __("Copy to All Days"),
                function () {
                        const selected_days = grid.get_selected_children();

                        if (selected_days.length !== 1) {
                                frappe.msgprint(
                                        __("Please select exactly one day to copy.")
                                );
                                return;
                        }

                        const source_day = selected_days[0];

                        (frm.doc.availability_days || []).forEach((day) => {
                                if (day.name === source_day.name) {
                                        return;
                                }

                                day.online_from = source_day.online_from || "";
                                day.online_to = source_day.online_to || "";
                                day.emergency_from = source_day.emergency_from || "";
                                day.emergency_to = source_day.emergency_to || "";
                                day.clinic_from = source_day.clinic_from || "";
                                day.clinic_to = source_day.clinic_to || "";
                        });

                        frm.refresh_field("availability_days");

                        frappe.show_alert({
                                message: __("Availability timings copied to all days."),
                                indicator: "green",
                        });
                },
                "top"
        );
},

},
);
