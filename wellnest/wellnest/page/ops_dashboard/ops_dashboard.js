frappe.pages['ops-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Ops Dashboard',
        single_column: true
    });

    let current_page = 1;
    const items_per_page = 10;

    function load_dashboard_data(filters = {}, page_number = 1) {
        const offset = (page_number - 1) * items_per_page;

        frappe.call({
            method: 'wellnest.wellnest.page.ops_dashboard.ops_dashboard.get_dashboard_data',
            args: { filters: JSON.stringify(filters), limit: items_per_page, offset: offset },
            callback: function(response) {
                var data = response.message;

                // Clear existing content
                page.main.empty();

                // Filters UI
                create_filters(page.main, load_dashboard_data);

                // Caregiver Table
                var caregivers_table = $('<table class="table table-bordered">');
                caregivers_table.append('<thead><tr><th>Caregiver Name</th><th>Caregiver Type</th><th>Last Engagement</th><th>Status</th><th>Due Amount</th><th>Paid Amount</th></tr></thead><tbody>');
                data.caregivers.forEach(function(caregiver) {
                    caregivers_table.append('<tr><td>' + caregiver.caregiver_name + '</td><td>' + caregiver.caregiver_type + '</td><td>' + caregiver.last_engagement + '</td><td>' + caregiver.engagement_status + '</td><td>' + caregiver.due_amount + '</td><td>' + caregiver.paid_amount + '</td></tr>');
                });
                caregivers_table.append('</tbody>');
                page.main.append('<h3>Caregivers</h3>');
                page.main.append(caregivers_table);

                // Customer Table
                var customers_table = $('<table class="table table-bordered">');
                customers_table.append('<thead><tr><th>Customer Name</th><th>Engaged Caregivers</th><th>Status</th><th>Due Amount</th><th>Paid Amount</th></tr></thead><tbody>');
                data.customers.forEach(function(customer) {
                    customers_table.append('<tr><td>' + customer.customer_name + '</td><td>' + customer.engaged_caregivers + '</td><td>' + customer.engagement_status + '</td><td>' + customer.due_amount + '</td><td>' + customer.paid_amount + '</td></tr>');
                });
                customers_table.append('</tbody>');
                page.main.append('<h3>Customers</h3>');
                page.main.append(customers_table);

                // Pagination Controls
                create_pagination_controls(page.main, page_number, data.total_items, filters);
            }
        });
    }

    function create_filters(parent, on_apply_filters) {
        var filter_section = $('<div class="filters">');
        var caregiver_filter = $('<input type="text" placeholder="Search Caregiver" class="form-control" style="width: 200px; display: inline-block; margin-right: 10px;">');
        var customer_filter = $('<input type="text" placeholder="Search Customer" class="form-control" style="width: 200px; display: inline-block; margin-right: 10px;">');
        var apply_button = $('<button class="btn btn-primary">Apply Filters</button>');

        apply_button.on('click', function() {
            var filters = {
                caregiver_name: caregiver_filter.val(),
                customer_name: customer_filter.val()
            };
            on_apply_filters(filters);
        });

        filter_section.append('<h4>Filters</h4>');
        filter_section.append(caregiver_filter);
        filter_section.append(customer_filter);
        filter_section.append(apply_button);
        parent.append(filter_section);
    }

    function create_pagination_controls(parent, current_page, total_items, filters) {
        const total_pages = Math.ceil(total_items / items_per_page);

        const pagination_section = $('<div class="pagination-controls" style="margin-top: 20px;">');
        if (current_page > 1) {
            const prev_button = $('<button class="btn btn-secondary">Previous</button>');
            prev_button.on('click', function() {
                load_dashboard_data(filters, current_page - 1);
            });
            pagination_section.append(prev_button);
        }

        if (current_page < total_pages) {
            const next_button = $('<button class="btn btn-secondary">Next</button>');
            next_button.on('click', function() {
                load_dashboard_data(filters, current_page + 1);
            });
            pagination_section.append(next_button);
        }

        parent.append(pagination_section);
    }

    // Initialize data load
    load_dashboard_data();
};
