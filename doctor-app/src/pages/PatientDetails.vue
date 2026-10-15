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
        <button class="rounded-lg border border-amber-400 px-4 py-2 text-sm font-semibold text-amber-700">
          Message
        </button>
        <button class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white">
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
            <div
              v-for="(condition, index) in timelineResource.data?.medical_history || []"
              :key="index"
              class="rounded-lg border p-3"
            >
              <p class="font-semibold">{{ condition.condition_name || 'Condition recorded' }}</p>
              <p class="mt-1 text-sm text-gray-500">
                {{ condition.notes || condition.status || 'No additional details' }}
              </p>
              <p class="mt-1 text-xs text-gray-400">{{ condition.onset_date || '' }}</p>
            </div>
            <p v-if="!timelineResource.data?.medical_history?.length" class="text-sm text-gray-500">
              No conditions recorded.
            </p>
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
              class="rounded-lg border p-3"
            >
              <p class="font-semibold">{{ prescriptionResource.data.name }}</p>
              <p class="mt-1 text-sm text-gray-500">
                Status: {{ prescriptionResource.data.workflow_state || 'Not available' }}
              </p>
              <p class="mt-1 text-sm text-gray-500">
                {{ prescriptionResource.data.provisional_diagnosis || 'No diagnosis recorded' }}
              </p>
            </div>
            <p v-else class="text-sm text-gray-500">
              No prescription found for this appointment.
            </p>
          </div>

          <!-- Other tabs remain out of scope -->
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

const route = useRoute();
const router = useRouter();
const activeTab = ref('Timeline');

const tabs = [
  'Timeline',
  'Conditions',
  'Medications',
  'Vitals',
  'Lab Reports',
  'Prescriptions',
  'Notes',
  'Care Plans',
  'Files',
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


const prescriptionResource = createResource({
  url: 'wellnest.api.prescription.get_consultation_prescription',
  makeParams() {
    return {
      appointment: route.query.appointment,
    };
  },
  auto: false,
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
      return;
    }

    patientResource.reload();
    timelineResource.reload();
    prescriptionResource.reload();

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