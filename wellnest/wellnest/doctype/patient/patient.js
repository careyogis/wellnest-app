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
                                padding: 10px;
                                margin-bottom: 10px;
                                border-radius: 6px;
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
                                    • <b>${reading.vital_type}</b> :
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
                                padding: 10px;
                                margin-bottom: 10px;
                                border-radius: 6px;
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
                                padding: 10px;
                                margin-bottom: 10px;
                                border-radius: 6px;
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
                                padding: 10px;
                                margin-bottom: 10px;
                                border-radius: 6px;
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
                                padding: 10px;
                                margin-bottom: 10px;
                                border-radius: 6px;
                            ">

                                <p>
                                    <b>Review Date:</b>
                                    ${r.review_date || '-'}
                                </p>

                                <p>
                                    <b>Summary:</b>
                                    ${r.summary || '-'}
                                </p>

                            </div>
                        `;
                    });

                    // -----------------------------------
                    // Final HTML
                    // -----------------------------------

                    let html = `
                        <div style="padding: 10px;">

                            <h2>Patient Health Timeline</h2>

                            <p>
                                Longitudinal patient care timeline displaying
                                vitals, medical history, reviews,
                                nurse observations, and risk indicators.
                            </p>

                            <hr>

                            <h3>Vitals</h3>
                            ${vitals_html || '<p>No vitals found.</p>'}

                            <hr>

                            <h3>Medical History</h3>
                            ${history_html || '<p>No medical history found.</p>'}

                            <hr>

                            <h3>Risk Flags</h3>
                            ${risk_html || '<p>No risk flags found.</p>'}

                            <hr>

                            <h3>Nurse Visits</h3>
                            ${visit_html || '<p>No nurse visits found.</p>'}

                            <hr>

                            <h3>Geriatric Reviews</h3>
                            ${review_html || '<p>No reviews found.</p>'}

                        </div>
                    `;

                    let d = new frappe.ui.Dialog({
                        title: 'Patient Timeline Summary',
                        size: 'large',
                        fields: [
                            {
                                fieldtype: 'HTML',
                                fieldname: 'timeline_html'
                            }
                        ]
                    });

                    d.fields_dict.timeline_html.$wrapper.html(html);

                    d.show();
                }
            });

        });

    }
});