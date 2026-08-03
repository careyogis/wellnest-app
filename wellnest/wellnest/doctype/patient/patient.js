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
                            border:1px solid #e5e7eb;
                            border-radius:12px;
                            background:#fff;
                            padding:20px;
                            margin-bottom:20px;
                            box-shadow:0 2px 8px rgba(0,0,0,.06);
                        ">

                            <div style="
                                display:flex;
                                justify-content:space-between;
                                border-bottom:1px solid #ececec;
                                padding-bottom:12px;
                                margin-bottom:18px;
                            ">

                                <div>
                                    <div style="font-size:12px;color:#777;">
                                        Recorded On
                                    </div>

                                    <div style="font-weight:600;">
                                        ${vital.recorded_on || "-"}
                                    </div>
                                </div>

                                <div style="text-align:right;">
                                    <div style="font-size:12px;color:#777;">
                                        Recorded By
                                    </div>

                                    <div style="font-weight:600;">
                                        ${vital.recorded_by || "-"}
                                    </div>
                                </div>

                            </div>

                            <div style="
                                display:grid;
                                grid-template-columns:1fr 1fr;
                                gap:12px 40px;
                            ">
                        `;

                        (vital.vital_reading || []).forEach(reading => {

                            vitals_html += `
                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    align-items:center;
                                    padding:8px 0;
                                    border-bottom:1px dashed #eee;
                                ">

                                    <span
                                        class="view-vital-trend"
                                        data-vital="${reading.vital_type}"
                                        style="
                                            color:#3366cc;
                                            cursor:pointer;
                                            font-weight:600;
                                            text-decoration:none;
                                        "
                                    >
                                        ${reading.vital_type}
                                    </span>

                                    <span style="font-weight:600;">

                                        ${reading.value || "-"}
                                        ${reading.unit || ""}

                                    </span>

                                </div>
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
                            border:1px solid #e5e7eb;
                            border-radius:12px;
                            background:#fff;
                            padding:20px;
                            margin-bottom:20px;
                            box-shadow:0 2px 8px rgba(0,0,0,.06);
                        ">

                            <div style="
                                display:grid;
                                grid-template-columns:1fr 1fr;
                                gap:12px 40px;
                            ">

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Condition</span>
                                    <span><b>${h.condition_name || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>ICD-10 Code</span>
                                    <span><b>${h.icd_10_code || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Status</span>
                                    <span><b>${h.status || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Chronic</span>
                                    <span><b>${h.chronic ? "Yes" : "No"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Onset Date</span>
                                    <span><b>${h.onset_date || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Allergies</span>
                                    <span><b>${h.allergies || "-"}</b></span>
                                </div>

                                <div style="
                                    grid-column:1 / span 2;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span><b>Notes</b></span><br>
                                    <span>${h.notes || "-"}</span>
                                </div>

                            </div>

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
                            border:1px solid #e5e7eb;
                            border-radius:12px;
                            background:#fff;
                            padding:20px;
                            margin-bottom:20px;
                            box-shadow:0 2px 8px rgba(0,0,0,.06);
                        ">

                            <div style="
                                display:grid;
                                grid-template-columns:1fr 1fr;
                                gap:12px 40px;
                            ">

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Flag Type</span>
                                    <span><b>${risk.flag_type || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Severity</span>
                                    <span><b>${risk.severity || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Status</span>
                                    <span><b>${risk.status || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Created At</span>
                                    <span><b>${risk.created_at || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Resolved At</span>
                                    <span><b>${risk.resolved_at || "-"}</b></span>
                                </div>

                                <div></div>

                                <div style="
                                    grid-column:1 / span 2;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span><b>Description</b></span><br>
                                    <span>${risk.description || "-"}</span>
                                </div>

                            </div>

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
                            border:1px solid #e5e7eb;
                            border-radius:12px;
                            background:#fff;
                            padding:20px;
                            margin-bottom:20px;
                            box-shadow:0 2px 8px rgba(0,0,0,.06);
                        ">

                            <div style="
                                display:grid;
                                grid-template-columns:1fr 1fr;
                                gap:12px 40px;
                            ">

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Visit Date</span>
                                    <span><b>${v.visit_date || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Nurse</span>
                                    <span><b>${v.nurse_id || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Mobility Observation</span>
                                    <span><b>${v.mobility_observation || "-"}</b></span>
                                </div>

                                <div></div>

                                <div style="
                                    grid-column:1 / span 2;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span><b>Concerns</b></span><br>
                                    <span>${v.concerns || "-"}</span>
                                </div>

                                <div style="
                                    grid-column:1 / span 2;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span><b>Vitals Summary</b></span><br>
                                    <span>${v.vitals_summary || "-"}</span>
                                </div>

                                <div style="
                                    grid-column:1 / span 2;
                                ">
                                    <span><b>Next Actions</b></span><br>
                                    <span>${v.next_actions || "-"}</span>
                                </div>

                            </div>

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
                            border:1px solid #e5e7eb;
                            border-radius:12px;
                            background:#fff;
                            padding:20px;
                            margin-bottom:20px;
                            box-shadow:0 2px 8px rgba(0,0,0,.06);
                        ">

                            <div style="
                                display:grid;
                                grid-template-columns:1fr 1fr;
                                gap:12px 40px;
                            ">

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Review Date</span>
                                    <span><b>${r.review_date || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Reviewer HPR</span>
                                    <span><b>${r.reviewer_hpr || "-"}</b></span>
                                </div>

                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span>Risk Flags</span>
                                    <span><b>${r.risk_flags || "-"}</b></span>
                                </div>

                                <div></div>

                                <div style="
                                    grid-column:1 / span 2;
                                    border-bottom:1px dashed #eee;
                                    padding-bottom:8px;
                                ">
                                    <span><b>Summary</b></span><br>
                                    <span>${r.summary || "-"}</span>
                                </div>

                                <div style="
                                    grid-column:1 / span 2;
                                ">
                                    <span><b>Recommendations</b></span><br>
                                    <span>${r.recommendations || "-"}</span>
                                </div>

                            </div>

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
                                border:1px solid #e5e7eb;
                                border-radius:12px;
                                background:#fff;
                                padding:20px;
                                margin-bottom:20px;
                                box-shadow:0 2px 8px rgba(0,0,0,.06);
                            ">

                                <div style="
                                    display:grid;
                                    grid-template-columns:1fr 1fr;
                                    gap:12px 40px;
                                    margin-bottom:20px;
                                ">

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:8px;
                                    ">
                                        <span>Prescribed By</span>
                                        <span><b>${med.prescribed_by || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:8px;
                                    ">
                                        <span>Adherence Status</span>
                                        <span><b>${med.adherence_status || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:8px;
                                    ">
                                        <span>Created On</span>
                                        <span><b>${med.creation || "-"}</b></span>
                                    </div>

                                    <div></div>

                                    <div style="
                                        grid-column:1 / span 2;
                                    ">
                                        <span><b>Notes</b></span><br>
                                        <span>${med.notes || "-"}</span>
                                    </div>

                                </div>

                                <h4 style="
                                    margin:0 0 15px;
                                    color:#444;
                                    border-bottom:1px solid #eee;
                                    padding-bottom:8px;
                                ">
                                    Medicines
                                </h4>
                            `;

                       (med.medication_items || []).forEach(item => {

                            medication_html += `
                            <div style="
                                border:1px solid #f0f0f0;
                                border-radius:10px;
                                padding:15px;
                                margin-bottom:15px;
                                background:#fafafa;
                            ">

                                <div style="
                                    font-size:16px;
                                    font-weight:600;
                                    margin-bottom:15px;
                                ">
                                    💊 ${item.medicine_name || "-"}
                                </div>

                                <div style="
                                    display:grid;
                                    grid-template-columns:1fr 1fr;
                                    gap:12px 30px;
                                ">

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:6px;
                                    ">
                                        <span>Dosage</span>
                                        <span><b>${item.dosage || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:6px;
                                    ">
                                        <span>Frequency</span>
                                        <span><b>${item.frequency || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:6px;
                                    ">
                                        <span>Start Date</span>
                                        <span><b>${item.start_date || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:6px;
                                    ">
                                        <span>End Date</span>
                                        <span><b>${item.end_date || "-"}</b></span>
                                    </div>

                                </div>

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
                                border:1px solid #e5e7eb;
                                border-radius:12px;
                                background:#fff;
                                padding:20px;
                                margin-bottom:20px;
                                box-shadow:0 2px 8px rgba(0,0,0,.06);
                            ">

                                <div style="
                                    display:grid;
                                    grid-template-columns:1fr 1fr;
                                    gap:12px 40px;
                                ">

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:8px;
                                    ">
                                        <span>Document Type</span>
                                        <span><b>${doc.document_type || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:8px;
                                    ">
                                        <span>LOINC Code</span>
                                        <span><b>${doc.loinc_code || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:8px;
                                    ">
                                        <span>Uploader</span>
                                        <span><b>${doc.uploader || "-"}</b></span>
                                    </div>

                                    <div style="
                                        display:flex;
                                        justify-content:space-between;
                                        border-bottom:1px dashed #eee;
                                        padding-bottom:8px;
                                    ">
                                        <span>Document</span>

                                        ${
                                            doc.file
                                                ? `<a href="${doc.file}" target="_blank">View Document</a>`
                                                : "<span>-</span>"
                                        }

                                    </div>

                                </div>

                            </div>
                            `;
                    });

                    // -----------------------------------
                    // Final HTML
                    // -----------------------------------

                    let html = `
                            <div style="
                                padding:25px;
                                max-height:82vh;
                                overflow-y:auto;
                                background:#f7f8fa;
                            ">
                            <h2 style="
                                margin-bottom:8px;
                                font-size:32px;
                                font-weight:700;
                            ">
                                Patient Health Timeline
                            </h2>

                            <p style="
                                color:#666;
                                font-size:15px;
                                margin-bottom:25px;
                            ">
                                Longitudinal patient care timeline displaying vitals,
                                medical history, medications, nurse observations,
                                reviews, documents and clinical risk indicators.
                            </p>

                            <hr>

                            <h3 style="
                                margin-top:30px;
                                margin-bottom:15px;
                                padding-bottom:10px;
                                border-bottom:2px solid #3366cc;
                            ">
                                Vitals
                            </h3>
                            ${vitals_html || '<p>No vitals found.</p>'}

                            <hr>

                            <h3 style="
                                margin-top:30px;
                                margin-bottom:15px;
                                padding-bottom:10px;
                                border-bottom:2px solid #3366cc;
                            ">
                                Medical History
                            </h3>
                            ${history_html || '<p>No medical history found.</p>'}

                            <hr>

                            <h3 style="
                                margin-top:30px;
                                margin-bottom:15px;
                                padding-bottom:10px;
                                border-bottom:2px solid #3366cc;
                            ">
                                Medications
                            </h3>
                            ${medication_html || '<p>No medications found.</p>'}

                            <hr>

                            <h3 style="
                                margin-top:30px;
                                margin-bottom:15px;
                                padding-bottom:10px;
                                border-bottom:2px solid #3366cc;
                            ">
                                Risk Flags
                            </h3>
                            ${risk_html || '<p>No risk flags found.</p>'}

                            <hr>

                            <h3 style="
                                margin-top:30px;
                                margin-bottom:15px;
                                padding-bottom:10px;
                                border-bottom:2px solid #3366cc;
                            ">
                                Nurse Visits
                            </h3>
                            ${visit_html || '<p>No nurse visits found.</p>'}

                            <hr>

                            <h3 style="
                                margin-top:30px;
                                margin-bottom:15px;
                                padding-bottom:10px;
                                border-bottom:2px solid #3366cc;
                            ">
                                Geriatric Reviews
                            </h3>
                            ${review_html || '<p>No reviews found.</p>'}

                            <hr>

                            <h3 style="
                                margin-top:30px;
                                margin-bottom:15px;
                                padding-bottom:10px;
                                border-bottom:2px solid #3366cc;
                            ">
                                Medical Documents
                            </h3>
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

                // Make timeline popup wider
                d.$wrapper.find('.modal-dialog').css({
                    width: '95vw',
                    'max-width': '95vw'
                });

                d.$wrapper.find('.modal-content').css({
                    height: '90vh'
                });

                d.$wrapper.find('.modal-body').css({
                    'max-height': '80vh',
                    overflow: 'auto'
                });

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
                                           border:1px solid #e5e7eb;
                                            padding:18px;
                                            margin-bottom:18px;
                                            border-radius:12px;
                                            background:#ffffff;
                                            box-shadow:0 2px 8px rgba(0,0,0,.06);
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
                                // Make trend popup wider
                                trend_dialog.$wrapper.find('.modal-dialog').css({
                                    width: '90vw',
                                    'max-width': '90vw'
                                });

                                trend_dialog.$wrapper.find('.modal-content').css({
                                    height: '88vh'
                                });

                                trend_dialog.$wrapper.find('.modal-body').css({
                                    overflow: 'auto'
                                });

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
                                            },

                                            {
                                                name: 'Normal Range',
                                                values: labels.map(() => {

                                                    if (vital_type === 'BP') return 120;

                                                    if (vital_type === 'SPO2') return 95;

                                                    if (vital_type === 'Heart Rate') return 60;

                                                    if (vital_type === 'Temperature') return 98;

                                                    if (vital_type === 'Sugar') return 140;

                                                    if (vital_type === 'Weight') return 75;

                                                    if (vital_type === 'Respiratory Rate') return 16;

                                                    return 0;
                                                })
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