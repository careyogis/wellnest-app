consultations. page
<template>
  <div class="p-6 md:p-8">
    <!-- Page Header -->
    <div class="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Consultations</h1>
        <p class="text-gray-500 mt-1">Each booked row opens its own patient-specific prescription workspace, whether the doctor writes digitally or validates an uploaded paper prescription.</p>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
      <div v-for="card in summaryCards" :key="card.title" class="bg-white border border-gray-200 rounded-2xl p-5">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500">{{ card.title }}</p>

            <p class="text-3xl font-bold text-gray-900 mt-4" :class="{ 'text-2xl': card.value.length > 8 }">
              {{ card.value }}
            </p>

            <p class="text-sm text-gray-500 mt-2">
              {{ card.description }}
            </p>
          </div>

          <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <FeatherIcon :name="card.icon" class="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,2fr)_380px] gap-6 items-start">
      <!-- Waiting Room / Upcoming -->
      <section class="bg-white border border-gray-200 rounded-2xl overflow-y-auto overflow-x-hidden max-h-[600px]">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-6 py-5 border-b border-gray-200">
          <div>
            <h2 class="text-xl font-bold text-gray-900">Consultations</h2>
            <p class="text-sm text-gray-500 mt-1">View and manage your patient consultations.</p>
          </div>

          <div class="flex items-center gap-3">
            <select v-model="statusFilter" class="px-3 py-2 rounded-lg border border-gray-300 bg-white text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-amber-200">
              <option value="All">All</option>
              <option value="Upcoming">Upcoming</option>
              <option value="Completed">Completed</option>
              <option value="Payment Pending">Payment Pending</option>
            </select>

            <button type="button" class="text-sm font-semibold text-amber-600 hover:underline whitespace-nowrap" @click="router.push({ name: 'Schedule' })">Manage slots</button>
          </div>
        </div>
        <div class="w-full overflow-x-auto">
          <div class="min-w-full">
            <!-- Desktop table header -->
            <div class="hidden lg:grid w-max min-w-full grid-cols-[140px_150px_100px_150px_300px] gap-4 px-6 py-3 bg-gray-50 text-xs font-semibold text-gray-500 uppercase tracking-wide">
              <div>Time</div>
              <div>Patient</div>
              <div>Mode</div>
              <div>Reason</div>

              <div>Actions</div>
            </div>

            <!-- Consultation rows -->
            <div
              v-for="consultation in filteredConsultations"
              :key="consultation.id"
              class="w-max min-w-full border-t border-gray-100 transition-colors"
              :class="{
                'bg-amber-50/60': selectedConsultation?.id === consultation.id,
              }"
            >
              <div class="w-full min-w-0 grid grid-cols-1 lg:grid-cols-[140px_150px_100px_150px_300px] gap-4 px-6 py-5 items-center">
                <!-- Time -->
                <div class="text-sm font-semibold text-gray-900">
                  {{ consultation.time }}
                </div>

                <!-- Patient -->
                <div>
                  <p class="font-bold text-gray-900 truncate max-w-[180px]" :title="consultation.patient">
                    {{ consultation.patient }}
                  </p>

                  <p class="text-sm text-gray-500">
                    {{ consultation.bookingStatus }}
                  </p>
                </div>

                <!-- Mode -->
                <div class="text-sm text-gray-700">
                  {{ consultation.mode }}
                </div>

                <!-- Reason -->
                <div class="text-sm text-gray-700">
                  {{ consultation.reason }}
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-3 whitespace-nowrap min-w-max">
                  <template v-if="consultation.bookingStatus === 'Completed'">
                    <button
                      type="button"
                      class="px-3 py-2 rounded-lg border border-amber-400 text-amber-700 text-sm font-semibold bg-white hover:bg-amber-50 transition-colors"
                      @click="openPrescription(consultation)"
                    >
                      Open Prescription
                    </button>

                    <span class="inline-flex items-center px-3 py-2 rounded-lg bg-emerald-100 text-emerald-700 text-sm font-semibold"> Completed </span>
                  </template>

                  <template v-else-if="consultation.paymentStatus !== 'Paid'">
                    <span class="inline-flex items-center px-3 py-2 rounded-lg bg-amber-100 text-amber-700 text-sm font-semibold"> Payment Pending </span>
                  </template>

                  <template v-else-if="consultation.bookingStatus === 'In-Progress'">
                    <button
                      type="button"
                      class="px-3 py-2 rounded-lg border border-amber-400 text-amber-700 text-sm font-semibold bg-white hover:bg-amber-50 transition-colors"
                      @click="openPrescription(consultation)"
                    >
                      Open Prescription
                    </button>

                    <button type="button" class="px-4 py-2 rounded-lg bg-teal-600 text-white text-sm font-semibold hover:bg-teal-700 transition" @click="joinConsultation(consultation)">
                      Continue
                    </button>
                  </template>

                  <template v-else>
                    <button type="button" class="px-4 py-2 rounded-lg bg-teal-600 text-white text-sm font-semibold hover:bg-teal-700 transition" @click="joinConsultation(consultation)">
                      Start Call
                    </button>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Template Preview -->
      <aside v-if="showPatientDetails" class="bg-white border border-gray-200 rounded-2xl overflow-y-auto max-h-[600px]">
        <div class="flex items-center justify-between px-5 py-5 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-900">Template preview</h2>

          <button type="button" class="px-3 py-2 rounded-lg border border-amber-400 text-amber-700 text-sm font-semibold hover:bg-amber-50" @click="consultationRef?.previewTemplate()">
            Open full preview
          </button>
        </div>

        <div class="p-5">
          <!-- Doctor details -->

          <div class="grid grid-cols-3 gap-3">
            <div v-for="doctor in consultationRef?.doctorDetails || []" :key="doctor.label" class="border border-gray-200 rounded-xl p-4">
              <p class="text-xs text-gray-500">
                {{ doctor.label }}
              </p>

              <p class="font-bold text-gray-900 mt-2">
                {{ doctor.value }}
              </p>

              <p v-if="doctor.description" class="text-xs text-gray-500 mt-2">
                {{ doctor.description }}
              </p>
            </div>
          </div>

          <!-- Selected patient -->
          <div class="mt-6">
            <p class="text-xs text-gray-500">Selected patient</p>

            <p class="text-3xl font-bold text-gray-900 mt-1">
              {{ selectedConsultation.patient }}
            </p>

            <p class="text-sm text-gray-500">
              {{ selectedConsultation.mode }} consult /
              {{ selectedConsultation.time }}
            </p>
          </div>

          <!-- Chief Complaints -->
          <div class="mt-6">
            <h3 class="text-lg font-bold text-gray-900">Chief Complaints (with duration)</h3>

            <ul class="list-disc pl-5 mt-2 space-y-1 text-sm text-gray-700">
              <li v-for="complaint in consultationRef?.complaints || []" :key="complaint.id">
                {{ complaint.text }}
                <span v-if="complaint.duration"> ({{ complaint.duration }}) </span>
              </li>

              <li v-if="!(consultationRef?.complaints || []).length" class="list-none text-gray-500">No complaints entered.</li>
            </ul>
          </div>

          <!-- History -->
          <div class="mt-6">
            <h3 class="text-lg font-bold text-gray-900">History (brief)</h3>

            <p class="text-sm text-gray-700 mt-2 leading-6">
              {{ consultationRef?.history || 'No history entered.' }}
            </p>
          </div>

          <!-- Vitals -->
          <div class="mt-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900">Vitals</h3>

              <span class="text-xs text-gray-500"> Optional </span>
            </div>

            <div class="grid grid-cols-2 gap-3 mt-3">
              <div v-for="vital in (consultationRef?.vitals || []).filter((item) => item.value)" :key="vital.label" class="border border-gray-200 rounded-xl p-3">
                <p class="text-xs text-gray-500">
                  {{ vital.label }}
                </p>

                <p class="font-bold text-gray-900 mt-1">
                  {{ vital.value }}
                  <span v-if="vital.unit">
                    {{ vital.unit }}
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
    <!-- Full consultation workspace -->
    <section class="mt-4">
      <Consultation ref="consultationRef" :selected-consultation="selectedConsultation" />
    </section>

    <!-- Join consultation modal -->
    <div v-if="showJoinModal" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="closeJoinModal">
      <div class="w-full max-w-3xl h-[88vh] bg-white rounded-xl shadow-xl overflow-hidden flex flex-col">
        <!-- Modal header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 class="text-2xl font-bold text-gray-900">Join consultation</h2>

          <button type="button" class="text-gray-500 hover:text-gray-900 text-2xl" @click="closeJoinModal">×</button>
        </div>

        <!-- Waiting room -->
        <div class="p-5">
          <div class="rounded-2xl min-h-[420px] bg-gradient-to-br from-teal-500 to-teal-700 text-white p-7 flex flex-col">
            <!-- Patient details -->
            <div>
              <span class="inline-flex px-3 py-1 rounded-lg bg-white/90 text-gray-800 text-xs font-semibold"> Waiting room </span>

              <h2 class="text-4xl font-bold mt-4">
                {{ selectedConsultation.patient }}
              </h2>

              <p class="text-lg mt-2">
                {{ selectedConsultation.reason }}
              </p>

              <p class="mt-4 text-base">
                {{ selectedConsultation.mode }} consult /
                {{ selectedConsultation.time }}
              </p>
            </div>

            <!-- Controls -->
            <div class="flex-1 flex items-end justify-center gap-3">
              <button type="button" class="w-12 h-12 rounded-xl border border-white/40 bg-white/10 flex items-center justify-center">
                <FeatherIcon name="mic" class="w-5 h-5" />
              </button>

              <button type="button" class="w-12 h-12 rounded-xl border border-white/40 bg-white/10 flex items-center justify-center">
                <FeatherIcon name="video" class="w-5 h-5" />
              </button>

              <button type="button" class="w-12 h-12 rounded-xl border border-white/40 bg-white/10 flex items-center justify-center">
                <FeatherIcon name="monitor" class="w-5 h-5" />
              </button>

              <button type="button" class="ml-3 px-5 py-3 rounded-xl bg-red-500 text-white font-semibold hover:bg-red-600" @click="closeJoinModal">End consultation</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed, ref, watch } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';
import { useRouter } from 'vue-router';
import Consultation from './Consultation.vue';
import logoUrl from '@/assets/images/logo-01.png';

const router = useRouter();

const consultationsResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.get_teleconsultation_appointments',
  auto: true,
});

const startConsultationResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.start_consultation',
});

function formatAppointmentTime(value) {
  if (!value) return '';

  const [datePart, timePart] = value.split(' ');

  if (!datePart || !timePart) {
    return value;
  }

  const [year, month, day] = datePart.split('-');
  const [hours, minutes] = timePart.split(':');

  const date = new Date(Number(year), Number(month) - 1, Number(day), Number(hours), Number(minutes));

  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

const consultations = computed(() => {
  return (consultationsResource.data || []).map((appointment) => ({
    id: appointment.name,
    time: formatAppointmentTime(appointment.scheduled_time),
    patient: appointment.patient_name || appointment.patient,
    practitioner: appointment.practitioner,
    bookingStatus: appointment.status,
    paymentStatus: appointment.payment_status,
    mode: 'Video',
    reason: 'Teleconsultation',
    workflow: 'Clinical consultation',
    appointment: appointment.name,
  }));
});

const statusFilter = ref('Upcoming');

const filteredConsultations = computed(() => {
  if (statusFilter.value === 'All') {
    return consultations.value;
  }

  if (statusFilter.value === 'Upcoming') {
    return consultations.value.filter((consultation) => consultation.bookingStatus !== 'Completed' && consultation.paymentStatus === 'Paid');
  }

  if (statusFilter.value === 'Completed') {
    return consultations.value.filter((consultation) => consultation.bookingStatus === 'Completed');
  }

  if (statusFilter.value === 'Payment Pending') {
    return consultations.value.filter((consultation) => consultation.paymentStatus !== 'Paid');
  }

  return consultations.value;
});

const consultationRef = ref(null);

const selectedConsultation = ref({
  id: null,
  time: '',
  patient: '',
  practitioner: '',
  bookingStatus: '',
  mode: 'Video',
  reason: 'Teleconsultation',
  workflow: 'Clinical consultation',
  appointment: null,
});
const showPatientDetails = ref(false);

// const selectedConsultation = ref(consultations.value[0])

const showJoinModal = ref(false);
const showTemplatePreview = ref(false);

const summaryCards = computed(() => [
  {
    title: 'Digital drafts',
    value: '0',
    description: 'Written during or after consultation',
    icon: 'edit-3',
  },
  {
    title: 'In review',
    value: '0',
    description: 'Paper uploads being processed asynchronously',
    icon: 'loader',
  },
  {
    title: 'Ready for validation',
    value: '0',
    description: 'OCR output awaiting doctor confirmation',
    icon: 'check-square',
  },
  {
    title: 'Selected patient',
    value: selectedConsultation.value.patient,
    description: `${selectedConsultation.value.mode} consult at ${selectedConsultation.value.time}`,
    icon: 'user',
  },
]);

const vitals = [
  { label: 'Weight', value: '74 kg' },
  { label: 'Height', value: '162 cm' },
  { label: 'Pulse', value: '76 /min' },
  { label: 'BP', value: '128/78 mmHg' },
  { label: 'SpO2', value: '98%' },
  { label: 'Temperature', value: '98.4 F' },
];

function workflowClass(workflow) {
  if (workflow === 'Ready for validation') {
    return 'bg-cyan-100 text-cyan-700';
  }

  if (workflow === 'In review') {
    return 'bg-amber-100 text-amber-700';
  }

  return 'bg-emerald-100 text-emerald-700';
}

function openPrescription(consultation) {
  selectedConsultation.value = consultation;
  showPatientDetails.value = true;
}
async function joinConsultation(consultation) {
  try {
    const response = await startConsultationResource.submit({
      appointment: consultation.id,
    });

    router.push({
      name: 'ConsultationRoom',
      params: {
        bookingId: consultation.id,
      },
      query: {
        channelName: response.channel_name,
        uid: response.uid,
        rtcToken: response.rtcToken,
        appId: response.appId,
      },
    });
  } catch (error) {
    console.error('Failed to start consultation:', error);
  }
}

function closeJoinModal() {
  showJoinModal.value = false;
}
</script>
