frappe.pages["care-operations"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Care Operations Dashboard",
		single_column: true,
	});

	new CareOperationsDashboard(page);
};

class CareOperationsDashboard {
	constructor(page) {
		this.page = page;

		this.data = {
			summary: {
				critical: 0,
				high: 0,
				medium: 0,
				total: 0,
			},
			alerts: [],
			consultations: [],
			payments: [],
			doctor_onboarding: [],
			customer_journey: [],
		};

		this.page.set_primary_action(__("Refresh"), () => this.loadDashboard());

		this.loadDashboard();
	}

	formatTime(datetime) {
		if (!datetime) return "-";

		try {
			return frappe.datetime.prettyDate(datetime);
		} catch (e) {
			return datetime;
		}
	}
	loadDashboard() {
		this.page.main.html(`
			<div class="care-ops-loading">
				<div class="spinner-border text-primary" role="status"></div>
				<p>Loading dashboard...</p>
			</div>
		`);

		frappe.call({
			method: "wellnest.wellnest.page.care_operations.care_operations.get_dashboard_data",
			callback: (r) => {
				if (r.message) {
					this.data = r.message;
				}
				this.render();
			},
			error: () => {
				frappe.msgprint(__("Failed to load Care Operations Dashboard."));
			},
		});
	}

	render() {
		this.page.main.empty();

		this.page.main.append(`
			<div class="care-ops-dashboard">
				<div class="summary-cards"></div>

				<div class="dashboard-section" id="attention-section"></div>

				<div class="dashboard-section" id="consultations-section"></div>

				<div class="dashboard-section" id="payments-section"></div>

				<div class="dashboard-section" id="doctor-section"></div>

				<div class="dashboard-section" id="customer-section"></div>
			</div>
		`);

		this.renderSummaryCards();
		this.renderAttentionRequired();
		this.renderConsultations();
		this.renderPayments();
		this.renderDoctorHealth();
		this.renderCustomerJourney();
	}

	renderSummaryCards() {
		const s = this.data.summary;

		this.page.main.find(".summary-cards").html(`
			<div class="ops-card critical">
				<div class="count">${s.critical}</div>
				<div class="label">Critical</div>
			</div>

			<div class="ops-card high">
				<div class="count">${s.high}</div>
				<div class="label">High</div>
			</div>

			<div class="ops-card medium">
				<div class="count">${s.medium}</div>
				<div class="label">Medium</div>
			</div>

			<div class="ops-card total">
				<div class="count">${s.total}</div>
				<div class="label">Total Alerts</div>
			</div>
		`);
	}

	renderAttentionRequired() {
		const rows = this.data.alerts.length
			? this.data.alerts.map(
					(alert) => `
				<tr>
					<td><span class="priority-badge ${alert.priority.toLowerCase()}">${alert.priority}</span></td>
					<td>${alert.category}</td>
					<td><strong>${alert.alert}</strong></td>
					<td>${alert.doctor || "-"}</td>
					<td>${alert.customer || "-"}</td>
					<td>${this.formatTime(alert.time)}</td>
					<td>${alert.action || "-"}</td>
				</tr>`
			  ).join("")
			: `<tr><td colspan="7" class="empty-state">No alerts requiring attention.</td></tr>`;

		this.page.main.find("#attention-section").html(`
			<h3 class="section-title">Attention Required</h3>

			<div class="table-responsive">
				<table class="table table-hover ops-table">
					<thead>
						<tr>
							<th>Priority</th>
							<th>Category</th>
							<th>Alert</th>
							<th>Doctor</th>
							<th>Customer</th>
							<th>Time</th>
							<th>Recommended Action</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`);
	}

	renderConsultations() {
		const rows = this.data.consultations.length
			? this.data.consultations.map(
					(c) => `
				<tr>
					<td><strong>${c.alert}</strong></td>
					<td>${c.doctor || "-"}</td>
					<td>${c.customer || "-"}</td>
					<td>${this.formatTime(c.time)}</td>
					<td>${c.action || "-"}</td>
				</tr>`
			  ).join("")
			: `<tr><td colspan="5" class="empty-state">No consultation alerts.</td></tr>`;

		this.page.main.find("#consultations-section").html(`
			<h3 class="section-title">Consultations</h3>

			<div class="table-responsive">
				<table class="table table-hover ops-table">
					<thead>
						<tr>
							<th>Alert</th>
							<th>Doctor</th>
							<th>Customer</th>
							<th>Time</th>
							<th>Recommended Action</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`);
	}

	renderPayments() {
		const rows = this.data.payments.length
			? this.data.payments.map(
					(p) => `
				<tr>
					<td>${p.customer || "-"}</td>
					<td>${p.reference || "-"}</td>
					<td>${p.alert || "Payment Failure"}</td>
					<td>${this.formatTime(p.time)}</td>
					<td>${p.action || "-"}</td>
				</tr>`
			  ).join("")
			: `<tr><td colspan="5" class="empty-state">No payment alerts.</td></tr>`;

		this.page.main.find("#payments-section").html(`
			<h3 class="section-title">Payments</h3>

			<div class="table-responsive">
				<table class="table table-hover ops-table">
					<thead>
						<tr>
							<th>Customer</th>
							<th>Appointment</th>
							<th>Status</th>
							<th>Time</th>
							<th>Recommended Action</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`);
	}

	renderDoctorHealth() {
		const rows = this.data.doctor_onboarding.length
			? this.data.doctor_onboarding.map(
					(d) => `
				<tr>
					<td>${d.doctor || "-"}</td>
					<td>${d.alert || "-"}</td>
					<td>${
						d.details
							? `<ul class="mb-0">${d.details.split(", ").map(item => `<li>${item}</li>`).join("")}</ul>`
							: "-"
					}</td>
				</tr>`
			  ).join("")
			: `<tr><td colspan="3" class="empty-state">No onboarding alerts.</td></tr>`;

		this.page.main.find("#doctor-section").html(`
			<h3 class="section-title">Doctor Onboarding Health</h3>

			<div class="table-responsive">
				<table class="table table-hover ops-table">
					<thead>
						<tr>
							<th>Doctor</th>
							<th>Issue</th>
							<th>Details</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`);
	}

	renderCustomerJourney() {
		const rows = this.data.customer_journey.length
			? this.data.customer_journey.map(
					(c) => `
				<tr>
					<td>${c.customer || "-"}</td>
					<td>${c.alert || "-"}</td>
					<td>${this.formatTime(c.time)}</td>
					<td>${c.details || "-"}</td>
				</tr>`
			  ).join("")
			: `<tr><td colspan="4" class="empty-state">No customer journey alerts.</td></tr>`;

		this.page.main.find("#customer-section").html(`
			<h3 class="section-title">Customer Journey Telemetry</h3>

			<div class="table-responsive">
				<table class="table table-hover ops-table">
					<thead>
						<tr>
							<th>Customer</th>
							<th>Issue</th>
							<th>Time</th>
							<th>Details</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`);
	}
}

frappe.dom.set_style(`
	.care-ops-dashboard {
		padding: 16px;
	}

	.care-ops-loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 60px 0;
		gap: 12px;
		color: #64748b;
	}

	.summary-cards {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 16px;
		margin-bottom: 24px;
	}

	.ops-card {
		background: #fff;
		border-radius: 14px;
		padding: 22px;
		box-shadow: 0 2px 8px rgba(0,0,0,.06);
		border-left: 6px solid #ddd;
	}

	.ops-card.critical { border-left-color: #dc2626; }
	.ops-card.high { border-left-color: #ea580c; }
	.ops-card.medium { border-left-color: #2563eb; }
	.ops-card.total { border-left-color: #64748b; }

	.ops-card .count {
		font-size: 34px;
		font-weight: 700;
		margin-bottom: 6px;
	}

	.ops-card .label {
		color: #666;
		font-size: 15px;
	}

	.dashboard-section {
		background: #fff;
		border-radius: 14px;
		padding: 20px;
		margin-bottom: 20px;
		box-shadow: 0 2px 8px rgba(0,0,0,.06);
	}

	.section-title {
		font-size: 20px;
		font-weight: 700;
		margin-bottom: 16px;
	}

	.ops-table {
		margin-bottom: 0;
	}

	.ops-table th {
		font-size: 13px;
		color: #64748b;
		font-weight: 600;
		border-top: none;
	}

	.ops-table td {
		vertical-align: middle;
		padding: 16px 12px;
	}

	.priority-badge {
		display: inline-block;
		padding: 5px 10px;
		border-radius: 999px;
		font-size: 12px;
		font-weight: 600;
	}

	.priority-badge.critical {
		background: #fee2e2;
		color: #991b1b;
	}

	.priority-badge.high {
		background: #ffedd5;
		color: #9a3412;
	}

	.priority-badge.medium {
		background: #dbeafe;
		color: #1d4ed8;
	}

	.table-responsive {
		overflow-x: auto;
	}

	.empty-state {
		text-align: center;
		color: #64748b;
		padding: 24px !important;
		font-style: italic;
	}
`);