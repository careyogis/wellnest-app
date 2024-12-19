frappe.pages['ops-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Ops Dashboard',
        single_column: true
    });

    // Embed CSS styles directly in the page
    var css = `
        /* Make filter search inputs small */
        .filter-input {
            width: auto;
            display: inline-block;
            margin-right: 10px;
            max-width: 250px;  /* Adjust size as needed */
            font-size: 14px;
        }

        /* Adjust filter buttons to fit */
        .apply-button, .remove-filter-button {
            display: inline-block;
            font-size: 14px;
            margin-top: 5px;
        }

        /* Adjust filter section for alignment */
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
    `;
    // Add styles to the page
    var style = $('<style>').text(css);
    $('head').append(style);

    let current_page = 1;
    const items_per_page = 10;
    let current_filters = {}; // Store filters for removing them later

    function load_dashboard_data(filters = {}, page_number = 1) {
        const offset = (page_number - 1) * items_per_page;

        frappe.call({
            method: 'wellnest.wellnest.page.ops_dashboard.ops_dashboard.get_dashboard_data',
            args: { filters: JSON.stringify(filters), limit: items_per_page, offset: offset },
            callback: function(response) {
                var data = response.message;

                // Clear page content
                page.main.empty();

                // Add filters UI
                create_filters(page.main, load_dashboard_data, filters);

                // Caregivers Table
                render_table(page.main, "Caregivers", data.caregivers, [
                    "caregiver_name", "caregiver_type", "last_engagement", "status", "due_amount", "paid_amount"
                ]);

                // Customers Table
                render_table(page.main, "Customers", data.customers, [
                    "customer_name", "engaged_caregivers", "status", "due_amount", "paid_amount"
                ]);

                // Pagination Controls
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

        // Set the filter inputs to the current filter values (if any)
        caregiver_filter.val(filters.caregiver_name || "");
        customer_filter.val(filters.customer_name || "");

        apply_button.on('click', function() {
            var filters = {
                caregiver_name: caregiver_filter.val(),
                customer_name: customer_filter.val()
            };
            current_filters = filters;  // Store filters for later removal
            on_apply_filters(filters, 1);  // Apply filters and reload data
        });

        remove_filter_button.on('click', function() {
            caregiver_filter.val("");  // Clear caregiver filter
            customer_filter.val("");   // Clear customer filter
            current_filters = {};      // Reset current filters
            on_apply_filters({}, 1);   // Reload data without filters
        });

        // Append elements to filter section
        filter_section.append('<h4>Filters</h4>');
        filter_section.append(caregiver_filter);
        filter_section.append(customer_filter);
        filter_section.append(apply_button);
        filter_section.append(remove_filter_button);
        parent.append(filter_section);
    }

    function render_table(parent, title, data, columns) {
        var table = $('<table class="table table-bordered">');
        var thead = '<thead><tr>' + columns.map(col => `<th>${col.replace('_', ' ').toUpperCase()}</th>`).join('') + '</tr></thead>';
        table.append(thead);

        var tbody = $('<tbody>');
        data.forEach(row => {
            var tr = $('<tr>');
            columns.forEach(col => {
                tr.append(`<td>${row[col] || ''}</td>`);
            });
            tbody.append(tr);
        });

        table.append(tbody);
        parent.append(`<h3>${title}</h3>`);
        parent.append(table);
    }

    function create_pagination_controls(parent, current_page, has_more, filters) {
        const pagination = $('<div class="pagination-controls" style="margin-top: 20px;">');

        if (current_page > 1) {
            const prev_button = $('<button class="btn btn-secondary">Previous</button>');
            prev_button.on('click', () => load_dashboard_data(filters, current_page - 1));
            pagination.append(prev_button);
        }

        if (has_more) {
            const next_button = $('<button class="btn btn-secondary">Next</button>');
            next_button.on('click', () => load_dashboard_data(filters, current_page + 1));
            pagination.append(next_button);
        }

        pagination.append(`<span>Page ${current_page}</span>`);
        parent.append(pagination);
    }

    // Initial data load
    load_dashboard_data();
};
