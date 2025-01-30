frappe.pages['ops-dashboard'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Ops Dashboard',
        single_column: true,
    });

    var css = `
        .filter-input {
            width: auto;
            display: inline-block;
            margin-right: 10px;
            max-width: 250px;
            font-size: 14px;
        }

        .apply-button, .remove-filter-button {
            display: inline-block;
            font-size: 14px;
            margin-top: 5px;
        }

        .filters {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }

        .filters h4 {
            margin-right: 10px;
            font-size: 16px;
        }

        .status-engaged {
            color: green;
            font-size: 16px;
            display: inline-block;
            margin-left: 10px;
            font-weight: bold;
        }

        .status-not-engaged {
            color: red;
            font-size: 16px;
            display: inline-block;
            margin-left: 10px;
            font-weight: bold;
        }

        .status-dot {
            border-radius: 50%;
            width: 10px;
            height: 10px;
            display: inline-block;
            margin-left: 5px;
        }

        .status-engaged-dot {
            background-color: green;
        }

        .status-not-engaged-dot {
            background-color: red;
        }
    `;

    var style = $('<style>').text(css);
    $('head').append(style);

    let current_page = 1;
    const items_per_page = 10;
    let current_filters = {};

    function load_dashboard_data(filters = {}, page_number = 1) {
        const offset = (page_number - 1) * items_per_page;

        
    
        frappe.call({
            method: 'wellnest.wellnest.page.ops_dashboard.ops_dashboard.get_dashboard_data',
            args: { filters: JSON.stringify(filters), limit: items_per_page, offset: offset },
            callback: function (response) {
                var data = response.message;
    
                page.main.empty();
    
                create_filters(page.main, load_dashboard_data, filters);
    
                render_table(page.main, "Caregivers", data.caregivers, [
                    "caregiver_name", "caregiver_type", "last_engagement", "status", "total_accrued_amount", "invoice_raised", "due_amount", "paid_amount", "engagement_id"
                ]);
    
                render_table(page.main, "Customers", data.customers, [
                    "customer_name",
                    "status",
                    "last_engagement",
                    "invoice_raised",
                    "invoice_raised_date",
                    "outstanding_total",
                    "paid_amount",
                    "assigned_caregivers"  
                ]);
    
                create_pagination_controls(page.main, page_number, data.has_more, filters);
            }
        });
    }
    

    function create_filters(parent, on_apply_filters, filters) {
        var filter_section = $('<div class="filters" style="margin-bottom: 20px;">');
        var caregiver_filter = $('<input type="text" placeholder="Search Caregiver" class="form-control filter-input">');
        var customer_filter = $('<input type="text" placeholder="Search Customer" class="form-control filter-input">');
        var apply_button = $('<button class="btn btn-primary apply-button">Apply Filters</button>');
        var remove_filter_button = $('<button class="btn btn-secondary remove-filter-button">Remove Filter</button>');

        caregiver_filter.val(filters.caregiver_name || "");
        customer_filter.val(filters.customer_name || "");

        apply_button.on('click', function () {
            var filters = {
                caregiver_name: caregiver_filter.val(),
                customer_name: customer_filter.val()
            };
            current_filters = filters;
            on_apply_filters(filters, 1);
        });

        remove_filter_button.on('click', function () {
            caregiver_filter.val("");
            customer_filter.val("");
            current_filters = {};
            on_apply_filters({}, 1);
        });

        filter_section.append(caregiver_filter, customer_filter, apply_button, remove_filter_button);
        parent.append(filter_section);
    }

    function render_table(parent, title, data, columns) {
        data.sort((a, b) => {
            // Sort by status first: 'Engaged' should be higher priority than 'Not Engaged'
            if (a.status === "Engaged" && b.status !== "Engaged") return -1;
            if (a.status !== "Engaged" && b.status === "Engaged") return 1;
        
            // If both have the same status, sort by last engagement date in descending order
            const a_last_engagement = a.last_engagement ? new Date(a.last_engagement) : 0;
            const b_last_engagement = b.last_engagement ? new Date(b.last_engagement) : 0;
        
            return b_last_engagement - a_last_engagement; // Sort latest engagement first
        });
        

    var table_html = `
        <h3>${title}</h3>
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    ${columns.map(col => `<th>${capitalize(col.replace('_', ' '))}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
                ${data.map(row => {
                    return `
                        <tr>
                            ${columns.map(col => {
                                if (col === "caregiver_name") {
                                    return `<td><a href="javascript:void(0)" class="caregiver-link" data-caregiver="${row[col]}">${row[col]}</a></td>`;
                                } else if (col === "status") {
                                    return `<td>${row[col]} <span class="status-dot ${row[col] === 'Engaged' ? 'status-engaged-dot' : 'status-not-engaged-dot'}"></span></td>`;
                                } else if (col === "last_engagement") {
                                    return `<td>${row[col] ? new Date(row[col]).toLocaleDateString() : ''}</td>`;
                                } else if (col === "invoice_raised_date") {
                                    return `<td>${row[col] ? new Date(row[col]).toLocaleDateString() : 'No Date'}</td>`;
                                } else if (col === "assigned_caregivers") {
                                    const caregivers = row["assigned_caregivers"] ? row["assigned_caregivers"].split(', ') : "No caregivers assigned";
                                    return `<td>${caregivers}</td>`;
                                } else {
                                    return `<td>${row[col] || ''}</td>`;
                                }
                            }).join('')}
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
    parent.append(table_html);

    // Prevent double event binding
    parent.find('.caregiver-link').off('click').on('click', function () {
        const caregiver_name = $(this).data('caregiver');
        show_caregiver_popup(caregiver_name);
    });
}

    

    function show_caregiver_popup(caregiver_name) {
        frappe.call({
            method: 'wellnest.wellnest.page.ops_dashboard.ops_dashboard.get_engagements_for_caregiver',
            args: { caregiver_name: caregiver_name },
            callback: function (response) {
                const engagements = response.message.engagements || [];
                const invoices = response.message.invoices ? [response.message.invoices] : [];
                const payments = response.message.payments ? [response.message.payments] : [];
    
                // Prepare Engagements Table
                const engagementRows = engagements.length
                    ? engagements.map(e => `
                        <tr>
                            <td>${e.engagement_id}</td>
                            <td>${e.start_date ? new Date(e.start_date).toLocaleDateString() : '-'}</td>
                            <td>${e.end_date ? new Date(e.end_date).toLocaleDateString() : '-'}</td>
                        </tr>
                    `).join('')
                    : `<tr><td colspan="3">No engagements found</td></tr>`;
    
                // Prepare Invoices Table
                const invoiceRows = invoices.length
                    ? invoices.map(i => `
                        <tr>
                            <td>${i.outstanding_amount}</td>
                        </tr>
                    `).join('')
                    : `<tr><td>No invoices found</td></tr>`;
    
                // Prepare Payments Table
                const paymentRows = payments.length
                    ? payments.map(p => `
                        <tr>
                            <td>${p.amount_paid}</td>
                        </tr>
                    `).join('')
                    : `<tr><td>No payments found</td></tr>`;
    
                const popupHtml = `
                    <div>
                        <h3>Caregiver Details</h3>
                        <p><strong>Name:</strong> ${caregiver_name}</p>
    
                        <h4>Engagements</h4>
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>Engagement ID</th>
                                    <th>Start Date</th>
                                    <th>End Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${engagementRows}
                            </tbody>
                        </table>
    
                        <h4>Generated Invoices</h4>
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>Outstanding Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${invoiceRows}
                            </tbody>
                        </table>
    
                        <h4>Paid Out</h4>
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>Amount Paid</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${paymentRows}
                            </tbody>
                        </table>
                    </div>
                `;
    
                // Display popup with the caregiver details
                frappe.msgprint({
                    title: `Details for ${caregiver_name}`,
                    indicator: 'green',
                    message: `<div>${popupHtml}</div>`, // Wrap content to avoid re-adding content
                });
            },
        });
    }

    function create_pagination_controls(parent, page_number, has_more, filters) {
        const pagination = $('<div class="pagination-controls">');
        if (page_number > 1) {
            const prevButton = $('<button class="btn btn-secondary">Previous</button>');
            prevButton.on('click', function () {
                load_dashboard_data(filters, page_number - 1);
            });
            pagination.append(prevButton);
        }

        if (has_more) {
            const nextButton = $('<button class="btn btn-secondary">Next</button>');
            nextButton.on('click', function () {
                load_dashboard_data(filters, page_number + 1);
            });
            pagination.append(nextButton);
        }

        parent.append(pagination);
    }

    load_dashboard_data();
};

function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
}
