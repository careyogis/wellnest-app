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

          <div v-if="activeTab === 'Timeline'" class="space-y-6">
            <div
              v-for="(item, index) in timeline"
              :key="index"
              class="relative border-l-2 border-gray-200 pb-1 pl-5"
            >
              <span class="absolute -left-[7px] top-1 h-3 w-3 rounded-full border-2 border-white bg-amber-400"></span>
              <p class="font-semibold">{{ item.title }}</p>
              <p class="mt-1 text-sm text-gray-500">{{ item.description }}</p>
            </div>
          </div>

          
      <!-- Conditions -->
<div v-else-if="activeTab === 'Conditions'" class="space-y-3">
  <div class="rounded-lg border border-gray-200 bg-white p-4">
    <h3 class="font-semibold text-gray-900">History</h3>

    <p class="mt-2 whitespace-pre-wrap text-sm text-gray-600">
      {{ prescriptionResource.data?.history || 'No history recorded for this appointment.' }}
    </p>
  </div>
</div>

        <!-- Medications -->
         <div v-else-if="activeTab === 'Medications'" class="space-y-3">
            <div
            v-for="(medicine, index) in prescriptionResource.data?.medicines || []"
            :key="index"
            class="rounded-lg border p-4"
            >
             <p class="font-semibold">
             {{ medicine.medicine_name || 'Medicine' }}
             </p>

             <div class="mt-2 grid grid-cols-1 gap-2 text-sm text-gray-600 sm:grid-cols-2">
             <p><strong>Dose:</strong> {{ medicine.dosage || 'Not specified' }}</p>
            <p><strong>Frequency:</strong> {{ medicine.timing || 'Not specified' }}</p>
             <p class="sm:col-span-2">
             <strong>Instructions:</strong>
        {{ medicine.instructions || 'Not specified' }}
      </p>
    </div>
  </div>

  <p
    v-if="!prescriptionResource.data?.medicines?.length"
    class="text-sm text-gray-500"
  >
    No medications found for this appointment.
  </p>
</div>


          
<!-- Vitals -->
<div v-else-if="activeTab === 'Vitals'" class="space-y-3">
  <div
    v-if="vitalsResource.data?.vital_reading?.length"
    class="grid grid-cols-1 gap-3 sm:grid-cols-2"
  >
    <div
      v-for="(reading, index) in vitalsResource.data.vital_reading"
      :key="index"
      class="rounded-lg border p-4"
    >
      <p class="text-sm text-gray-500">
        {{ reading.vital_type || 'Vital' }}
      </p>
      <p class="mt-1 text-lg font-semibold text-gray-900">
        {{ reading.value ?? '—' }}
      </p>
    </div>
  </div>

  <p v-else class="text-sm text-gray-500">
    No vitals recorded for this appointment.
  </p>
</div>
        

<!-- Prescriptions -->
<div v-else-if="activeTab === 'Prescriptions'" class="space-y-3">
  <div
    v-if="prescriptionResource.data"
    class="rounded-xl border border-gray-200 bg-white p-5"
  >
    <div class="flex items-center justify-between gap-4">
     

      <button
        type="button"
        class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600"
        @click="showPrescriptionPreview = true"
      >
        Preview prescription
      </button>
    </div>
  </div>

  <p v-else class="text-sm text-gray-500">
    No prescription found for this appointment.
  </p>

  <!-- Prescription Preview Modal -->
  <div
    v-if="showPrescriptionPreview && prescriptionResource.data"
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
              {{ prescriptionResource.data.workflow_state || 'Prescription' }}
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

          <div class="mt-6">
            <h3 class="font-bold text-gray-900">Provisional Diagnosis</h3>
            <p class="mt-2 whitespace-pre-wrap text-sm text-gray-700">
              {{ prescriptionResource.data.provisional_diagnosis || 'No provisional diagnosis recorded.' }}
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
              {{ prescriptionResource.data.doctor_advice || prescriptionResource.data.advice || 'No doctor advice recorded.' }}
            </p>
          </div>

          <div class="mt-5">
            <h3 class="font-bold text-gray-900">Follow-up In (days)</h3>
            <p class="mt-2 text-sm text-gray-700">
              {{ prescriptionResource.data.follow_up_in_days || 'Not specified' }}
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

<!-- Fallback for other tabs -->
<p v-else class="text-sm text-gray-500">
  {{ activeTab }} content will be added in a future implementation.
</p>

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

const prescriptionMedicines = computed(() => {
  const prescription = prescriptionResource.data;
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

const vitalsResource = createResource({
  url: 'wellnest.wellnest.doctype.vitals.vitals.get_consultation_vitals',
  auto: false,
});


watch(
  () => [route.query.patient, route.query.appointment],
  ([patientId]) => {
    if (!patientId) {
      patientResource.reset();
      timelineResource.reset();
      prescriptionResource.reset();
      vitalsResource.reset();
      patientHistoryResource.reset();
      return;
    }

    patientResource.reload();
    timelineResource.reload();
    prescriptionResource.reload();

    if (route.query.appointment) {
  patientHistoryResource.submit({
    patient_appointment: route.query.appointment,
  });
} else {
  patientHistoryResource.reset();
}

    if (route.query.appointment) {
      vitalsResource.submit({
        appointment: route.query.appointment,
      });
    }
  },
  { immediate: true },
);

const timeline = computed(() => {
  const data = timelineResource.data || {};

  const events = [];



const appointment = patientResource.data?.appointment;

if (appointment?.scheduled_time) {
  events.push({
    date: appointment.scheduled_time,
    title: 'Appointment scheduled',
    description: appointment.main_complaints
      ? `Consultation reason: ${appointment.main_complaints}`
      : patient.consultationReason !== 'Not available'
        ? `Consultation reason: ${patient.consultationReason}`
        : 'Appointment scheduled.',
  });
}

  const prescription = prescriptionResource.data;

  if (prescription?.creation) {
  events.push({
    date: prescription.creation,
    title: 'Draft saved',
    description: 'Doctor saved the prescription as a draft.',
  });
}

if (prescription?.workflow_state === 'Draft') {
  events.push({
    date: prescription.modified || prescription.creation || new Date().toISOString(),
    title: 'Draft saved',
    description: 'Doctor saved the prescription as a draft.',
  });
}

if (
  prescription &&
  ['Complete', 'Confirmed'].includes(prescription.workflow_state)
) {
  events.push({
    date: prescription.modified || prescription.creation || new Date().toISOString(),
    title: 'Prescription reviewed and shared',
    description: 'Doctor completed the prescription workflow.',
  });
}

  for (const condition of data.medical_history || []) {
    if (condition.onset_date || condition.condition_name) {
      events.push({
        date: condition.onset_date,
        title: condition.condition_name || 'Medical history recorded',
        description: condition.notes || condition.status || 'Medical history entry.',
      });
    }
  }

  for (const medication of data.medications || []) {
    if (medication.creation) {
      events.push({
        date: medication.creation,
        title: 'Medication record',
        description: medication.notes || medication.adherence_status || 'Medication information recorded.',
      });
    }
  }

  for (const visit of data.nurse_visits || []) {
    if (visit.visit_date) {
      events.push({
        date: visit.visit_date,
        title: 'Nurse visit',
        description: visit.concerns || visit.vitals_summary || 'Nurse visit recorded.',
      });
    }
  }

  for (const review of data.reviews || []) {
    if (review.review_date) {
      events.push({
        date: review.review_date,
        title: 'Geriatric review',
        description: review.summary || review.recommendations || 'Review recorded.',
      });
    }
  }

  
return events
  .filter((event) => event.date)
  .sort((a, b) => {
    if (a.title === 'Appointment scheduled') return -1;
    if (b.title === 'Appointment scheduled') return 1;
    return new Date(b.date) - new Date(a.date);
  })
  .map((event) => ({
    ...event,
    title: `${formatTimelineDate(event.date)} — ${event.title}`,
  }));

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