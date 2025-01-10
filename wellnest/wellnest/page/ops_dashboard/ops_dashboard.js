frappe.pages['ops-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Ops Dashboard',
        single_column: true
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
            callback: function(response) {
                var data = response.message;

                page.main.empty();

                create_filters(page.main, load_dashboard_data, filters);

                render_table(page.main, "Caregivers", data.caregivers, [
                    "caregiver_name", "caregiver_type", "last_engagement", "status", "total_accrued_amount", "invoice_raised", "due_amount", "paid_amount", "engagement_id" // Added engagement_id
                ]);

                render_table(page.main, "Customers", data.customers, [
                    "customer_name", 
                    "engaged_caregivers", 
                    "status", 
                    "last_engagement", 
                    "invoice_raised", 
                    "outstanding_total", 
                    "paid_amount"
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

        apply_button.on('click', function() {
            var filters = {
                caregiver_name: caregiver_filter.val(),
                customer_name: customer_filter.val()
            };
            current_filters = filters;
            on_apply_filters(filters, 1);
        });

        remove_filter_button.on('click', function() {
            caregiver_filter.val("");
            customer_filter.val("");
            current_filters = {};
            on_apply_filters({}, 1);
        });

        filter_section.append(caregiver_filter, customer_filter, apply_button, remove_filter_button);
        parent.append(filter_section);
    }

    function render_table(parent, title, data, columns) {
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
                                    if (col === "status") {
                                        return `<td>${row[col]} <span class="status-dot ${row[col] === 'Engaged' ? 'status-engaged-dot' : 'status-not-engaged-dot'}"></span></td>`;
                                    } else if (col === "last_engagement") {
                                        return `<td>${row[col] ? new Date(row[col]).toLocaleDateString() : ''}</td>`;
                                    } else if (col === "engagement_id") {
                                        // Simply display the engagement ID without making it clickable
                                        return `<td>${row[col] || ''}</td>`;
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
    }

    function create_pagination_controls(parent, current_page, has_more_data, filters) {
        var pagination_controls = $('<div class="pagination-controls">');
        var previous_button = $('<button class="btn btn-link">Previous</button>');
        var next_button = $('<button class="btn btn-link">Next</button>');

        previous_button.on('click', function() {
            if (current_page > 1) {
                load_dashboard_data(filters, current_page - 1);
            }
        });

        next_button.on('click', function() {
            if (has_more_data) {
                load_dashboard_data(filters, current_page + 1);
            }
        });

        pagination_controls.append(previous_button, next_button);
        parent.append(pagination_controls);
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    load_dashboard_data(current_filters, current_page);
};
