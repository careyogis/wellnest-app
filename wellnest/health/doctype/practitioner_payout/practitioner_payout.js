// Copyright (c) 2026, CareYogi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Practitioner Payout', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			if (!frm.doc.supplier) {
				frm.dashboard.clear_headline();
				frm.dashboard.set_headline_alert(
					__('No Supplier linked to this Practitioner. Care Operations must link an ERPNext Supplier in Practitioner before accounting entries can be created.'),
					'yellow'
				);
			}

			if (frm.doc.status === 'Draft') {
				frm.add_custom_button(__('Approve'), function() {
					frappe.confirm(__('Are you sure you want to approve this payout?'), function() {
						frm.set_value('status', 'Approved');
						frm.save();
					});
				}).addClass('btn-primary');
			}

			if (frm.doc.status === 'Approved') {
				frm.add_custom_button(__('Mark as Paid'), function() {
					let d = new frappe.ui.Dialog({
						title: __('Record Payment Disbursement'),
						fields: [
							{
								label: __('Payment Reference / UTR'),
								fieldname: 'payment_reference',
								fieldtype: 'Data',
								reqd: 1,
								description: __('Bank UTR number or UPI transaction reference')
							},
							{
								label: __('Payout Date'),
								fieldname: 'payout_date',
								fieldtype: 'Date',
								default: frappe.datetime.nowdate(),
								reqd: 1
							},
							{
								label: __('Payment Method'),
								fieldname: 'payment_method',
								fieldtype: 'Select',
								options: 'Bank Transfer (NEFT/IMPS)\nUPI\nCheque\nOther',
								default: frm.doc.payment_method || 'Bank Transfer (NEFT/IMPS)',
								reqd: 1
							}
						],
						primary_action_label: __('Confirm Payment'),
						primary_action: function(values) {
							d.hide();
							frappe.call({
								method: 'mark_as_paid',
								doc: frm.doc,
								args: values,
								freeze: true,
								callback: function(r) {
									if (!r.exc) {
										frm.reload_doc();
									}
								}
							});
						}
					});
					d.show();
				}).addClass('btn-success');
			}

			if (frm.doc.status !== 'Paid' && frm.doc.status !== 'Cancelled') {
				frm.add_custom_button(__('Cancel Payout'), function() {
					frappe.confirm(__('Cancelling this payout will unlink all consultations and return them to Accrued status. Continue?'), function() {
						frappe.call({
							method: 'cancel_payout',
							doc: frm.doc,
							freeze: true,
							callback: function(r) {
								if (!r.exc) {
									frm.reload_doc();
								}
							}
						});
					});
				}).addClass('btn-danger');
			}
		}
	}
});
