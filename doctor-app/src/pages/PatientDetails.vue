<template>
  <div class="p-5 md:p-8">
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">
          {{ patient.name }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          Longitudinal care record aligned with the currently selected consultation workspace.
        </p>
      </div>

      <div class="flex gap-2">

       <button
        @click="messagePatient"
        class="rounded-lg border border-amber-400 px-4 py-2 text-sm font-semibold text-amber-700"
         >
          Message
         </button>
            <button
            @click="returnToSelectedConsult"
            class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white"
           >
           Open booked consult
          </button>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-5 xl:grid-cols-[0.8fr_1.8fr]">
      <!-- Left column -->
      <div class="space-y-5">
        <section class="rounded-xl border border-gray-200 bg-white p-5">
          <div class="text-center">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-emerald-600 text-xl font-bold text-white">
              {{ initials(patient.name) }}
            </div>
            <h2 class="mt-3 text-xl font-semibold">{{ patient.name }}</h2>
            <p class="mt-2 text-sm text-gray-500">
              {{ patient.age }} yrs · {{ patient.gender }} · {{ patient.location }}
            </p>

          </div>

          <div class="grid grid-cols-2 gap-4">
        <!--<div>
              <p class="text-sm text-gray-500">Adherence</p>
              <p class="font-semibold">{{ patient.adherence }}%</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Next visit</p>
              <p class="font-semibold">{{ patient.nextVisit }}</p>
            </div>-->
          </div>
        </section>

        <section class="rounded-xl border border-gray-200 bg-white p-5">
          <h2 class="text-lg font-semibold">Emergency contact</h2>
          <p class="mt-3 text-sm">
            <strong>{{ patient.emergencyContact }}</strong>,
            {{ patient.emergencyRelationship }}
          </p>
          <p class="mt-2 text-sm text-gray-500">{{ patient.emergencyPhone }}</p>
        </section>

<section class="rounded-xl border border-gray-200 bg-white p-5">
  <h2 class="text-lg font-semibold">Current consult linkage</h2>

  <div class="mt-3 rounded-lg border border-gray-200 bg-gray-50 p-4">
    <p class="font-semibold">{{ patient.consultationReason }}</p>
    <p class="mt-2 text-sm text-gray-500">
      {{ patient.consultationType }} · {{ patient.consultationDate }}
    </p>
  </div>

  <button
  v-if="route.query.appointment"
  type="button"
  class="mt-3 w-full rounded-lg border border-amber-500 px-4 py-2.5 text-sm font-semibold text-amber-700 hover:bg-amber-50"
  @click="returnToSelectedConsult"
>
  Return to selected consult
</button>
</section>

      </div>

      <!-- Right column -->
      <div class="min-w-0">
        <div class="mb-4 flex flex-wrap gap-1 rounded-xl bg-gray-100 p-2">
          <button
            v-for="tab in tabs"
            :key="tab"
            @click="activeTab = tab"
            class="rounded-lg px-3 py-2 text-sm font-semibold"
            :class="activeTab === tab
              ? 'bg-white text-amber-600 shadow-sm'
              : 'text-gray-600 hover:bg-white'"
          >
            {{ tab }}
          </button>
        </div>

        <section class="min-h-64 rounded-xl border border-gray-200 bg-white p-5 md:p-6">
          <h2 class="mb-5 text-lg font-semibold">{{ activeTab }}</h2>

          <div v-if="activeTab === 'Timeline'" class="space-y-4">
  <template v-for="item in timeline" :key="item.id">
    <div
      v-if="item.type === 'appointment'"
      class="rounded-xl border border-gray-200 bg-white p-4"
    >
      <h3 class="font-semibold text-gray-900">
        Appointment
      </h3>

      <p class="mt-1 text-sm text-gray-500">
        Scheduled:
        {{ item.scheduledTime ? formatTimelineDate(item.scheduledTime) : 'Date not available' }}
      </p>

      <p class="mt-1 text-sm text-gray-500">
        Appointment ID: {{ item.appointmentId || 'Not available' }}
      </p>

      <p
        v-if="item.mainComplaints"
        class="mt-2 text-sm text-gray-700"
      >
        Reason: {{ item.mainComplaints }}
      </p>

      <div
        v-for="prescription in item.prescriptions"
        :key="prescription.name"
        class="mt-3 border-t border-gray-200 pt-3"
      >
        <p class="font-semibold text-gray-900">Prescription</p>

        <p class="mt-1 text-sm text-gray-500">
          Status: {{ prescription.workflow_state || 'Not available' }}
        </p>

        <p
          v-if="prescription.completionDate"
          class="mt-1 text-sm text-gray-500"
        >
          Completed on: {{ formatTimelineDate(prescription.completionDate) }}
        </p>
        </div>

      <p
        v-if="!item.prescriptions.length"
        class="mt-3 text-sm text-gray-500"
      >
        No linked prescription found.
      </p>
    </div>

    <div
      v-else
      class="rounded-xl border border-gray-200 bg-white p-4"
    >
      <h3 class="font-semibold text-gray-900">{{ item.title }}</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ formatTimelineDate(item.date) }}
      </p>
      <p class="mt-1 text-sm text-gray-600">{{ item.description }}</p>
    </div>
  </template>
</div>


      <!-- Conditions -->
<div v-else-if="activeTab === 'Conditions'" class="space-y-3">
  <div
    v-for="consultation in consultationHistory"
    :key="consultation.patient_appointment"
    class="rounded-lg border border-gray-200 bg-white p-4"
  >
    <h3 class="font-semibold text-gray-900">
      Consultation — {{ formatTimelineDate(consultation.scheduled_time) }}
    </h3>

    <div
      v-for="prescription in consultation.prescriptions || []"
      :key="prescription.name"
      class="mt-3 border-t border-gray-100 pt-3"
    >
      <p class="font-medium text-gray-800">History</p>
      <p class="mt-1 whitespace-pre-wrap text-sm text-gray-600">
        {{ prescription.history || 'No history recorded for this appointment.' }}
      </p>
    </div>

    <p
      v-if="!(consultation.prescriptions || []).length"
      class="mt-3 text-sm text-gray-500"
    >
      No history recorded for this appointment.
    </p>
  </div>

  <p
    v-if="!consultationHistory.length"
    class="text-sm text-gray-500"
  >
    No history recorded for this appointment.
  </p>
</div>

       <!-- Medications -->
<div v-else-if="activeTab === 'Medications'" class="space-y-3">
  <div
    v-for="(medicine, index) in historicalMedicines"
    :key="`${medicine.prescription_name}-${medicine.name || index}`"
    class="rounded-lg border border-gray-200 bg-white p-4"
  >
    <p class="text-sm font-semibold text-gray-500">
      Consultation:
      {{ formatTimelineDate(medicine.consultation_date) }}
    </p>

    <div class="mt-3 overflow-x-auto">
      <table class="w-full border-collapse text-left text-sm">
        <thead>
          <tr class="bg-amber-100 text-gray-800">
            <th class="border-b border-amber-200 px-3 py-2 font-semibold">
              Medicine
            </th>
            <th class="border-b border-amber-200 px-3 py-2 font-semibold">
              Dose
            </th>
            <th class="border-b border-amber-200 px-3 py-2 font-semibold">
              Frequency
            </th>
            <th class="border-b border-amber-200 px-3 py-2 font-semibold">
              Instructions
            </th>
          </tr>
        </thead>

        <tbody>
          <tr class="text-gray-700">
            <td class="border-b border-gray-100 px-3 py-2">
              {{ medicine.medicine_name || 'Medicine' }}
            </td>
            <td class="border-b border-gray-100 px-3 py-2">
              {{ medicine.dosage || 'Not specified' }}
            </td>
            <td class="border-b border-gray-100 px-3 py-2">
              {{ medicine.timing || 'Not specified' }}
            </td>
            <td class="break-words border-b border-gray-100 px-3 py-2">
              {{ medicine.instructions || 'Not specified' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p
      v-if="medicine.main_complaints"
      class="mt-2 text-sm text-gray-500"
    >
      Reason: {{ medicine.main_complaints }}
    </p>
  </div>

  <p
    v-if="!historicalMedicines.length"
    class="text-sm text-gray-500"
  >
    No medications found for this appointment.
  </p>
</div>

<!-- Vitals -->
<div v-else-if="activeTab === 'Vitals'" class="space-y-3">
  <div
    v-if="timelineResource.data?.vitals?.length"
    class="space-y-4"
  >
    <div
      v-for="(vital, index) in timelineResource.data.vitals"
      :key="vital.name || index"
      class="rounded-lg border border-gray-200 bg-white p-4"
    >
      <h3 class="font-semibold text-gray-900">
        Consultation — {{ formatTimelineDate(vital.appointment_date || vital.recorded_on) }}
      </h3>

      <div
        v-if="vital.vital_reading?.length"
        class="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2"
      >
        <div
          v-for="(reading, readingIndex) in vital.vital_reading"
          :key="readingIndex"
          class="rounded-lg border border-gray-200 p-3"
        >
          <p class="text-sm text-gray-500">
            {{ reading.vital_type || 'Vital' }}
          </p>
          <p class="mt-1 break-words font-semibold text-gray-900">
            {{ reading.value ?? '—' }}
            <span class="text-sm font-normal text-gray-500">
              {{ reading.unit }}
            </span>
          </p>
          <p
            v-if="reading.remarks"
            class="mt-1 whitespace-pre-wrap text-sm text-gray-600"
          >
            {{ reading.remarks }}
          </p>
        </div>
      </div>
    </div>
  </div>

  <p v-else class="text-sm text-gray-500">
    No vitals recorded for this patient.
  </p>
</div>

<!-- Prescriptions -->
<div v-else-if="activeTab === 'Prescriptions'" class="space-y-3">
  <!-- Historical prescriptions -->
  <div
    v-for="prescription in historicalPrescriptions"
    :key="prescription.name"
    class="rounded-xl border border-gray-200 bg-white p-5"
  >
    <div class="flex items-center justify-between gap-3">
      <h3 class="font-semibold text-gray-900">
       Prescription — {{
  new Date(
    prescription.prescription_date ||
    prescription.creation ||
    prescription.scheduled_time
  ).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}}
      </h3>

      <button
        type="button"
        class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600"
        @click="openPrescriptionPreview(prescription)"
      >
        Preview prescription
      </button>
    </div>
  </div>

  <!-- Selected appointment prescription -->
  <div
    v-if="
      prescriptionResource.data &&
      !historicalPrescriptions.some(
        (item) => item.name === prescriptionResource.data.name
      )
    "
    class="rounded-xl border border-gray-200 bg-white p-5"
  >
    <div class="flex items-center justify-between gap-3">
      <h3 class="font-semibold text-gray-900">
        Prescription — {{
          formatTimelineDate(
            prescriptionResource.data.prescription_date ||
            prescriptionResource.data.creation
          )
        }}
      </h3>

      <button
        type="button"
        class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600"
        @click="openPrescriptionPreview(prescriptionResource.data)"
      >
        Preview prescription
      </button>
    </div>
  </div>

  <p
    v-if="
      !prescriptionResource.data &&
      !historicalPrescriptions.length
    "
    class="text-sm text-gray-500"
  >
    No prescriptions found for this patient.
  </p>
</div>

  <!-- Prescription Preview Modal -->
  <div
    v-if="showPrescriptionPreview && activePrescriptionPreview"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    @click.self="showPrescriptionPreview = false"
  >
    <div class="flex max-h-[90vh] w-full max-w-6xl flex-col overflow-hidden rounded-2xl bg-white shadow-xl">
      <div class="flex shrink-0 items-center justify-between border-b border-gray-200 px-6 py-4">
        <h2 class="text-2xl font-semibold text-gray-900">
          {{ patient.name }} prescription preview
        </h2>

        <button
          type="button"
          class="text-3xl leading-none text-gray-500 hover:text-gray-900"
          @click="showPrescriptionPreview = false"
        >
          ×
        </button>
      </div>

      <div class="flex-1 overflow-y-auto px-5 py-5">
        <div class="rounded-xl border border-amber-200 bg-[#fffdf7] p-5">
          <div class="flex flex-col gap-4 border-b border-amber-200 pb-5 md:flex-row md:items-start md:justify-between">
            <div class="flex flex-col items-start gap-4 sm:flex-row">
              <img
                :src="careyogiLogo"
                alt="CareYogi"
                class="h-auto w-24 shrink-0 object-contain sm:w-32"
              />

              <div>
                <h3 class="break-words text-lg font-bold text-gray-900 sm:text-xl">
                  CAREYOGI DIGITAL CONSULTATION PRESCRIPTION
                </h3>
                <p class="mt-2 break-words text-sm text-gray-600">
                  5th Floor, Adilakshmi Square, Plot No.137, Old Mumbai Highway,
                  Gachibowli, Hyderabad, Telangana - 500032
                </p>
                <p class="mt-1 break-words text-sm text-gray-600">
                  +91-9810918237 / info@careyogis.com
                </p>
              </div>
            </div>

            <span class="shrink-0 rounded-lg bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
              {{ activePrescriptionPreview.workflow_state || 'Prescription' }}
            </span>
          </div>

          <div class="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-4">
            <div
              v-for="item in prescriptionPreviewDetails"
              :key="item.label"
              class="rounded-xl border border-gray-200 bg-white p-4"
            >
              <p class="text-xs text-gray-500">{{ item.label }}</p>
              <p class="mt-2 break-words font-bold text-gray-900">{{ item.value }}</p>
            </div>
          </div>

          <!-- Doctor Details -->
          <div class="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
            <div
              v-for="item in prescriptionPreviewDoctorDetails"
              :key="item.label"
              class="rounded-xl border border-gray-200 bg-white p-4"
            >
              <p class="text-xs text-gray-500">{{ item.label }}</p>
              <p class="mt-2 break-words font-bold text-gray-900">
                {{ item.value }}
              </p>
              <p v-if="item.description" class="mt-1 text-xs text-gray-500">
                {{ item.description }}
              </p>
            </div>
          </div>

<!-- Chief Complaints -->
<div class="mt-6">
  <h3 class="font-bold text-gray-900">Chief Complaints</h3>

  <div
    v-if="prescriptionChiefComplaints.length"
    class="mt-3 space-y-2"
  >
    <div
      v-for="(complaint, index) in prescriptionChiefComplaints"
      :key="index"
      class="rounded-lg border border-gray-200 bg-white p-3"
    >
      <p class="font-medium text-gray-900">
        {{ complaint.complaint || complaint.name || 'Complaint' }}
      </p>
      <p
        v-if="complaint.duration"
        class="mt-1 text-sm text-gray-600"
      >
        Duration: {{ complaint.duration }}
      </p>
    </div>
  </div>

  <p v-else class="mt-2 text-sm text-gray-500">
    No chief complaints recorded.
  </p>
</div>

<!-- History -->
<div class="mt-5">
  <h3 class="font-bold text-gray-900">History</h3>
  <p class="mt-2 whitespace-pre-wrap break-words text-sm text-gray-700">
   {{ activePrescriptionPreview.history || 'No history recorded.' }}
  </p>
</div>

          <!-- Vitals -->
          <div class="mt-5">
            <h3 class="font-bold text-gray-900">Vitals</h3>

            <div
              v-if="prescriptionPreviewVitals.length"
              class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3"
            >
              <div
                v-for="vital in prescriptionPreviewVitals"
                :key="vital.label"
                class="rounded-xl border border-gray-200 bg-white p-4"
              >
                <p class="text-xs uppercase text-gray-500">{{ vital.label }}</p>
                <p class="mt-2 font-bold text-gray-900">{{ vital.value }}</p>
              </div>
            </div>

            <p v-else class="mt-2 text-sm text-gray-500">
              No vitals recorded for this consultation.
            </p>
          </div>

<!-- Investigations -->
<div class="mt-5">
  <h3 class="font-bold text-gray-900">Investigations Advised</h3>
  <p class="mt-2 whitespace-pre-wrap break-words text-sm text-gray-700">
   {{ activePrescriptionPreview.investigations || 'No investigations advised.' }}
  </p>
</div>

          <div class="mt-6">
            <h3 class="font-bold text-gray-900">Provisional Diagnosis</h3>
            <p class="mt-2 whitespace-pre-wrap text-sm text-gray-700">
              {{ activePrescriptionPreview.provisional_diagnosis || 'No provisional diagnosis recorded.' }}
            </p>
          </div>

          <div class="mt-5">
            <h3 class="font-bold text-gray-900">Treatment / Medication</h3>

            <div class="mt-3 overflow-x-auto">
              <table class="w-full text-left text-sm">
                <thead>
                  <tr class="border-b border-amber-200 bg-amber-100">
                    <th class="px-3 py-2">Medicine</th>
                    <th class="px-3 py-2">Dose</th>
                    <th class="px-3 py-2">Frequency</th>
                    <th class="px-3 py-2">Instructions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(medicine, index) in prescriptionMedicines"
                    :key="index"
                    class="border-b border-gray-200"
                  >
                    <td class="px-3 py-2">{{ medicine.medicine_name || medicine.medicine || '—' }}</td>
                    <td class="px-3 py-2">{{ medicine.dosage || medicine.dose || '—' }}</td>
                    <td class="px-3 py-2">{{ medicine.timing || medicine.frequency || '—' }}</td>
                    <td class="px-3 py-2">{{ medicine.instructions || medicine.duration || medicine.instruction || '—' }}</td>
                  </tr>
                  <tr v-if="!prescriptionMedicines.length">
                    <td colspan="4" class="px-3 py-4 text-gray-500">
                      No medicine details available.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="mt-5">
            <h3 class="font-bold text-gray-900">Doctor Advice</h3>
            <p class="mt-2 whitespace-pre-wrap text-sm text-gray-700">
              {{ activePrescriptionPreview.doctor_advice || activePrescriptionPreview.advice || 'No doctor advice recorded.' }}
            </p>
          </div>

          <div class="mt-5">
            <h3 class="font-bold text-gray-900">Follow-up In (days)</h3>
            <p class="mt-2 text-sm text-gray-700">
              {{ activePrescriptionPreview.follow_up_in_days || 'Not specified' }}
            </p>
          </div>

          <div class="mt-6 border-t border-amber-200 pt-5">
            <h3 class="font-bold text-gray-900">Digitally Signed</h3>
            <p class="mt-2 text-sm text-gray-600">
              This is a digitally generated CareYogi prescription and does not require a physical signature.
            </p>
            <p class="mt-2 text-sm text-gray-700">© CareYogi 2026</p>
          </div>
        </div>
      </div>

      <div class="flex shrink-0 justify-end border-t border-gray-200 bg-white px-6 py-4">
        <button
          type="button"
          class="rounded-xl bg-gray-100 px-5 py-3 font-semibold text-gray-800 hover:bg-gray-200"
          @click="showPrescriptionPreview = false"
        >
          Close
        </button>
      </div>
    </div>
      </div>

        <!-- Lab Reports -->
<div v-else-if="activeTab === 'Lab Reports'" class="space-y-3">
  <div
    v-for="document in healthVaultRecords"
    :key="document.name"
    class="rounded-xl border border-gray-200 p-4"
  >
    <p class="font-medium text-gray-900">
      {{ document.document_type || 'Health Document' }}
    </p>
    <a
      v-if="document.document_url"
      :href="document.document_url"
      target="_blank"
      rel="noopener noreferrer"
      class="mt-2 inline-block text-sm text-blue-600 hover:underline"
    >
      View document
    </a>
  </div>

  <p
    v-if="!patientHistoryResource.loading && !healthVaultRecords.length"
    class="py-8 text-center text-sm text-gray-500"
  >
    No health records found for this patient.
  </p>
</div>

        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { createResource } from 'frappe-ui';
import careyogiLogo from '@/assets/images/logo-01.png';

const route = useRoute();
const router = useRouter();
const activeTab = ref('Timeline');
const showPrescriptionPreview = ref(false);
const selectedPrescriptionPreview = ref(null);

const activePrescriptionPreview = computed(
  () => selectedPrescriptionPreview.value || prescriptionResource.data,
);


const tabs = [
  'Timeline',
  'Conditions',
  'Medications',
  'Vitals',
  'Lab Reports',
  'Prescriptions',
];


const patientResource = createResource({
  url: 'wellnest.wellnest.doctype.patient.patient.get_doctor_patient_details',
  makeParams() {
    return {
      patient: route.query.patient,
      appointment: route.query.appointment || undefined,
    };
  },
  auto: false,
});

const patient = computed(() => {
  const data = patientResource.data;

  if (!data) {
    return {
      id: '',
      name: 'Loading patient...',
      age: null,
      gender: '',
      location: '',
      risk: 'Not available',
      adherence: null,
      nextVisit: 'Not available',
      emergencyContact: 'Not available',
      emergencyRelationship: '',
      emergencyPhone: '',
      consultationReason: 'Not available',
      consultationType: 'Not available',
      consultationDate: 'Not available',
    };
  }

  const dob = data.date_of_birth
    ? new Date(`${data.date_of_birth}T00:00:00`)
    : null;

  let age = null;

  if (dob && !Number.isNaN(dob.getTime())) {
    const today = new Date();
    age = today.getFullYear() - dob.getFullYear();

    if (
      today.getMonth() < dob.getMonth() ||
      (today.getMonth() === dob.getMonth() &&
        today.getDate() < dob.getDate())
    ) {
      age -= 1;
    }
  }

  const contact = data.emergency_contacts?.[0];
  const appointment = data.appointment || {};
  const formatDateTime = (value) => {
  if (!value) return 'Not available';

  const date = new Date(value.replace(' ', 'T'));

  if (Number.isNaN(date.getTime())) return 'Not available';

  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
};

  return {
    id: data.id,
    name: data.full_name || data.id,
    age,
    gender: data.gender || 'Not available',
    location: data.address || 'Not available',
    risk: 'Not available',
    adherence: null,
    nextVisit: formatDateTime(appointment.scheduled_time),
    emergencyContact: contact?.contact_name || 'Not available',
    emergencyRelationship: contact?.relationship || '',
    emergencyPhone: contact?.phone_number || '',
    consultationReason: appointment.main_complaints || 'Not available',
    consultationType: appointment.consultation_type || 'Not available',
    consultationDate: formatDateTime(appointment.scheduled_time),
  };
});

const timelineResource = createResource({
  url: 'wellnest.wellnest.doctype.patient.patient.get_patient_timeline',
  makeParams() {
    return {
      patient: route.query.patient,
      appointment: route.query.appointment || undefined,
    };
  },
  auto: false,
});

const patientHistoryResource = createResource({
  url: 'wellnest.api.patient_history.get_patient_history',
  auto: false,
});

const healthVaultRecords = computed(
  () => patientHistoryResource.data?.health_vault || [],
);

const prescriptionResource = createResource({
  url: 'wellnest.api.prescription.get_consultation_prescription',
  makeParams() {
    return {
      appointment: route.query.appointment,
    };
  },
  auto: false,
});

const consultationHistoryResource = createResource({
  url: 'wellnest.api.patient_history.get_patient_consultation_history',
  makeParams() {
    return {
      patient: route.query.patient,
    };
  },
  auto: false,
});

const consultationHistory = computed(
  () => consultationHistoryResource.data || [],
);

const historicalPrescriptions = computed(() =>
  consultationHistory.value.flatMap((consultation) =>
    (consultation.prescriptions || []).map((prescription) => ({
      ...prescription,
      scheduled_time: consultation.scheduled_time,
      main_complaints: consultation.main_complaints,
    })),
  ),
);

const historicalMedicines = computed(() =>
  historicalPrescriptions.value.flatMap((prescription) =>
    (prescription.medicines || []).map((medicine) => ({
      ...medicine,
      prescription_name: prescription.name,
      patient_appointment: prescription.patient_appointment,
      consultation_date:
        prescription.scheduled_time ||
        prescription.prescription_date ||
        prescription.creation,
      main_complaints: prescription.main_complaints,
    })),
  ),
);

const prescriptionPreviewDetails = computed(() => {
  const appointment = patientResource.data?.appointment || {};

  return [
    { label: 'Patient', value: patient.value.name },
    {
      label: 'Consultation Type',
      value: appointment.consultation_type || patient.value.consultationType,
    },
    {
      label: 'Date',
      value: patient.value.consultationDate,
    },
    {
      label: 'Appointment ID',
      value: route.query.appointment || 'Not available',
    },
  ];
});

const prescriptionPreviewDoctorDetails = computed(() => {
  const appointment = patientResource.data?.appointment || {};

  return [
    {
  label: 'Consulting Doctor',
  value: appointment.practitioner || 'Not Available',
  description: '',
    },
    {
      label: 'Qualification',
      value: 'MBBS, MD (Internal Medicine)',
      description: '34 Years Experience',
    },
    {
      label: 'Registration',
      value: appointment.registration_no || 'Not Available',
      description: 'Digitally signed draft',
    },
  ];
});

const prescriptionPreviewVitals = computed(() => {
  const readings =
    prescriptionPreviewVitalsResource.data?.vital_reading || [];

  const labels = {
    Weight: 'Weight',
    Height: 'Height',
    'Heart Rate': 'Pulse',
    BP: 'BP',
    SPO2: 'SpO2',
    Temperature: 'Temperature',
    Sugar: 'Blood Sugar',
    'Respiratory Rate': 'Respiratory Rate',
  };

  return readings.map((reading) => ({
    label: labels[reading.vital_type] || reading.vital_type || 'Vital',
    value: [reading.value, reading.unit].filter(Boolean).join(' ') || '—',
  }));
});

const prescriptionMedicines = computed(() => {
  const prescription = activePrescriptionPreview.value;
  if (!prescription) return [];

  const medicines =
    prescription.medicines ||
    prescription.prescription_items ||
    [];

  if (Array.isArray(medicines)) return medicines;

  if (typeof medicines === 'string') {
    try {
      const parsed = JSON.parse(medicines);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  return [];
});

const prescriptionChiefComplaints = computed(() => {
  const complaints = prescriptionResource.data?.chief_complaints || [];

  if (Array.isArray(complaints)) {
    return complaints;
  }

  if (typeof complaints === 'string') {
    try {
      const parsed = JSON.parse(complaints);
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      console.error('Failed to parse chief complaints:', error);
      return [];
    }
  }

  return [];
});

const vitalsResource = createResource({
  url: 'wellnest.wellnest.doctype.vitals.vitals.get_consultation_vitals',
  auto: false,
});

const prescriptionPreviewVitalsResource = createResource({
  url: 'wellnest.wellnest.doctype.vitals.vitals.get_consultation_vitals',
  auto: false,
});


watch(
  () => [route.query.patient, route.query.appointment],
  async ([patientId]) => {
    if (!patientId) {
      patientResource.reset();
      timelineResource.reset();
      prescriptionResource.reset();
      vitalsResource.reset();
      patientHistoryResource.reset();
      consultationHistoryResource.reset();
      return;
    }

    patientResource.reload();
    timelineResource.reload();
    prescriptionResource.reload();
    consultationHistoryResource.reload();

    if (route.query.appointment) {
  patientHistoryResource.submit({
    patient_appointment: route.query.appointment,
  });
} else {
  patientHistoryResource.reset();
}

    if (route.query.appointment) {
  await vitalsResource.submit({
    appointment: route.query.appointment,
  });
} else {
  vitalsResource.reset();
}
  },
  { immediate: true },
);



const timeline = computed(() => {
  const data = timelineResource.data || {};
  const appointmentCards = [];
  const linkedAppointmentIds = new Set();

  for (const consultation of consultationHistory.value) {
    const appointmentId = consultation.patient_appointment;

    const prescriptions = consultation.prescriptions || [];

    if (appointmentId) {
      linkedAppointmentIds.add(appointmentId);
    }

    if (consultation.scheduled_time || prescriptions.length) {
      appointmentCards.push({
        type: 'appointment',
        id: appointmentId || `consultation-${consultation.scheduled_time}`,
        appointmentId,
        scheduledTime: consultation.scheduled_time,
        mainComplaints: consultation.main_complaints,
        prescriptions: prescriptions.map((prescription) => ({
          ...prescription,
          completionDate:
            ['Complete', 'Confirmed'].includes(prescription.workflow_state)
              ? prescription.modified || prescription.creation
              : null,
        })),
        sortDate:
          consultation.scheduled_time ||
          prescriptions[0]?.modified ||
          prescriptions[0]?.creation,
      });
    }
  }

  const appointment = patientResource.data?.appointment;

  if (
    appointment?.name &&
    !linkedAppointmentIds.has(appointment.name)
  ) {
    appointmentCards.push({
      type: 'appointment',
      id: appointment.name,
      appointmentId: appointment.name,
      scheduledTime: appointment.scheduled_time,
      mainComplaints: appointment.main_complaints,
      prescriptions: [],
      sortDate: appointment.scheduled_time,
    });
  }

  const otherEvents = [];

  for (const condition of data.medical_history || []) {
    if (condition.onset_date || condition.condition_name) {
      otherEvents.push({
        type: 'event',
        id: `condition-${condition.name || condition.condition_name}`,
        date: condition.onset_date,
        title: condition.condition_name || 'Medical history recorded',
        description: condition.notes || condition.status || 'Medical history entry.',
      });
    }
  }

  for (const medication of data.medications || []) {
    if (medication.creation) {
      otherEvents.push({
        type: 'event',
        id: `medication-${medication.name}`,
        date: medication.creation,
        title: 'Medication record',
        description:
          medication.notes ||
          medication.adherence_status ||
          'Medication information recorded.',
      });
    }
  }

  for (const visit of data.nurse_visits || []) {
    if (visit.visit_date) {
      otherEvents.push({
        type: 'event',
        id: `nurse-${visit.name || visit.visit_date}`,
        date: visit.visit_date,
        title: 'Nurse visit',
        description:
          visit.concerns || visit.vitals_summary || 'Nurse visit recorded.',
      });
    }
  }

  for (const review of data.reviews || []) {
    if (review.review_date) {
      otherEvents.push({
        type: 'event',
        id: `review-${review.name || review.review_date}`,
        date: review.review_date,
        title: 'Geriatric review',
        description:
          review.summary || review.recommendations || 'Review recorded.',
      });
    }
  }

  const currentPrescription = prescriptionResource.data;

  if (
    currentPrescription &&
    !historicalPrescriptions.value.some(
      (item) => item.name === currentPrescription.name,
    )
  ) {
    const linkedId = currentPrescription.patient_appointment;
    const linkedCard = appointmentCards.find(
      (card) => card.appointmentId === linkedId,
    );

    if (linkedCard) {
      linkedCard.prescriptions.push({
        ...currentPrescription,
        completionDate:
          ['Complete', 'Confirmed'].includes(currentPrescription.workflow_state)
            ? currentPrescription.modified || currentPrescription.creation
            : null,
      });
    } else {
      otherEvents.push({
        type: 'event',
        id: `prescription-${currentPrescription.name}`,
        date: currentPrescription.modified || currentPrescription.creation,
        title:
          currentPrescription.workflow_state === 'Draft'
            ? 'Draft saved'
            : 'Prescription',
        description: currentPrescription.workflow_state || 'Prescription recorded.',
      });
    }
  }

  return [
    ...appointmentCards.map((card) => ({
      ...card,
      sortDate: card.sortDate || card.scheduledTime,
    })),
    ...otherEvents.map((event) => ({
      ...event,
      sortDate: event.date,
    })),
  ]
    .filter((item) => item.sortDate)
    .sort((a, b) => new Date(b.sortDate) - new Date(a.sortDate));
});


function formatTimelineDate(value) {
  const date = new Date(String(value).replace(' ', 'T'));

  if (Number.isNaN(date.getTime())) {
    return '';
  }

  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

async function openPrescriptionPreview(prescription) {
  selectedPrescriptionPreview.value = prescription;
  showPrescriptionPreview.value = true;

  prescriptionPreviewVitalsResource.reset();

  const appointmentId = prescription?.patient_appointment;

  if (!appointmentId) return;

  await prescriptionPreviewVitalsResource.submit({
    appointment: appointmentId,
  });
}

function returnToSelectedConsult() {
  const appointmentId = route.query.appointment;

  if (!appointmentId) return;

  router.push({
    name: 'ConsultationDetails',
    params: {
      bookingId: appointmentId,
    },
    query: {
      status: 'All',
    },
  });
}

function messagePatient() {
  router.push({
    name: 'Messages',
    query: {
      patient: route.query.patient,
    },
  });
}

function initials(name) {
  return String(name || 'P')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();
}
</script>