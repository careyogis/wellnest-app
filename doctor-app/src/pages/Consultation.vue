<template>
  <div class="w-full">
    <div class="space-y-6">
      <!-- Main consultation workspace -->
      <main class="space-y-6">
        <!-- Clinical findings -->
        <section class="bg-white border border-gray-200 rounded-2xl p-6">
          <input ref="prescriptionFileInput" type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" class="hidden" @change="handlePrescriptionFile" />

          <!-- Vitals -->
          <div class="mb-7">
            <button type="button" class="w-full flex items-center justify-between py-2 text-left" @click="vitalsExpanded = !vitalsExpanded">
              <div class="flex items-center gap-2">
                <h2 class="text-xl font-bold text-gray-900">Vitals</h2>
                <span class="text-sm text-gray-500">Optional</span>
              </div>

              <!-- Arrow -->
              <svg class="w-5 h-5 text-gray-500 transition-transform duration-200" :class="{ 'rotate-90': vitalsExpanded }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <!-- Vitals fields -->
            <div v-if="vitalsExpanded" class="mt-4">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div v-for="vital in vitals" :key="vital.key">
                  <label class="block text-sm text-gray-700 mb-2">
                    {{ vital.label }}
                    <span class="text-gray-400">({{ vital.unit }})</span>
                  </label>

                  <input
                    v-model="vital.value"
                    type="text"
                    :placeholder="vital.placeholder"
                    class="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Chief Complaints -->
          <div class="mb-7">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
              <h2 class="text-xl font-bold text-gray-900">Chief Complaints <span class="text-red-500">*</span></h2>

              <button type="button" class="px-4 py-2 rounded-lg bg-gray-50 text-gray-900 font-semibold hover:bg-gray-100" @click="addComplaint">Add complaint</button>
            </div>

            <div class="space-y-3">
              <div v-for="(complaint, index) in complaints" :key="complaint.id" class="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-3">
                <input
                  v-model="complaint.text"
                  type="text"
                  placeholder="Chief complaint"
                  class="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
                />

                <button v-if="complaints.length > 1" type="button" class="px-3 py-2 rounded-lg text-red-600 hover:bg-red-50" @click="removeComplaint(index)">Remove</button>
              </div>
            </div>
          </div>

          <!-- History -->
          <div class="mb-7">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-lg font-semibold text-gray-900">History <span class="text-red-500">*</span></h2>
            </div>

            <textarea
              v-model="history"
              rows="3"
              placeholder="Enter brief history"
              class="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 resize-y focus:outline-none focus:ring-2 focus:ring-amber-200"
            ></textarea>
          </div>

          <div class="h-6"></div>

          <!-- Examination -->
          <div class="mb-3">
            <h2 class="text-xl font-bold text-gray-900">Examination <span class="text-red-500">*</span></h2>
          </div>

          <textarea
            v-model="examination"
            rows="3"
            placeholder="Enter examination findings"
            class="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 resize-y focus:outline-none focus:ring-2 focus:ring-amber-200"
          ></textarea>

          <!-- Provisional Diagnosis -->
          <div class="mt-6">
            <h2 class="text-xl font-bold text-gray-900">Provisional Diagnosis <span class="text-red-500">*</span></h2>

            <textarea
              v-model="provisionalDiagnosis"
              rows="3"
              placeholder="Enter provisional diagnosis"
              class="w-full mt-3 rounded-xl border border-gray-200 px-4 py-3 text-gray-900 resize-y focus:outline-none focus:ring-2 focus:ring-amber-200"
            ></textarea>
          </div>
          <!-- Investigations advised -->
          <section class="mt-6 bg-white border border-gray-200 rounded-2xl p-6">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-4">
              <div>
                <h2 class="text-xl font-bold text-gray-900">Investigations advised</h2>

                <p class="text-gray-500 mt-1">Optional field, with autosuggest support for common advisories.</p>
              </div>

              <button type="button" class="w-full sm:w-auto px-4 py-2 rounded-xl bg-gray-50 text-gray-900 font-semibold hover:bg-gray-100" @click="addInvestigation">Add investigation</button>
            </div>

            <div class="space-y-3">
              <div v-for="(investigation, index) in investigations" :key="index" class="flex flex-col sm:flex-row sm:items-center gap-3">
                <input
                  v-model="investigations[index]"
                  type="text"
                  placeholder="Investigation"
                  class="flex-1 rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
                />

                <button type="button" class="shrink-0 px-3 py-2 rounded-lg text-red-600 bg-red-50 hover:bg-red-100 font-semibold text-sm" @click="removeInvestigation(index)">Remove</button>
              </div>
            </div>
          </section>
        </section>
        <!-- Treatment / Medication -->
        <section class="mt-6 bg-white border border-gray-200 rounded-2xl p-6">
          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-5">
            <div>
              <h2 class="text-xl font-bold text-gray-900">Treatment / Medication</h2>

              <p class="text-gray-500 mt-1">Brand or generic, dose, frequency, and instructions.</p>
            </div>

            <button type="button" class="px-4 py-2 rounded-xl bg-gray-50 text-gray-900 font-semibold hover:bg-gray-100" @click="addMedicine">Add medicine</button>
          </div>

          <!-- Table header -->
          <div class="hidden md:grid grid-cols-[1.2fr_1fr_1fr_1.2fr_auto] gap-4 px-2 pb-3 border-b border-gray-200 text-sm font-semibold text-gray-900">
            <div>Medicine</div>
            <div>Dose</div>
            <div>Frequency</div>
            <div>Instruction</div>
            <div></div>
          </div>

          <!-- Medicine rows -->
          <div class="space-y-0">
            <div v-for="(medicine, index) in medicines" :key="index" class="grid grid-cols-1 md:grid-cols-[1.2fr_1fr_1fr_1.2fr_auto] gap-4 py-3 border-b border-gray-200">
              <!-- Medicine -->
              <input
                v-model="medicine.medicine"
                type="text"
                placeholder="Brand / generic"
                class="w-full rounded-xl border border-gray-200 px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
              />

              <!-- Dose -->
              <input
                v-model="medicine.dose"
                type="text"
                placeholder="Dose"
                class="w-full rounded-xl border border-gray-200 px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
              />

              <!-- Frequency -->
              <input
                v-model="medicine.frequency"
                type="text"
                placeholder="Frequency"
                class="w-full rounded-xl border border-gray-200 px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
              />

              <!-- Instruction -->
              <input
                v-model="medicine.instruction"
                type="text"
                placeholder="Instruction"
                class="w-full rounded-xl border border-gray-200 px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
              />

              <!-- Remove -->
              <button type="button" class="self-center shrink-0 px-3 py-2 rounded-lg bg-red-50 text-red-600 text-sm font-semibold hover:bg-red-100" @click="removeMedicine(index)">Remove</button>
            </div>
          </div>
        </section>
        <!-- Follow-up Advice -->
        <section class="mt-6 bg-white border border-gray-200 rounded-2xl p-6">
          <div class="mb-5">
            <h2 class="text-xl font-bold text-gray-900">Follow-up Advice</h2>

            <p class="text-gray-500 mt-1">Add follow-up instructions for the patient.</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-900 mb-2"> Follow-up Advice </label>

            <textarea
              v-model="followUpAdvice"
              rows="3"
              placeholder="Enter follow-up advice"
              class="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 resize-y focus:outline-none focus:ring-2 focus:ring-amber-200"
            ></textarea>
          </div>
        </section>
      </main>
    </div>

    <!-- Template preview modal -->
    <div v-if="showPreview" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="showPreview = false">
      <div class="w-full max-w-6xl h-[90vh] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
        <!-- Preview modal header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
          <h2 class="text-2xl font-semibold text-gray-900">{{ patient.name }} prescription preview</h2>

          <button type="button" class="text-gray-500 hover:text-gray-900 text-3xl leading-none" @click="showPreview = false">×</button>
        </div>

        <!-- Scrollable prescription -->
        <div class="flex-1 overflow-y-auto px-5 py-5">
          <div class="border border-amber-200 bg-[#fffdf7] rounded-xl p-5">
            <!-- Prescription header -->
            <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4 pb-5 border-b border-amber-200">
              <!-- CareYogi logo + details -->
              <div class="flex flex-col sm:flex-row items-start gap-4">
                <img :src="careyogiLogo" alt="CareYogi" class="w-24 sm:w-32 h-auto object-contain shrink-0" />

                <div>
                  <h3 class="text-lg sm:text-xl font-bold text-gray-900 break-words">CAREYOGI DIGITAL CONSULTATION PRESCRIPTION</h3>

                  <p class="text-sm text-gray-600 mt-2 break-words">5th Floor, Adilakshmi Square, Plot No.137, Old Mumbai Highway, Gachibowli, Hyderabad, Telangana - 500032</p>

                  <p class="text-sm text-gray-600 mt-1 break-words">+91-9810918237 / info@careyogis.com</p>
                </div>
              </div>

              <!-- Status -->
              <span class="shrink-0 px-3 py-1 rounded-lg bg-emerald-100 text-emerald-700 text-xs font-semibold"> Digital draft </span>
            </div>

            <!-- Patient / consultation details -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mt-5">
              <div v-for="item in previewDetails" :key="item.label" class="border border-gray-200 bg-white rounded-xl p-4">
                <p class="text-xs text-gray-500">
                  {{ item.label }}
                </p>

                <p class="font-bold text-gray-900 mt-2">
                  {{ item.value }}
                </p>
              </div>
            </div>

            <!-- Doctor details -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
              <div v-for="item in doctorDetails" :key="item.label" class="border border-gray-200 bg-white rounded-xl p-4">
                <p class="text-xs text-gray-500">
                  {{ item.label }}
                </p>

                <p class="font-bold text-gray-900 mt-2">
                  {{ item.value }}
                </p>

                <p v-if="item.description" class="text-xs text-gray-500 mt-1">
                  {{ item.description }}
                </p>
              </div>
            </div>

            <!-- Chief Complaints -->
            <div class="mt-6">
              <h3 class="font-bold text-gray-900">Chief Complaints (with duration) <span class="text-red-500">*</span></h3>

              <ul class="list-disc pl-5 mt-2 space-y-1 text-sm text-gray-700">
                <li v-for="complaint in complaints" :key="complaint.id">
                  {{ complaint.text }}

                  <span v-if="complaint.duration"> ({{ complaint.duration }}) </span>
                </li>
              </ul>
            </div>

            <!-- History -->
            <div class="mt-5">
              <h3 class="font-bold text-gray-900">History (brief) <span class="text-red-500">*</span></h3>

              <p class="text-sm text-gray-700 mt-2">
                {{ history || 'No history entered.' }}
              </p>
            </div>

            <!-- Vitals -->
            <div class="mt-5">
              <h3 class="font-bold text-gray-900">Vitals</h3>

              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mt-4">
                <div v-for="vital in vitals" :key="vital.label" class="border border-gray-200 bg-white rounded-xl p-4">
                  <p class="text-xs uppercase text-gray-500">
                    {{ vital.label }}
                  </p>

                  <p class="font-bold text-gray-900 mt-2">
                    {{ vital.value }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Examination -->
            <div class="mt-5">
              <h3 class="font-bold text-gray-900">Examination <span class="text-red-500">*</span></h3>

              <p class="text-sm text-gray-700 mt-2">
                {{ examination || 'No examination findings entered.' }}
              </p>
            </div>

            <!-- Provisional Diagnosis -->
            <div class="mt-5">
              <h3 class="font-bold text-gray-900">Provisional Diagnosis <span class="text-red-500">*</span></h3>

              <p class="text-sm text-gray-700 mt-2">
                {{ provisionalDiagnosis || 'No provisional diagnosis entered.' }}
              </p>
            </div>

            <!-- Investigations -->
            <div class="mt-5">
              <h3 class="font-bold text-gray-900">Investigations Advised</h3>

              <ul class="list-disc pl-5 mt-2 space-y-1 text-sm text-gray-700">
                <li v-for="investigation in investigations.filter((item) => item)" :key="investigation">
                  {{ investigation }}
                </li>
              </ul>
            </div>

            <!-- Treatment / Medication -->
            <div class="mt-5">
              <h3 class="font-bold text-gray-900">Treatment / Medication</h3>

              <div class="mt-3 overflow-x-auto">
                <table class="w-full text-left text-sm">
                  <thead>
                    <tr class="bg-amber-100 border-b border-amber-200">
                      <th class="px-3 py-2 font-bold">Medicine (Brand / Generic)</th>

                      <th class="px-3 py-2 font-bold">Dose</th>

                      <th class="px-3 py-2 font-bold">Frequency</th>

                      <th class="px-3 py-2 font-bold">Instructions</th>
                    </tr>
                  </thead>

                  <tbody>
                    <tr v-for="(medicine, index) in medicines" :key="index" class="border-b border-gray-200">
                      <td class="px-3 py-2 text-gray-800">
                        {{ medicine.medicine }}
                      </td>

                      <td class="px-3 py-2 text-gray-800">
                        {{ medicine.dose }}
                      </td>

                      <td class="px-3 py-2 text-gray-800">
                        {{ medicine.frequency }}
                      </td>

                      <td class="px-3 py-2 text-gray-800">
                        {{ medicine.instruction }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Follow-up -->
            <div class="mt-6">
              <h3 class="font-bold text-gray-900">Follow-up Advise</h3>

              <p class="text-sm text-gray-700 mt-2">
                {{ followUpAdvice || 'No follow-up advice entered.' }}
              </p>
            </div>

            <!-- Digitally signed -->
            <div class="mt-6 pt-5 border-t border-amber-200">
              <h3 class="font-bold text-gray-900">Digitally Signed</h3>

              <p class="text-sm text-gray-600 mt-2">This is a digitally generated CareYogi prescription and does not require a physical signature.</p>
              <p class="text-sm text-gray-700 mt-2">© CareYogi 2026</p>
            </div>
          </div>
        </div>

        <!-- Preview footer -->
        <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-white shrink-0">
          <button type="button" class="px-5 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200" @click="showPreview = false">Close</button>
        </div>
      </div>
    </div>
  </div>
  <!-- OCR handwritten prescription modal -->
  <!-- Uploaded prescription modal -->
  <div v-if="showOcrModal" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="showOcrModal = false">
    <div class="w-full max-w-5xl max-h-[90vh] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
      <!-- Modal header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 shrink-0">
        <h2 class="text-xl font-semibold text-gray-900">Uploaded Prescription</h2>

        <button type="button" class="text-gray-500 hover:text-gray-900 text-3xl leading-none" @click="showOcrModal = false">×</button>
      </div>

      <!-- Uploaded prescription -->
      <div class="flex-1 overflow-y-auto p-5">
        <div class="min-h-[60vh] rounded-xl border border-gray-200 bg-gray-50 flex items-center justify-center p-4">
          <img
            v-if="prescriptionImagePreview"
            :src="prescriptionImagePreview"
            :alt="selectedPrescriptionFile?.name || 'Uploaded prescription'"
            class="max-w-full max-h-[70vh] object-contain rounded-lg"
          />

          <div v-else class="text-center text-gray-500">
            <FeatherIcon name="image" class="w-10 h-10 mx-auto mb-3" />

            <p class="font-medium">Prescription image is not available.</p>
          </div>
        </div>
      </div>

      <!-- Modal footer -->
      <div class="flex justify-end px-5 py-4 border-t border-gray-200 bg-white shrink-0">
        <button type="button" class="px-5 py-3 rounded-xl bg-gray-100 text-gray-700 font-semibold hover:bg-gray-200" @click="showOcrModal = false">Close</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed, ref, watch } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';
import careyogiLogo from '@/assets/images/logo-01.png';

const emit = defineEmits(['prescription-loaded', 'prescription-upload-processing']);

const props = defineProps({
  selectedConsultation: {
    type: Object,
    default: null,
  },
});

const clinicalRecordResource = createResource({
  url: 'wellnest.wellnest.doctype.teleconsultation_clinical_record.teleconsultation_clinical_record.get_clinical_record',
});

const saveClinicalRecordResource = createResource({
  url: 'wellnest.wellnest.doctype.teleconsultation_clinical_record.teleconsultation_clinical_record.save_clinical_record',
});

const vitalsResource = createResource({
  url: 'wellnest.wellnest.doctype.vitals.vitals.get_consultation_vitals',
});

const saveVitalsResource = createResource({
  url: 'wellnest.wellnest.doctype.vitals.vitals.save_consultation_vitals',
});

const createPrescriptionResource = createResource({
  url: 'wellnest.api.prescription.create_consultation_prescription',
});
const updatePrescriptionResource = createResource({
  url: 'wellnest.api.prescription.update_consultation_prescription',
});

const savePrescriptionDraftResource = createResource({
  url: 'wellnest.api.prescription.save_consultation_prescription_draft',
});

const getPrescriptionResource = createResource({
  url: 'wellnest.api.prescription.get_consultation_prescription',
});

const saveOcrPrescriptionResource = createResource({
  url: 'wellnest.api.prescription.save_ocr_prescription',
});

const completePrescriptionResource = createResource({
  url: 'wellnest.api.prescription.complete_consultation_prescription',
});

const startDoctorReviewResource = createResource({
  url: 'wellnest.api.prescription.start_doctor_review',
});

const ocrPrescriptionResource = createResource({
  url: 'wellnest.api.prescription.parse_and_create_prescription',
});

const patient = computed(() => ({
  name: props.selectedConsultation?.patient || 'Not Available',
}));

const consultation = computed(() => ({
  reason: props.selectedConsultation?.reason || 'Survivorship care plan',

  mode: props.selectedConsultation?.mode || 'Clinic',

  time: props.selectedConsultation?.time || 'Not Available',
}));

// Clinical Record data
const complaints = ref([]);
const investigations = ref([]);
const vitalsExpanded = ref(false);
const history = ref('');
const examination = ref('');
const provisionalDiagnosis = ref('');

const followUpAdvice = ref('');

// Existing prescription data - KEEP FOR NOW
const medicines = ref([]);
const prescriptionName = ref(null);
const prescriptionWorkflowState = ref(null);

// Existing vitals data - KEEP FOR NOW
const vitals = ref([
  {
    key: 'weight',
    label: 'Weight',
    placeholder: 'Weight',
    value: '',
    vitalType: 'Weight',
    unit: 'kg',
  },
  {
    key: 'height',
    label: 'Height',
    placeholder: 'Height',
    value: '',
    vitalType: 'Height',
    unit: 'cm',
  },
  {
    key: 'pulse',
    label: 'Pulse',
    placeholder: 'Pulse',
    value: '',
    vitalType: 'Heart Rate',
    unit: 'bpm',
  },
  {
    key: 'bp',
    label: 'BP',
    placeholder: 'Blood pressure',
    value: '',
    vitalType: 'BP',
    unit: 'mmHg',
  },
  {
    key: 'spo2',
    label: 'SpO2',
    placeholder: 'SpO2',
    value: '',
    vitalType: 'SPO2',
    unit: '%',
  },
  {
    key: 'temperature',
    label: 'Temperature',
    placeholder: 'Temperature',
    value: '',
    vitalType: 'Temperature',
    unit: '°C',
  },
  {
    key: 'sugar',
    label: 'Blood Sugar',
    placeholder: 'Blood sugar',
    value: '',
    vitalType: 'Sugar',
    unit: 'mg/dL',
  },
  {
    key: 'respiratory_rate',
    label: 'Respiratory Rate',
    placeholder: 'Respiratory rate',
    value: '',
    vitalType: 'Respiratory Rate',
    unit: 'breaths/min',
  },
]);

const showPreview = ref(false);
const showJoinModal = ref(false);
const showOcrModal = ref(false);
const ocrExtractedText = ref('');

const ocrPrescriptionName = ref('');
const ocrLoading = ref(false);

const prescriptionFileInput = ref(null);
const uploadWorkflowSection = ref(null);
const selectedPrescriptionFile = ref(null);
const prescriptionImagePreview = ref('');

async function loadClinicalRecord() {
  const appointment = props.selectedConsultation?.appointment;

  if (!appointment) {
    return;
  }

  try {
    // Load clinical record
    const response = await clinicalRecordResource.submit({
      appointment,
    });

    if (!response) {
      complaints.value = [];
      history.value = '';
    } else {
      complaints.value = (response.chief_complaints || []).map((complaint, index) => ({
        id: index + 1,
        text: complaint.complaint || '',
      }));

      history.value = response.history || '';
    }

    const prescriptionResponse = await getPrescriptionResource.submit({
      appointment,
    });

    const prescription = prescriptionResponse?.message || prescriptionResponse;

    if (prescription) {
      examination.value = prescription.examination || '';

      provisionalDiagnosis.value = prescription.provisional_diagnosis || '';

      investigations.value = prescription.investigations ? prescription.investigations.split('\n').filter((item) => item.trim()) : [];

      followUpAdvice.value = prescription.follow_up_advice || '';

      medicines.value = (prescription.medicines || []).map((medicine) => ({
        medicine: medicine.medicine_name || '',
        dose: medicine.dosage || '',
        frequency: medicine.timing || '',
        instruction: medicine.instructions || '',
      }));

      prescriptionName.value = prescription.name || null;

      prescriptionWorkflowState.value = prescription.workflow_state || null;
    } else {
      examination.value = '';
      provisionalDiagnosis.value = '';
      investigations.value = [];
      followUpAdvice.value = '';
      medicines.value = [];
      prescriptionName.value = null;
      prescriptionWorkflowState.value = null;
    }

    // Load vitals
    const vitalsResponse = await vitalsResource.submit({
      appointment,
    });

    // Clear current UI values first
    vitals.value.forEach((vital) => {
      vital.value = '';
    });

    // Populate saved vital values
    if (vitalsResponse?.vital_reading) {
      vitalsResponse.vital_reading.forEach((reading) => {
        const matchingVital = vitals.value.find((vital) => vital.vitalType === reading.vital_type);

        if (matchingVital) {
          matchingVital.value = reading.value || '';
        }
      });
    }
  } catch (error) {
    console.error('Failed to load consultation data:', error);
  }
}

async function loadPrescription() {
  const appointment = props.selectedConsultation?.appointment;

  console.log('>>> loadPrescription appointment:', appointment);

  if (!appointment) {
    return;
  }

  try {
    const response = await getPrescriptionResource.submit({
      appointment,
    });

    if (!response) {
      emit('prescription-loaded', null);
      return;
    }
    prescriptionName.value = response.name;
    prescriptionWorkflowState.value = response.workflow_state;

    if (response.file_url) {
      prescriptionImagePreview.value = response.file_url;
    }

    emit('prescription-loaded', {
      name: response.name,
      workflow_state: response.workflow_state,
      file_url: response.file_url || '',
    });

    ocrPrescriptionName.value = response.name;
    ocrExtractedText.value = JSON.stringify(
      {
        medicines: response.medicines || [],
        follow_up_advice: response.follow_up_advice || '',
      },
      null,
      2
    );

    medicines.value = (response.medicines || []).map((medicine) => ({
      medicine: medicine.medicine_name || '',
      dose: medicine.dosage || '',
      frequency: medicine.timing || '',
      instruction: medicine.instructions || '',
    }));

    followUpAdvice.value = response.follow_up_advice || '';
  } catch (error) {
    console.error('Failed to load prescription:', error);
  }
}

watch(
  () => props.selectedConsultation?.appointment,
  () => {
    if (prescriptionImagePreview.value) {
      URL.revokeObjectURL(prescriptionImagePreview.value);
    }

    selectedPrescriptionFile.value = null;
    prescriptionImagePreview.value = '';
    ocrLoading.value = false;
    showOcrModal.value = false;

    loadClinicalRecord();
    loadPrescription();
  },
  { immediate: true }
);

const previewDetails = computed(() => [
  {
    label: 'Patient',
    value: patient.value.name || 'Not Available',
  },
  {
    label: 'Consultation Type',
    value: consultation.value.mode || 'Not Available',
  },
  {
    label: 'Date',
    value: consultation.value.time ? consultation.value.time.split(',')[0] : 'Not Available',
  },
  {
    label: 'Time',
    value: consultation.value.time ? consultation.value.time.split(',').slice(1).join(',').trim() : 'Not Available',
  },
  {
    label: 'Appointment ID',
    value: props.selectedConsultation?.appointment || 'Not Available',
  },
]);
const doctorDetails = computed(() => [
  {
    label: 'Consulting Doctor',
    value: props.selectedConsultation?.practitioner || 'Not Available',
    description: '',
  },
  {
    label: 'Qualification',
    value: 'MBBS, MD (Internal Medicine)',
    description: '34 Years Experience',
  },
  {
    label: 'Registration',
    value: props.selectedConsultation?.registration_no || 'Not Available',
    description: 'Digitally signed draft',
  },
]);
function addComplaint() {
  complaints.value.push({
    id: Date.now(),
    text: '',
  });
}

function addInvestigation() {
  investigations.value.push('');
}

function removeInvestigation(index) {
  investigations.value.splice(index, 1);
}

function addMedicine() {
  medicines.value.push({
    medicine: '',
    dose: '',
    frequency: '',
    instruction: '',
  });
}

async function finalizePrescription() {
  if (prescriptionWorkflowState.value === 'Confirmed' || prescriptionWorkflowState.value === 'Complete') {
    alert('This prescription has already been submitted for this patient.');
    return;
  }

  if (!window.confirm('This prescription will be shared with the patient. Publish now?')) {
    return;
  }

  const appointment = props.selectedConsultation?.appointment;

  if (!appointment) {
    alert('No consultation selected.');
    return;
  }

  const hasChiefComplaint = complaints.value.some((complaint) => complaint.text?.trim());

  if (!hasChiefComplaint) {
    alert('Chief Complaint is required before submitting the prescription.');
    return;
  }

  if (!history.value?.trim()) {
    alert('History is required before submitting the prescription.');
    return;
  }

  if (!examination.value?.trim()) {
    alert('Examination is required before submitting the prescription.');
    return;
  }

  if (!provisionalDiagnosis.value?.trim()) {
    alert('Provisional Diagnosis is required before submitting the prescription.');
    return;
  }

  if (prescriptionWorkflowState.value === 'Confirmed') {
    alert('This prescription has already been submitted.');
    return;
  }

  try {
    const medicinesPayload = medicines.value
      .filter((medicine) => medicine.medicine?.trim())
      .map((medicine) => ({
        medicine_name: medicine.medicine.trim(),
        dosage: medicine.dose?.trim() || '',
        timing: medicine.frequency?.trim() || '',
        instructions: medicine.instruction?.trim() || '',
      }));

    let response;

    // If no prescription exists yet, create it as Draft first.
    if (!prescriptionName.value) {
      response = await createPrescriptionResource.submit({
        appointment,
        investigations: investigations.value.filter((investigation) => investigation?.trim()).join('\n'),
        examination: examination.value || '',
        provisional_diagnosis: provisionalDiagnosis.value || '',
        follow_up_advice: followUpAdvice.value || '',
        medicines: JSON.stringify(medicinesPayload),
      });

      prescriptionName.value = response.name;
      prescriptionWorkflowState.value = response.workflow_state;

      emit('prescription-loaded', {
        name: response.name,
        workflow_state: response.workflow_state,
        file_url: response.file_url || '',
      });
    } else if (prescriptionWorkflowState.value === 'Draft') {
      // Existing Draft: save the latest changes before submitting.
      response = await savePrescriptionDraftResource.submit({
        name: prescriptionName.value,
        appointment,

        investigations: investigations.value.filter((investigation) => investigation?.trim()).join('\n'),

        examination: examination.value || '',
        provisional_diagnosis: provisionalDiagnosis.value || '',
        follow_up_advice: followUpAdvice.value || '',

        medicines: JSON.stringify(medicinesPayload),
      });

      prescriptionWorkflowState.value = response?.workflow_state || 'Draft';
    }

    response = await completePrescriptionResource.submit({
      name: prescriptionName.value,
    });

    prescriptionWorkflowState.value = response.workflow_state;

    emit('prescription-submitted', {
      workflow_state: response.workflow_state,
    });

    console.log('Prescription submitted:', response);
    alert('Prescription submitted successfully.');
  } catch (error) {
    console.error('Failed to submit prescription:', error);
    alert('Failed to submit prescription.');
  }
}

async function savePrescriptionDraft(showMessage = true) {
  console.log('Current prescription workflow state:', prescriptionWorkflowState.value);

  if (prescriptionWorkflowState.value === 'Confirmed' || prescriptionWorkflowState.value === 'Complete') {
    alert('This prescription has already been submitted for this patient.');
    return;
  }

  const appointment = props.selectedConsultation?.appointment;

  if (!appointment) {
    alert('No consultation selected.');
    return;
  }

  try {
    const medicinesPayload = medicines.value
      .filter((medicine) => medicine.medicine?.trim())
      .map((medicine) => ({
        medicine_name: medicine.medicine.trim(),
        dosage: medicine.dose?.trim() || '',
        timing: medicine.frequency?.trim() || '',
        instructions: medicine.instruction?.trim() || '',
      }));

    const response = await savePrescriptionDraftResource.submit({
      name: prescriptionName.value || undefined,
      appointment,

      investigations: investigations.value.filter((investigation) => investigation?.trim()).join('\n'),

      examination: examination.value || '',
      provisional_diagnosis: provisionalDiagnosis.value || '',
      follow_up_advice: followUpAdvice.value || '',

      medicines: JSON.stringify(medicinesPayload),
    });

    if (response?.name) {
      prescriptionName.value = response.name;
    }

    prescriptionWorkflowState.value = response?.workflow_state || 'Draft';

    console.log('Prescription draft saved:', response);

    if (showMessage) {
      alert('Prescription saved as draft.');
    }
  } catch (error) {
    console.error('Failed to save prescription draft:', error);

    if (showMessage) {
      alert('Failed to save prescription draft.');
    }

    throw error;
  }
}

async function saveClinicalRecord(showMessage = true) {
  const appointment = props.selectedConsultation?.appointment;

  if (!appointment) {
    console.error('No consultation appointment selected.');
    return;
  }

  const data = {
    chief_complaints: complaints.value
      .filter((complaint) => complaint.text?.trim())
      .map((complaint) => ({
        complaint: complaint.text.trim(),
      })),

    history: history.value,
  };

  try {
    const response = await saveClinicalRecordResource.submit({
      appointment,
      data: JSON.stringify(data),
    });

    console.log('Clinical record saved:', response);

    const vitalReadings = vitals.value
      .filter((vital) => vital.value?.trim())
      .map((vital) => ({
        vital_type: vital.vitalType,
        unit: vital.unit,
        value: vital.value.trim(),
      }));

    const vitalsResponse = await saveVitalsResource.submit({
      appointment,
      readings: JSON.stringify(vitalReadings),
    });

    console.log('Vitals saved:', vitalsResponse);

    if (showMessage) {
      alert('Clinical record saved successfully.');
    }
  } catch (error) {
    console.error('Failed to save clinical record:', error);

    if (showMessage) {
      alert('Failed to save clinical record.');
    }

    throw error;
  }
}

async function handlePrescriptionFile(event) {
  const file = event.target.files?.[0];

  if (!file) return false;

  const allowedTypes = ['image/jpeg', 'image/png'];

  if (!allowedTypes.includes(file.type)) {
    alert('Please upload a JPG, JPEG, or PNG image.');
    event.target.value = '';
    return false;
  }

  selectedPrescriptionFile.value = file;

  emit('prescription-upload-processing', {
    fileName: file.name,
  });

  if (prescriptionImagePreview.value) {
    URL.revokeObjectURL(prescriptionImagePreview.value);
  }

  prescriptionImagePreview.value = URL.createObjectURL(file);

  ocrLoading.value = true;
  ocrExtractedText.value = 'Processing prescription...';

  try {
    // Upload image to Frappe
    const formData = new FormData();
    formData.append('file', file);

    const uploadResponse = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: {
        'X-Frappe-CSRF-Token': window.csrf_token,
      },
      body: formData,
    });

    const uploadResult = await uploadResponse.json();
    const fileUrl = uploadResult.message?.file_url;

    if (!fileUrl) {
      throw new Error('Failed to upload prescription image.');
    }

    // Show processing status immediately
    if (fileUrl) {
      prescriptionImagePreview.value = fileUrl;
    }

    ocrExtractedText.value = 'Prescription processing has started. You will be notified once it is ready for review.';

    // OCR will continue in the background.
    ocrLoading.value = false;

    fetch('/api/method/wellnest.api.prescription.parse_and_create_prescription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token,
      },
      body: JSON.stringify({
        file_url: fileUrl,
        patient: props.selectedConsultation?.patient || null,
        patient_appointment: props.selectedConsultation?.appointment || null,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`OCR request failed with status ${response.status}`);
        }

        return response.json();
      })
      .then((response) => {
        console.log('Prescription OCR processing completed:', response);
      })
      .catch((error) => {
        // Keep backend/OCR failures out of the doctor's UI.
        console.error('Prescription OCR processing failed:', error);
      });

    return true;
  } catch (error) {
    console.error('Prescription OCR failed:', error);

    ocrExtractedText.value = 'Prescription processing is temporarily unavailable. Please try again in a moment.';

    return false;
  } finally {
    ocrLoading.value = false;
  }
}

async function handleOcrSaveUpdate() {
  console.log('>>> SAVE/UPDATE CLICKED');
  if (!ocrPrescriptionName.value) {
    alert('Prescription not found.');
    return;
  }

  try {
    const response = await saveOcrPrescriptionResource.submit({
      name: ocrPrescriptionName.value,
      response_data: ocrExtractedText.value,
    });

    if (response) {
      alert('Prescription updated successfully.');
    }
  } catch (error) {
    console.error('Failed to update prescription:', error);
    alert('Failed to update prescription.');
  }
}

function removePrescriptionFile() {
  selectedPrescriptionFile.value = null;

  if (prescriptionImagePreview.value) {
    URL.revokeObjectURL(prescriptionImagePreview.value);
  }

  prescriptionImagePreview.value = '';

  if (prescriptionFileInput.value) {
    prescriptionFileInput.value.value = '';
  }
}

function removeMedicine(index) {
  medicines.value.splice(index, 1);
}

function removeComplaint(index) {
  complaints.value.splice(index, 1);
}

function insertComplaintSuggestion() {
  complaints.value.push({
    id: Date.now(),
    text: 'Elevated fasting glucose readings',
  });
}

function insertHistorySuggestion() {
  history.value = 'Known history of diabetes and hypertension.';
}

function insertExaminationSuggestion() {
  examination.value = 'General condition reviewed and relevant systems examined.';
}

function insertDiagnosisSuggestion() {
  console.log('Diagnosis suggestion selected.');
}

async function saveConsultation() {
  try {
    await saveClinicalRecord(false);
    await savePrescriptionDraft(false);

    alert('Consultation saved as draft.');
  } catch (error) {
    console.error('Failed to save consultation:', error);
    alert('Failed to save consultation.');
  }
}

function openOcrModal() {
  showOcrModal.value = true;
}

function focusUploadWorkflow() {
  uploadWorkflowSection.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  });
}

function previewTemplate() {
  showPreview.value = true;
}

function triggerUpload() {
  prescriptionFileInput.value?.click();
}

async function saveAll() {
  await saveClinicalRecord(false);

  if (prescriptionWorkflowState.value !== 'Confirmed' && prescriptionWorkflowState.value !== 'Complete') {
    await savePrescriptionDraft(false);
  }
}

defineExpose({
  previewTemplate,
  focusUploadWorkflow,
  saveConsultation,
  finalizePrescription,
  openOcrModal,
  handlePrescriptionFile,
  triggerUpload,
  selectedPrescriptionFile,
  prescriptionImagePreview,
  ocrLoading,
  ocrPrescriptionName,
  complaints,
  history,
  vitals,
  medicines,
  followUpAdvice,
  provisionalDiagnosis,
  investigations,
  previewDetails,
  doctorDetails,
});

async function finalizeDraft() {
  if (!prescriptionName.value) {
    alert('No prescription found.');
    return;
  }

  try {
    const response = await confirmPrescriptionResource.submit({
      name: prescriptionName.value,
    });

    prescriptionWorkflowState.value = response.workflow_state;

    console.log('Prescription confirmed:', response);

    alert('Prescription confirmed successfully.');
  } catch (error) {
    console.error('Failed to confirm prescription:', error);
    alert('Failed to confirm prescription.');
  }
}
</script>
