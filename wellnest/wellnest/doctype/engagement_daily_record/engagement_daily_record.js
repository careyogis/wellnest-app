// Copyright (c) 2024, www.careyogis.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Engagement Daily Record", {
	refresh(frm) {

    },        
    async engagement(frm) {
        source_doc = null;
        if(frm.doc.engagement){
            try {
                // Load Engagement
                source_doc = await frappe.db.get_doc('Engagement', frm.doc.engagement);
            } catch (error) {
                // Handle any errors that occur during the fetch
                console.error('Error fetching data:', error);
            }

            in_clause = "";
            if (source_doc) {
                number_of_caregivers = 0; 
                $.each(source_doc.assigned_caregivers, function (index, source_row) {                    
                    if (number_of_caregivers == 0) {
                        in_clause = source_row.caregiver;
                    } 
                    else {
                        in_clause += ', ' + source_row.caregiver;
                    }
                    number_of_caregivers++;
                });
                
                // If there's only 1 caregiver assigned, set it in the field
                if (number_of_caregivers == 1){
                    frm.set_value('caregiver', in_clause);
                }
                
                // Restrict the caregiver selection to only the ones assigned in this engagement
                frm.fields_dict['caregiver'].get_query = function(doc) {
                    return {
                        filters: [
                            ['name', 'in', in_clause]
                        ]
                    }
                }    

                // frm.refresh_field('caregiver');
                // Refresh the child table with activities from the selected Engagement           
                frm.clear_table('performed_activities');
                $.each(source_doc.required_activity, function (index, source_row) {
                    target_row = frm.add_child('performed_activities');
                    target_row.activity = source_row.activity;
                    target_row.prescribed_time = source_row.prescribed_time;
                    target_row.notes = source_row.notes;
                });

                frm.refresh_field('performed_activities');
            }
        }
    },
});
