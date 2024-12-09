frappe.pages['ops-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Ops Dashboard',
        single_column: true
    });

    // Function to fetch and display data
    function load_dashboard_data() {
        frappe.call({
            method: 'wellnest.wellnest.page.ops_dashboard.ops_dashboard.get_dashboard_data',
            callback: function(response) {
                var data = response.message;

                // Caregiver Table
                var caregivers_table = $('<table class="table table-bordered">');
                caregivers_table.append('<thead><tr><th>Caregiver Name</th><th>Caregiver Type</th><th>Last Engagement</th><th>Due Amount</th><th>Paid Amount</th></tr></thead><tbody>');
                data.caregivers.forEach(function(caregiver) {
                    caregivers_table.append('<tr><td>' + caregiver.caregiver_name + '</td><td>' + caregiver.caregiver_type + '</td><td>' + caregiver.last_engagement + '</td><td>' + caregiver.due_amount + '</td><td>' + caregiver.paid_amount + '</td></tr>');
                });
                caregivers_table.append('</tbody>');
                page.main.append(caregivers_table);

                // Customer Table
                var customers_table = $('<table class="table table-bordered">');
                customers_table.append('<thead><tr><th>Customer Name</th><th>Engaged Caregivers</th><th>Due Amount</th><th>Paid Amount</th></tr></thead><tbody>');
                data.customers.forEach(function(customer) {
                    customers_table.append('<tr><td>' + customer.customer_name + '</td><td>' + customer.engaged_caregivers + '</td><td>' + customer.due_amount + '</td><td>' + customer.paid_amount + '</td></tr>');
                });
                customers_table.append('</tbody>');
                page.main.append(customers_table);
            }
        });
    }

    // Call function to load dashboard data
    load_dashboard_data();
};
