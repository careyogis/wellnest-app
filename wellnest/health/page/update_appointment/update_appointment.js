frappe.pages['update-appointment'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Update Patient Appointment',
		single_column: true
	});

	// Add Reset button in page actions	
	page.set_secondary_action(__('Reset Page'), function () {
		reset_page();
	});

	// Internal state
	let selected_appointment = null;
	let appointment_control = null;
	let is_submitting = false;

	// Page Container Styles
	const custom_styles = `
		.upload-rx-wrapper {
			padding: 15px 0 40px 0;
		}
		.upload-rx-card {
			background: var(--card-bg, #ffffff);
			border: 1px solid var(--border-color, #e2e8f0);
			border-radius: 12px;
			padding: 24px;
			margin-bottom: 24px;
			box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
		}
		.upload-rx-header-title {
			font-size: 18px;
			font-weight: 600;
			color: var(--text-color, #1a202c);
			margin-bottom: 6px;
		}
		.upload-rx-header-sub {
			font-size: 13px;
			color: var(--text-muted, #0f3b7c);
			margin-bottom: 20px;
		}
		.field-section-grid {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 24px;
			margin-bottom: 20px;
		}
		@media (max-width: 768px) {
			.field-section-grid {
				grid-template-columns: 1fr;
			}
		}
		.field-box {
			background: var(--bg-color, #f8fafc);
			border: 1px solid var(--border-color, #e2e8f0);
			border-radius: 10px;
			padding: 18px;
		}
		.field-box-title {
			font-size: 14px;
			font-weight: 600;
			color: var(--heading-color, #2d3748);
			margin-bottom: 12px;
			display: flex;
			align-items: center;
			gap: 8px;
		}
		.appointment-badge {
			display: inline-flex;
			align-items: center;
			gap: 6px;
			padding: 4px 10px;
			border-radius: 20px;
			font-size: 12px;
			font-weight: 500;
		}
		.badge-status-allowed {
			background: #def7ec;
			color: #03543f;
		}
		.badge-status-blocked {
			background: #fde8e8;
			color: #9b1c1c;
		}
		.upload-dropzone {
			border: 2px dashed var(--border-color, #cbd5e0);
			border-radius: 8px;
			padding: 24px;
			text-align: center;
			background: var(--card-bg, #ffffff);
			transition: all 0.2s ease;
			cursor: pointer;
			margin-top: 12px;
		}
		.upload-dropzone:hover:not(.disabled) {
			border-color: var(--primary-color, #2b6cb0);
			background: #f0f7ff;
		}
		.upload-dropzone.disabled {
			cursor: not-allowed;
			opacity: 0.6;
			background: #edf2f7;
		}
		.rx-detail-table {
			width: 100%;
			border-collapse: collapse;
			margin-top: 12px;
		}
		.rx-detail-table th {
			background: var(--bg-color, #f7fafc);
			padding: 10px 14px;
			font-size: 12px;
			text-transform: uppercase;
			color: var(--text-muted, #0f3b7c);
			border-bottom: 1px solid var(--border-color, #e2e8f0);
			text-align: left;
		}
		.rx-detail-table td {
			padding: 12px 14px;
			font-size: 13px;
			border-bottom: 1px solid var(--border-color, #edf2f7);
			vertical-align: top;
		}
		.json-viewer {
			background: #1a202c;
			color: #a0aec0;
			padding: 16px;
			border-radius: 8px;
			font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
			font-size: 12px;
			overflow-x: auto;
			max-height: 400px;
		}
	`;

	$('<style>').text(custom_styles).appendTo(page.main);

	// Build Main Layout Structure
	const main_html = $(`
		<div class="upload-rx-wrapper">
			<!-- Step 1 & 2: Selection & Upload Card -->
			<div class="upload-rx-card">
				<div class="upload-rx-header-title">${__('Process Prescription for Appointment')}</div>
				<div class="upload-rx-header-sub">
					${__('Select a Patient Appointment. If no Smart Prescription is currently associated, attach a prescription image to analyze and generate the Smart Prescription.')}
				</div>

				<div class="field-section-grid">
					<!-- Appointment Column -->
					<div class="field-box">
						<div class="field-box-title">
							<span class="indicator blue"></span>
							<span>1. ${__('Patient Appointment')}</span>
						</div>
						<div class="appointment-control-mount"></div>
						<div class="appointment-meta-info" style="margin-top: 12px;"></div>
					</div>

					<!-- Attach Column -->
					<div class="field-box">
						<div class="field-box-title">
							<span class="indicator" id="attach-indicator"></span>
							<span>2. ${__('Prescription Image File')}</span>
						</div>
						<div class="attach-control-mount"></div>

						<!-- Custom Upload Trigger Button / Helper -->
						<div id="upload-action-box" style="margin-top: 12px;">
							<button class="btn btn-default btn-sm btn-block btn-open-uploader" disabled>
								<i class="fa fa-paperclip"></i> ${__('Choose / Upload File')}
							</button>
							<div class="text-muted" style="font-size: 11px; margin-top: 6px; text-align: center;">
								${__('Supported formats: JPG, PNG, WEBP, PDF (Images preferred)')}
							</div>
						</div>
					</div>
				</div>

				<!-- Status Message Area -->
				<div class="appointment-status-area" style="margin-top: 8px;"></div>
			</div>

			<!-- Step 3: API Response Card -->
			<div class="upload-rx-card response-card" style="display: none;">
				<div class="upload-rx-header-title d-flex justify-content-between align-items-center">
					<span>${__('API Response & Extracted Prescription')}</span>
					<span id="response-status-badge"></span>
				</div>
				<div class="response-content-area" style="margin-top: 16px;"></div>
			</div>
		</div>
	`);

	page.main.append(main_html);

	const $appointment_mount = main_html.find('.appointment-control-mount');
	const $attach_mount = main_html.find('.attach-control-mount');
	const $appointment_meta = main_html.find('.appointment-meta-info');
	const $status_area = main_html.find('.appointment-status-area');
	const $btn_open_uploader = main_html.find('.btn-open-uploader');
	const $response_card = main_html.find('.response-card');
	const $response_content = main_html.find('.response-content-area');
	const $response_badge = main_html.find('#response-status-badge');
	const $attach_indicator = main_html.find('#attach-indicator');

	// Set initial attach indicator to grey
	$attach_indicator.addClass('gray');

	// 1. Create Patient Appointment Link Control
	appointment_control = frappe.ui.form.make_control({
		df: {
			fieldtype: 'Link',
			fieldname: 'patient_appointment',
			options: 'Patient Appointment',
			filters: {
				status: 'Completed',
			},
			label: __('Patient Appointment'),
			placeholder: __('Search & select Patient Appointment...'),
			reqd: 1,
			change: function () {
				const val = appointment_control.get_value();
				handle_appointment_selection(val);
			},
		},
		parent: $appointment_mount[0],
		render_input: true,
	});
	appointment_control.refresh();


	// Wire up upload button
	$btn_open_uploader.on('click', function () {
		if (!selected_appointment) {
			frappe.msgprint(__('Please select an appointment without an existing Smart Prescription first.'));
			return;
		}
		open_file_uploader();
	});

	/**
	 * Handle appointment change:
	 * Check if an associated 'Smart Prescription' exists.
	 */
	function handle_appointment_selection(appointment_name) {
		selected_appointment = appointment_name;

		// Clear previous status & response
		$appointment_meta.empty();
		$status_area.empty();
		$response_card.hide();
		$response_content.empty();

		if (!appointment_name) {
			lock_attachment_input(__('Select a Patient Appointment first.'));
			return;
		}

		// Show loading status
		$status_area.html(`
			<div class="alert alert-info py-2" style="font-size: 13px;">
				<i class="fa fa-spinner fa-spin"></i> ${__('Checking for existing Smart Prescription associated with')} <b>${frappe.utils.escape_html(appointment_name)}</b>...
			</div>
		`);

		// Query backend to check associated Smart Prescription
		frappe.call({
			method: 'wellnest.health.page.update_appointment.update_appointment.check_patient_appointment',
			args: {
				patient_appointment: appointment_name,
			},
			callback: function (r) {
				if (r && r.message) {
					process_appointment_check_result(r.message);
				} else {
					// Fallback direct check via db.get_list
					fallback_check_prescription(appointment_name);
				}
			},
			error: function () {
				fallback_check_prescription(appointment_name);
			},
		});
	}

	/**
	 * Direct query fallback if helper endpoint is unreachable
	 */
	function fallback_check_prescription(appointment_name) {
		frappe.db.get_list('Smart Prescription', {
			filters: { patient_appointment: appointment_name },
			fields: ['name', 'workflow_state', 'prescription_date', 'patient', 'practitioner'],
			order_by: 'creation desc',
		}).then(function (records) {
			if (records && records.length > 0) {
				process_appointment_check_result({
					has_smart_prescription: true,
					smart_prescriptions: records,
				});
			} else {
				// Fetch appointment doc for metadata
				frappe.db.get_value('Patient Appointment', appointment_name, ['patient', 'practitioner', 'appointment_date', 'status'])
					.then(function (res) {
						const data = res.message || {};
						process_appointment_check_result({
							has_smart_prescription: false,
							smart_prescriptions: [],
							patient: data.patient,
							practitioner: data.practitioner,
							appointment_date: data.appointment_date,
							status: data.status,
						});
					});
			}
		});
	}

	/**
	 * Process check results:
	 * If Smart Prescription exists: DISALLOW attaching file
	 * If NO Smart Prescription exists: ALLOW attaching file
	 */
	function process_appointment_check_result(data) {
		if (data.has_smart_prescription) {
			// 1. Associated Smart Prescription EXISTS: Block upload
			lock_attachment_input(__('Blocked: Associated Smart Prescription already exists'));

			const existing = data.smart_prescriptions[0];
			const rx_link = `<a href="/app/smart-prescription/${frappe.utils.escape_html(existing.name)}" target="_blank" style="text-decoration: underline; font-weight: 600;">${frappe.utils.escape_html(existing.name)}</a>`;

			$status_area.html(`
				<div class="alert alert-warning py-3" style="font-size: 13px; line-height: 1.5;">
					<div class="d-flex align-items-center mb-1">
						<i class="fa fa-exclamation-triangle text-warning mr-2" style="font-size: 16px;"></i>
						<strong style="color: #975a16;">${__('Smart Prescription Already Exists')}</strong>
					</div>
					<div>
						${__('Appointment')} <b>${frappe.utils.escape_html(selected_appointment)}</b> ${__('already has an associated Smart Prescription:')}
						${rx_link} (${__('Workflow State')}: <b>${frappe.utils.escape_html(existing.workflow_state || 'Draft')}</b>).
					</div>
					<div class="text-muted mt-1" style="font-size: 12px;">
						${__('New prescription attachment is disabled because each appointment can only have one Smart Prescription.')}
					</div>
				</div>
			`);
		} else {
			// 2. NO Associated Smart Prescription: Allow upload
			unlock_attachment_input();

			// Display Appointment info
			let meta_html = `
				<div style="font-size: 12px; background: #fff; padding: 10px; border-radius: 6px; border: 1px solid var(--border-color);">
					<div><b>${__('Patient')}:</b> ${frappe.utils.escape_html(data.patient_name || data.patient || __('Not Specified'))} (${frappe.utils.escape_html(data.patient || '')})</div>
					${data.practitioner ? `<div><b>${__('Practitioner')}:</b> ${frappe.utils.escape_html(data.practitioner_name || data.practitioner || __('Not Specified'))} (${frappe.utils.escape_html(data.practitioner)})</div>` : ''}
					${data.appointment_time ? `<div><b>${__('Appointment Date & Time')}:</b> ${frappe.utils.escape_html(data.appointment_time)}</div>` : ''}
				</div>
			`;
			$appointment_meta.html(meta_html);

			$status_area.html(`
				<div class="alert alert-success py-2" style="font-size: 13px;">
					<i class="fa fa-check-circle text-success mr-2"></i>
					<b>${__('Eligible for Prescription Upload')}:</b> ${__('No associated Smart Prescription found. You can now attach the prescription image.')}
				</div>
			`);
		}
	}

	function lock_attachment_input(reason) {
		$btn_open_uploader.prop('disabled', true);
		$attach_indicator.removeClass('green blue').addClass('red');
	}

	function unlock_attachment_input() {
		$btn_open_uploader.prop('disabled', false);
		$attach_indicator.removeClass('red gray').addClass('green');
	}

	/**
	 * Open Frappe File Uploader
	 */
	function open_file_uploader() {
		new frappe.ui.FileUploader({
			doctype: 'Patient Appointment',
			docname: selected_appointment,
			folder: 'Home/Attachments',
			restrictions: {
				allowed_file_types: ['image/*', 'application/pdf'],
			},
			on_success: function (file_doc) {
				const file_url = file_doc.file_url;
				on_file_attached(file_url);
			},
		});
	}

	/**
	 * Called when a file is attached:
	 * Invokes wellnest.api.presecription.parse_and_create_prescription
	 */
	function on_file_attached(file_url) {
		if (!selected_appointment) {
			frappe.msgprint(__('Please select a Patient Appointment first.'));
			return;
		}

		if (is_submitting) {
			return;
		}

		is_submitting = true;

		// Show submitting feedback
		$status_area.html(`
			<div class="alert alert-info py-2" style="font-size: 13px;">
				<i class="fa fa-spinner fa-spin mr-2"></i>
				${__('Analyzing prescription image with AI... This may take a few seconds.')}
			</div>
		`);

		$response_card.show();
		$response_badge.html(`<span class="badge badge-warning">${__('Processing...')}</span>`);
		$response_content.html(`
			<div class="text-center py-5">
				<div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
					<span class="sr-only">${__('Processing...')}</span>
				</div>
				<div class="mt-3 text-muted" style="font-size: 14px;">
					${__('Parsing prescription text, extracting medicines, dosages, and instructions...')}
				</div>
			</div>
		`);

		// Call API: wellnest.api.presecription.parse_and_create_prescription
		call_parse_and_create_api(selected_appointment, file_url);
	}

	function call_parse_and_create_api(appointment, file_url) {
		const api_method = 'wellnest.api.prescription.parse_and_create_prescription';

		frappe.call({
			method: api_method,
			args: {
				patient_appointment: appointment,
				file_url: file_url,
			},
			freeze: true,
			freeze_message: __('Analyzing prescription image and generating Smart Prescription...'),
			callback: function (r) {
				is_submitting = false;
				handle_api_success(r.message, file_url);
			},
			error: function (err) {
				console.warn('Attempt to call presecription parsing API failed...', err);
			},
		});
	}

	/**
	 * Render successful API response
	 */
	function handle_api_success(response, file_url) {
		$status_area.empty();

		if (!response) {
			// The doc was not identified as a prescription
			$response_badge.html(`<span class="badge badge-warning">${__('Non-Prescription Document')}</span>`);
			$response_content.html(`
				<div class="alert alert-warning py-3">
					<i class="fa fa-info-circle mr-2"></i>
					<b>${__('Document Not Identified as Prescription')}</b><br>
					${__('The uploaded file was analyzed by AI, but it was determined to not be a valid prescription. No Smart Prescription was created.')}
				</div>
				<div style="margin-top: 16px;">
					<h6>${__('Raw API Response')}:</h6>
					<pre class="json-viewer"><code>null</code></pre>
				</div>
			`);
			return;
		}

		// Prescription created successfully!
		$response_badge.html(`
			<span class="badge badge-success" style="font-size: 13px; padding: 6px 12px;">
				<i class="fa fa-check"></i> ${__('Prescription Created')}
			</span>
		`);

		// Update status alert
		$status_area.html(`
			<div class="alert alert-success py-3" style="font-size: 13px;">
				<div class="d-flex justify-content-between align-items-center">
					<div>
						<i class="fa fa-check-circle mr-2 text-success" style="font-size: 16px;"></i>
						<b>${__('Smart Prescription')} <a href="/app/smart-prescription/${encodeURIComponent(response.name)}" target="_blank" style="text-decoration: underline;">${frappe.utils.escape_html(response.name)}</a> ${__('created successfully!')}</b>
					</div>
					<a href="/app/smart-prescription/${encodeURIComponent(response.name)}" class="btn btn-sm btn-primary" target="_blank">
						<i class="fa fa-external-link mr-1"></i> ${__('Open Prescription')}
					</a>
				</div>
			</div>
		`);

		// Lock further attachments now that a prescription has been created
		lock_attachment_input(__('Smart Prescription created'));

		// Build medicines table
		const medicines = response.medicines || [];
		let medicines_html = '';
		if (medicines.length > 0) {
			medicines_html = `
				<table class="rx-detail-table">
					<thead>
						<tr>
							<th style="width: 50px;">#</th>
							<th>${__('Medicine Name')}</th>
							<th>${__('Dosage')}</th>
							<th>${__('Timing')}</th>
							<th>${__('Duration')}</th>
						</tr>
					</thead>
					<tbody>
						${medicines.map((m, idx) => `
							<tr>
								<td><b>${idx + 1}</b></td>
								<td><strong style="color: #2b6cb0;">${frappe.utils.escape_html(m.name || '-')}</strong></td>
								<td>${frappe.utils.escape_html(m.dosage || '-')}</td>
								<td>${frappe.utils.escape_html(m.timing || '-')}</td>
								<td>${frappe.utils.escape_html(m.duration || '-')}</td>
							</tr>
						`).join('')}
					</tbody>
				</table>
			`;
		} else {
			medicines_html = `<div class="text-muted p-3 text-center" style="background: var(--bg-color); border-radius: 6px;">${__('No specific medicines detected in the image.')}</div>`;
		}

		// Advice block
		const advice_html = response.advice ? `
			<div class="mt-4 p-3" style="background: #f7fafc; border-left: 4px solid #3182ce; border-radius: 0 6px 6px 0;">
				<h6 style="color: #2b6cb0; margin-bottom: 6px;"><i class="fa fa-stethoscope mr-1"></i> ${__('Doctor Advice / Instructions')}</h6>
				<div style="font-size: 13px; color: #2d3748; white-space: pre-wrap;">${frappe.utils.escape_html(response.advice)}</div>
			</div>
		` : '';

		// Prescription Preview thumbnail
		const is_image = file_url && (file_url.endsWith('.jpg') || file_url.endsWith('.jpeg') || file_url.endsWith('.png') || file_url.endsWith('.webp'));
		const image_preview = is_image ? `
			<div class="col-md-4 mb-3">
				<div style="border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; background: #000; text-align: center;">
					<a href="${file_url}" target="_blank" title="${__('Click to view full image')}">
						<img src="${file_url}" style="max-height: 280px; max-width: 100%; object-fit: contain; margin: 0 auto; display: block;" />
					</a>
				</div>
				<div class="text-center mt-2">
					<a href="${file_url}" target="_blank" class="btn btn-default btn-xs">
						<i class="fa fa-search-plus"></i> ${__('View Original File')}
					</a>
				</div>
			</div>
		` : `
			<div class="col-md-4 mb-3">
				<div class="p-4 text-center" style="background: var(--bg-color); border-radius: 8px; border: 1px solid var(--border-color);">
					<i class="fa fa-file-text-o fa-3x text-muted mb-2"></i>
					<div><a href="${file_url}" target="_blank" class="btn btn-default btn-sm mt-2">${__('View Attached File')}</a></div>
				</div>
			</div>
		`;

		const raw_json = JSON.stringify(response, null, 2);

		$response_content.html(`
			<div class="row">
				${image_preview}
				<div class="col-md-8">
					<div class="d-flex justify-content-between align-items-center mb-2">
						<h5 style="margin: 0;">${__('Prescribed Medicines')}</h5>
						<span class="badge badge-info">${__('State')}: ${frappe.utils.escape_html(response.workflow_state || 'Draft')}</span>
					</div>
					${medicines_html}
					${advice_html}
				</div>
			</div>

			<!-- Collapsible Raw API Response Section -->
			<div class="mt-4 pt-3 border-top">
				<details>
					<summary style="cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text-muted);">
						<i class="fa fa-code mr-1"></i> ${__('View Complete API Response (JSON)')}
					</summary>
					<div class="mt-2 position-relative">
						<pre class="json-viewer"><code>${frappe.utils.escape_html(raw_json)}</code></pre>
					</div>
				</details>
			</div>
		`);
	}

	/**
	 * Render API Error
	 */
	function handle_api_error(err, file_url) {
		$response_badge.html(`<span class="badge badge-danger">${__('Error')}</span>`);
		const err_msg = err && err.message ? err.message : __('An unexpected error occurred while processing the prescription image.');

		$status_area.html(`
			<div class="alert alert-danger py-2" style="font-size: 13px;">
				<i class="fa fa-exclamation-circle mr-2 text-danger"></i>
				<b>${__('Failed to process prescription')}:</b> ${frappe.utils.escape_html(err_msg)}
			</div>
		`);

		$response_content.html(`
			<div class="alert alert-danger py-3">
				<h5><i class="fa fa-times-circle mr-2"></i> ${__('Prescription Processing Failed')}</h5>
				<p>${frappe.utils.escape_html(err_msg)}</p>
				<div class="mt-3">
					<button class="btn btn-sm btn-outline-danger btn-retry">
						<i class="fa fa-refresh mr-1"></i> ${__('Retry Processing')}
					</button>
				</div>
			</div>
			<div class="mt-3">
				<details>
					<summary style="cursor: pointer; font-size: 12px; color: var(--text-muted);">${__('Error Details')}</summary>
					<pre class="json-viewer mt-2"><code>${frappe.utils.escape_html(JSON.stringify(err, null, 2))}</code></pre>
				</details>
			</div>
		`);

		$response_content.find('.btn-retry').on('click', function () {
			on_file_attached(file_url);
		});
	}

	/**
	 * Reset the entire page state
	 */
	function reset_page() {
		selected_appointment = null;
		is_submitting = false;
		if (appointment_control) {
			appointment_control.set_value('');
		}
		$appointment_meta.empty();
		$status_area.empty();
		$response_card.hide();
		$response_content.empty();
	}

	// Register page load handler for upload-prescription and aliases
	const page_keys = [
		'update-appointment',
		'update_appointment',
		'appointment-update',
		'appointment_update',
	];

	page_keys.forEach(function (key) {
		frappe.pages[key] = frappe.pages[key] || {};
		// frappe.pages[key].on_page_load = init_upload_prescription_page;
	});	
}
