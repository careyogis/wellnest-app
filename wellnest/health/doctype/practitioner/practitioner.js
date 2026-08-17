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
	},

	setup_availability_days_buttons: function (frm) {
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
			get_days(label).forEach((day) => frm.add_child("availability_days", { day: day }));
			frm.refresh_field("availability_days");
		};

		labels.forEach((label) =>
			frm.fields_dict["availability_days"].grid.add_custom_button(label, set_days, "top")
		);
	},

	copy_to_all_days: function(frm) {
		// Ease of use feature
		(frm.doc.availability_days || []).forEach(row => {
			row.from = row.emergency_from = row.clinic_from = frm.doc.from_time;
			row.to = row.emergency_to = row.clinic_to = frm.doc.to_time;
		});

		frm.refresh_field('availability_days');		
	},
},
);
