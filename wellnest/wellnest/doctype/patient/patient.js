// Copyright (c) 2026, www.careyogis.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Patient", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Patient', {
    refresh(frm) {

        frm.add_custom_button('View Timeline', () => {

            frappe.call({
                method: 'wellnest.wellnest.doctype.patient.patient.get_patient_timeline',
                args: {
                    patient: frm.doc.name
                },

                callback: function(r) {

                    let data = r.message;

                                        // -----------------------------------
                    // Vitals
                    // -----------------------------------

                    let vitals_html = '';

                    data.vitals.forEach(vital => {

                        vitals_html += `
                            <div style="
                                border: 1px solid #ddd;
                                padding: 14px;
                                margin-bottom: 14px;
                                border-radius: 8px;
                                background: #fafafa;
                            ">

                                <p>
                                    <b>Recorded On:</b>
                                    ${vital.recorded_on || '-'}
                                </p>

                                <p>
                                    <b>Recorded By:</b>
                                    ${vital.recorded_by || '-'}
                                </p>

                                <div style="margin-left: 15px;">
                        `;

                        (vital.vital_reading || []).forEach(reading => {

                            vitals_html += `
                                <p>
                                    • 
                                    <span
                                        class="view-vital-trend"
                                        data-vital="${reading.vital_type}"
                                        style="
                                            color: #3366cc;
                                            cursor: pointer;
                                            font-weight: bold;
                                            text-decoration: underline;
                                        "
                                    >
                                        ${reading.vital_type}
                                    </span>

                                    :
                                    ${reading.value || '-'}
                                    ${reading.unit || ''}
                                </p>
                            `;
                        });

                        vitals_html += `
                                </div>
                            </div>
                        `;
                    });
                    
                    // -----------------------------------
                    // Medical History
                    // -----------------------------------

                    let history_html = '';

                    data.medical_history.forEach(h => {

                        history_html += `
                            <div style="
                                border: 1px solid #ddd;
                                padding: 14px;
                                margin-bottom: 14px;
                                border-radius: 8px;
                                background: #fafafa;
                            ">

                                <p>
                                    <b>Condition:</b>
                                    ${h.condition_name || '-'}
                                </p>

                                <p>
                                    <b>ICD 10 Code:</b>
                                    ${h.icd_10_code || '-'}
                                </p>

                                <p>
                                    <b>Status:</b>
                                    ${h.status || '-'}
                                </p>

                                <p>
                                    <b>Chronic:</b>
                                    ${h.chronic ? 'Yes' : 'No'}
                                </p>

                                <p>
                                    <b>Onset Date:</b>
                                    ${h.onset_date || '-'}
                                </p>

                                <p>
                                    <b>Allergies:</b>
                                    ${h.allergies || '-'}
                                </p>

                                <p>
                                    <b>Notes:</b>
                                    ${h.notes || '-'}
                                </p>

                            </div>
                        `;
                    });

                    // -----------------------------------
                    // Risk Flags
                    // -----------------------------------

                    let risk_html = '';

                    data.risk_flags.forEach(risk => {

                        risk_html += `
                            <div style="
                                border: 1px solid #ddd;
                                padding: 14px;
                                margin-bottom: 14px;
                                border-radius: 8px;
                                background: #fafafa;
                            ">

                                <p>
                                    <b>Flag Type:</b>
                                    ${risk.flag_type || '-'}
                                </p>

                                <p>
                                    <b>Severity:</b>
                                    ${risk.severity || '-'}
                                </p>

                                <p>
                                    <b>Status:</b>
                                    ${risk.status || '-'}
                                </p>

                                <p>
                                    <b>Description:</b>
                                    ${risk.description || '-'}
                                </p>

                                <p>
                                    <b>Created At:</b>
                                    ${risk.created_at || '-'}
                                </p>

                                <p>
                                    <b>Resolved At:</b>
                                    ${risk.resolved_at || '-'}
                                </p>

                            </div>
                        `;
                    });

                    // -----------------------------------
                    // Nurse Visits
                    // -----------------------------------

                    let visit_html = '';

                    data.nurse_visits.forEach(v => {

                        visit_html += `
                            <div style="
                                border: 1px solid #ddd;
                                padding: 14px;
                                margin-bottom: 14px;
                                border-radius: 8px;
                                background: #fafafa;
                            ">

                                <p>
                                    <b>Visit Date:</b>
                                    ${v.visit_date || '-'}
                                </p>

                                <p>
                                    <b>Nurse:</b>
                                    ${v.nurse_id || '-'}
                                </p>

                                <p>
                                    <b>Concerns:</b>
                                    ${v.concerns || '-'}
                                </p>

                                <p>
                                    <b>Vitals Summary:</b>
                                    ${v.vitals_summary || '-'}
                                </p>

                                <p>
                                    <b>Mobility Observation:</b>
                                    ${v.mobility_observation || '-'}
                                </p>

                                <p>
                                    <b>Next Actions:</b>
                                    ${v.next_actions || '-'}
                                </p>

                            </div>
                        `;
                    });

                    // -----------------------------------
                    // Geriatric Reviews
                    // -----------------------------------

                    let review_html = '';

                    data.reviews.forEach(r => {

                        review_html += `
                            <div style="
                                border: 1px solid #ddd;
                                padding: 14px;
                                margin-bottom: 14px;
                                border-radius: 8px;
                                background: #fafafa;
                            ">

                                <p>
                                    <b>Review Date:</b>
                                    ${r.review_date || '-'}
                                </p>

                                <p>
                                    <b>Reviewer HPR:</b>
                                    ${r.reviewer_hpr || '-'}
                                </p>

                                <p>
                                    <b>Summary:</b>
                                    ${r.summary || '-'}
                                </p>

                                <p>
                                    <b>Recommendations:</b>
                                    ${r.recommendations || '-'}
                                </p>

                                <p>
                                    <b>Risk Flags:</b>
                                    ${r.risk_flags || '-'}
                                </p>

                            </div>
                        `;
                    });

                    // -----------------------------------
                    // Medications
                    // -----------------------------------

                    let medication_html = '';

                    data.medications.forEach(med => {

                        medication_html += `
                            <div style="
                                border: 1px solid #ddd;
                                padding: 14px;
                                margin-bottom: 14px;
                                border-radius: 8px;
                                background: #fafafa;
                            ">

                                <p>
                                    <b>Prescribed By:</b>
                                    ${med.prescribed_by || '-'}
                                </p>

                                <p>
                                    <b>Adherence Status:</b>
                                    ${med.adherence_status || '-'}
                                </p>

                                <p>
                                    <b>Notes:</b>
                                    ${med.notes || '-'}
                                </p>

                                <p>
                                    <b>Created On:</b>
                                    ${med.creation || '-'}
                                </p>

                                <hr>

                                <h4>Medicines</h4>
                        `;

                        (med.medication_items || []).forEach(item => {

                            medication_html += `
                                <div style="
                                    margin-bottom: 10px;
                                    padding-left: 10px;
                                ">

                                    <p>
                                        • <b>${item.medicine_name || '-'}</b>
                                    </p>

                                    <p>
                                        Dosage:
                                        ${item.dosage || '-'}
                                    </p>

                                    <p>
                                        Frequency:
                                        ${item.frequency || '-'}
                                    </p>

                                    <p>
                                        Start Date:
                                        ${item.start_date || '-'}
                                    </p>

                                    <p>
                                        End Date:
                                        ${item.end_date || '-'}
                                    </p>

                                </div>
                            `;
                        });

                        medication_html += `
                            </div>
                        `;
                    });

                    // -----------------------------------
                    // Medical Documents
                    // -----------------------------------

                    let document_html = '';

                    data.medical_documents.forEach(doc => {

                        document_html += `
                            <div style="
                                border: 1px solid #ddd;
                                padding: 14px;
                                margin-bottom: 14px;
                                border-radius: 8px;
                                background: #fafafa;
                            ">

                                <p>
                                    <b>Document Type:</b>
                                    ${doc.document_type || '-'}
                                </p>

                                <p>
                                    <b>LOINC Code:</b>
                                    ${doc.loinc_code || '-'}
                                </p>

                                <p>
                                    <b>Uploader:</b>
                                    ${doc.uploader || '-'}
                                </p>

                                <p>
                                    <b>File:</b>
                                    <a href="${doc.file}" target="_blank">
                                        View Document
                                    </a>
                                </p>

                            </div>
                        `;
                    });

                    // -----------------------------------
                    // Final HTML
                    // -----------------------------------

                    let html = `
                        <div style="
                            padding: 15px;
                            max-height: 80vh;
                            overflow-y: auto;
                        ">

                            <h2>Patient Health Timeline</h2>

                            <p>
                                Longitudinal patient care timeline displaying
                                vitals, medical history, medications,
                                nurse observations, reviews,
                                documents, and risk indicators.
                            </p>

                            <hr>

                            <h3>Vitals</h3>
                            ${vitals_html || '<p>No vitals found.</p>'}

                            <hr>

                            <h3>Medical History</h3>
                            ${history_html || '<p>No medical history found.</p>'}

                            <hr>

                            <h3>Medications</h3>
                            ${medication_html || '<p>No medications found.</p>'}

                            <hr>

                            <h3>Risk Flags</h3>
                            ${risk_html || '<p>No risk flags found.</p>'}

                            <hr>

                            <h3>Nurse Visits</h3>
                            ${visit_html || '<p>No nurse visits found.</p>'}

                            <hr>

                            <h3>Geriatric Reviews</h3>
                            ${review_html || '<p>No reviews found.</p>'}

                            <hr>

                            <h3>Medical Documents</h3>
                            ${document_html || '<p>No documents found.</p>'}

                        </div>
                    `;

                    let d = new frappe.ui.Dialog({
                        title: 'Patient Timeline Summary',
                        size: 'extra-large',
                        minimizable: true,
                        fields: [
                            {
                                fieldtype: 'HTML',
                                fieldname: 'timeline_html'
                            }
                        ]
                    });

                    d.fields_dict.timeline_html.$wrapper.html(html);

                    d.show();
                    d.$wrapper.on('click', '.view-vital-trend', function() {

                        let vital_type = $(this).data('vital');

                        frappe.call({
                            method: 'wellnest.wellnest.doctype.patient.patient.get_vital_trend',

                            args: {
                                patient: frm.doc.name,
                                vital_type: vital_type
                            },

                            callback: function(r) {

                                let trend_data = r.message.trend_data || [];

                                let normal_range = r.message.normal_range || '-';

                                let observation = r.message.observation || '-';

                                let trend_html = '';

                                trend_data.forEach(t => {

                                    trend_html += `
                                        <div style="
                                            border: 1px solid #ddd;
                                            padding: 12px;
                                            margin-bottom: 10px;
                                            border-radius: 6px;
                                            background: #fafafa;
                                        ">

                                            <p>
                                                <b>Date:</b>
                                                ${t.date || '-'}
                                            </p>

                                            <p>
                                                <b>Value:</b>
                                                ${t.value || '-'}
                                                ${t.unit || ''}
                                            </p>

                                            <p>
                                                <b>Change:</b>
                                                ${t.change || '-'}
                                            </p>

                                        </div>
                                    `;
                                });

                                let trend_dialog = new frappe.ui.Dialog({
                                    title: `${vital_type} Trend`,
                                    size: 'large',
                                    fields: [
                                        {
                                            fieldtype: 'HTML',
                                            fieldname: 'trend_html'
                                        }
                                    ]
                                });

                                trend_dialog.fields_dict.trend_html.$wrapper.html(`
                                    <div style="
                                        padding: 15px;
                                        max-height: 70vh;
                                        overflow-y: auto;
                                    ">

                                        <h3>${vital_type} Changes Over Time</h3>

                                        <hr>

                                        <div
                                            id="vital-chart"
                                            style="
                                                height: 300px;
                                                margin-bottom: 25px;
                                            "
                                        ></div>

                                        ${trend_html || '<p>No trend data found.</p>'}

                                        <hr>

                                        <p>
                                            <b>Normal Range:</b>
                                            ${normal_range}
                                        </p>

                                        <p>
                                            <b>Observation:</b>
                                            ${observation}
                                        </p>

                                    </div>
                                `);

                                trend_dialog.show();

                                // =====================================
                                // Render Chart
                                // =====================================

                                let labels = trend_data.map(d => d.date);

                                            let values = trend_data.map(d => d.chart_value);

                                            // Get chart container 
                                            let chart_container = trend_dialog.fields_dict.trend_html.$wrapper.find('#vital-chart')[0];

                                            new frappe.Chart(chart_container, {
                                    title: `${vital_type} Trend`,

                                    data: {
                                        labels: labels,

                                        datasets: [
                                            {
                                                name: vital_type,
                                                values: values
                                            }
                                        ]
                                    },

                                    type: 'line',

                                    height: 280,

                                    lineOptions: {
                                        regionFill: 1
                                    }
                                });

                            }
                        });

                    });

                }
            });

        });

    }

});