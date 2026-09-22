<template>
  <div class="p-4 md:p-6 lg:p-8">
    <!-- Page Header -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Consultations</h1>
        <p class="text-gray-500 mt-1">Select a consultation to open the patient workspace.</p>
      </div>
    </div>

    <!-- Blade workspace -->
    <div class="grid grid-cols-1 xl:grid-cols-[360px_minmax(0,1fr)] gap-4 xl:gap-6 items-stretch min-h-[calc(100vh-180px)]">
      <!-- LEFT: CONSULTATION LIST -->
      <aside class="bg-white border border-gray-200 rounded-2xl overflow-hidden xl:sticky xl:top-4 h-full">
        <!-- List header -->
        <div class="px-5 py-5 border-b border-gray-200">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-gray-900">Consultations</h2>
              <p class="text-sm text-gray-500 mt-1">{{ filteredConsultations.length }} consultation<span v-if="filteredConsultations.length !== 1">s</span></p>
            </div>

            <button type="button" class="text-sm font-semibold text-amber-600 hover:underline" @click="router.push({ name: 'Schedule' })">Manage slots</button>
          </div>

          <!-- Filter -->
          <div class="mt-4">
            <select v-model="statusFilter" class="w-full px-3 py-2.5 rounded-xl border border-gray-300 bg-white text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-amber-200">
              <option value="All">All consultations</option>
              <option value="Upcoming">Upcoming</option>
              <option value="Completed">Completed</option>
              <option value="Payment Pending">Payment Pending</option>
            </select>
          </div>
        </div>

        <!-- Consultation list -->
        <div class="flex-1 min-h-0 overflow-y-auto">
          <div v-if="!filteredConsultations.length" class="px-5 py-10 text-center">
            <div class="mx-auto w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center text-gray-500">
              <FeatherIcon name="calendar" class="w-5 h-5" />
            </div>

            <p class="mt-4 text-sm font-semibold text-gray-900">No consultations found</p>

            <p class="mt-1 text-sm text-gray-500">Try changing the filter.</p>
          </div>

          <button
            v-for="consultation in filteredConsultations"
            :key="consultation.id"
            type="button"
            class="w-full text-left px-5 py-4 border-b border-gray-100 transition-colors hover:bg-gray-50"
            :class="{
              'bg-amber-50 border-l-4 border-l-amber-500': selectedConsultation?.id === consultation.id,
              'border-l-4 border-l-transparent': selectedConsultation?.id !== consultation.id,
            }"
            @click="selectConsultation(consultation)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="font-bold text-gray-900 truncate">
                  {{ consultation.patient }}
                </p>

                <p class="text-sm text-gray-600 mt-1">
                  {{ consultation.time }}
                </p>
              </div>

              <span class="shrink-0 inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold" :class="statusClass(consultation)">
                {{ consultation.bookingStatus }}
              </span>
            </div>

            <div class="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1">
              <span class="inline-flex items-center gap-1.5 text-xs text-gray-500">
                <FeatherIcon name="video" class="w-3.5 h-3.5" />
                {{ consultation.mode }}
              </span>

              <span class="text-gray-300">•</span>

              <span class="text-xs text-gray-500 truncate">
                {{ consultation.reason }}
              </span>
            </div>

            <div v-if="consultation.prescriptionWorkflowState" class="mt-3">
              <span class="inline-flex items-center px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 text-xs font-medium">
                {{ consultation.prescriptionWorkflowState }}
              </span>
            </div>
          </button>
        </div>
      </aside>

      <!-- RIGHT: SELECTED CONSULTATION WORKSPACE -->
      <main v-if="selectedConsultation?.id" class="min-w-0">
        <!-- Consultation header -->
        <section class="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <!-- Patient / appointment information -->
          <div class="p-5 md:p-6 border-b border-gray-200">
            <div class="flex flex-col 2xl:flex-row 2xl:items-start 2xl:justify-between gap-5">
              <!-- Patient information -->
              <div class="min-w-0">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                    <FeatherIcon name="user" class="w-6 h-6" />
                  </div>

                  <div class="min-w-0">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-400">Patient</p>

                    <h2 class="text-2xl md:text-3xl font-bold text-gray-900 truncate">
                      {{ selectedConsultation.patient }}
                    </h2>
                  </div>
                </div>

                <!-- Appointment metadata -->
                <div class="mt-5 flex flex-wrap gap-3">
                  <div class="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                    <FeatherIcon name="calendar" class="w-4 h-4 text-gray-500" />

                    <span class="text-sm text-gray-700">
                      {{ selectedConsultation.time }}
                    </span>
                  </div>

                  <div class="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 border border-gray-200">
                    <FeatherIcon name="video" class="w-4 h-4 text-gray-500" />

                    <span class="text-sm text-gray-700">
                      {{ selectedConsultation.mode }}
                    </span>
                  </div>

                  <span class="inline-flex items-center px-3 py-2 rounded-lg text-sm font-semibold" :class="statusClass(selectedConsultation)">
                    {{ selectedConsultation.bookingStatus }}
                  </span>
                </div>
              </div>

              <!-- Action buttons -->
              <div class="flex flex-wrap items-center gap-2 2xl:justify-end shrink-0">
                <!-- Join -->
                <template v-if="selectedConsultation.bookingStatus === 'Completed'">
                  <span class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-emerald-100 text-emerald-700 font-semibold">
                    <FeatherIcon name="check-circle" class="w-4 h-4" />
                    Completed
                  </span>
                </template>

                <template v-else-if="selectedConsultation.paymentStatus !== 'Paid'">
                  <span class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-amber-100 text-amber-700 font-semibold"> Payment Pending </span>
                </template>

                <template v-else>
                  <button
                    type="button"
                    class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-teal-600 text-white font-semibold hover:bg-teal-700 transition"
                    :disabled="joiningConsultation"
                    @click="joinConsultation(selectedConsultation, selectedConsultation.bookingStatus === 'In-Progress')"
                  >
                    <FeatherIcon :name="selectedConsultation.bookingStatus === 'In-Progress' ? 'play' : 'video'" class="w-4 h-4" />

                    {{ selectedConsultation.bookingStatus === 'In-Progress' ? 'Continue Call' : 'Join Call' }}
                  </button>
                </template>

                <!-- Preview -->
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
                  @click="previewPrescription"
                >
                  <FeatherIcon name="eye" class="w-4 h-4" />
                  Preview Prescription
                </button>

                <!-- Upload -->
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
                  @click="uploadPrescription"
                >
                  <FeatherIcon name="upload" class="w-4 h-4" />
                  Upload Prescription
                </button>

                <!-- Save -->
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-amber-400 bg-white text-amber-700 font-semibold hover:bg-amber-50 transition"
                  @click="saveConsultation"
                >
                  <FeatherIcon name="save" class="w-4 h-4" />
                  Save
                </button>

                <!-- Submitted status -->
                <div v-if="prescriptionSubmitted" class="rounded-xl border border-green-200 bg-green-50 px-4 py-2.5 text-sm font-semibold text-green-700">
                  Prescription already submitted for this patient.
                </div>
                <!-- Publish -->
                <button
                  v-if="!prescriptionSubmitted"
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-amber-500 text-white font-semibold hover:bg-amber-600 transition"
                  @click="publishPrescription"
                >
                  <FeatherIcon name="send" class="w-4 h-4" />
                  Publish
                </button>
              </div>
            </div>
          </div>

          <!-- Context strip -->
          <div class="px-5 md:px-6 py-4 bg-gray-50 border-b border-gray-200">
            <!-- Reason -->
            <div class="w-full">
              <div class="flex items-start gap-2">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-400 shrink-0 pt-0.5"> Reason </span>

                <div class="min-w-0 flex-1">
                  <p
                    class="text-sm font-medium text-gray-700 leading-5 break-words whitespace-normal"
                    :class="{
                      'line-clamp-2': !isReasonExpanded(selectedConsultation.id),
                    }"
                  >
                    {{ selectedConsultation.reason }}
                  </p>

                  <button
                    v-if="selectedConsultation.reason && selectedConsultation.reason.length > 80"
                    type="button"
                    class="mt-1 text-xs font-semibold text-amber-600 hover:text-amber-700"
                    @click="toggleReason(selectedConsultation.id)"
                  >
                    {{ isReasonExpanded(selectedConsultation.id) ? 'Show less' : 'Show more' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Other metadata -->
            <div class="mt-3 pt-3 border-t border-gray-200 flex flex-wrap items-center gap-x-5 gap-y-2">
              <div class="flex items-center gap-2">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-400"> Mode </span>
                <span class="text-sm font-medium text-gray-700">
                  {{ selectedConsultation.mode }}
                </span>
              </div>

              <span class="hidden sm:block text-gray-300">•</span>

              <div class="flex items-center gap-2 min-w-0">
                <span class="text-xs font-semibold uppercase tracking-wide text-gray-400 shrink-0"> Appointment </span>
                <span class="text-sm font-medium text-gray-700 break-all">
                  {{ selectedConsultation.appointment }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Prescription upload -->
        <section v-if="uploadedPrescriptionVisible" class="mt-4 bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between gap-4">
            <div>
              <h3 class="text-lg font-bold text-gray-900">Upload Prescription</h3>

              <p class="text-sm text-gray-500 mt-1">Review the existing prescription or upload a new one.</p>
            </div>

            <button type="button" class="text-sm font-semibold text-gray-500 hover:text-gray-900" @click="uploadedPrescriptionVisible = false">Close</button>
          </div>

          <div class="p-5">
            <div class="rounded-xl border border-gray-200 bg-gray-50 p-6">
              <!-- Existing prescription -->
              <div v-if="prescriptionUploadCompleted" class="flex flex-col gap-4">
                <div class="w-20 h-20 rounded-xl bg-gray-100 border border-gray-200 overflow-hidden flex items-center justify-center shrink-0">
                  <img v-if="consultationRef?.prescriptionImagePreview" :src="consultationRef.prescriptionImagePreview" alt="Uploaded prescription" class="w-full h-full object-cover" />

                  <FeatherIcon v-else name="check-circle" class="w-8 h-8 text-emerald-600" />
                </div>

                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-gray-900 truncate">
                    {{ prescriptionUploadFileName || 'Prescription already uploaded' }}
                  </p>

                  <p class="text-sm text-gray-500 mt-1">Prescription already uploaded and processed.</p>
                </div>

                <div class="flex flex-col sm:flex-row gap-2 w-full">
                  <button
                    type="button"
                    class="px-4 py-3 rounded-xl border border-amber-400 text-amber-700 font-semibold hover:bg-amber-50 whitespace-nowrap w-full sm:w-auto"
                    @click="consultationRef?.openOcrModal"
                  >
                    View Extracted Prescription
                  </button>

                  <button
                    type="button"
                    class="px-4 py-3 rounded-xl bg-amber-500 text-white font-semibold hover:bg-amber-600 whitespace-nowrap w-full sm:w-auto"
                    @click="consultationRef?.triggerUpload"
                  >
                    Upload New Prescription
                  </button>
                </div>
              </div>

              <!-- Uploading / extracting -->
              <div v-else-if="prescriptionUploadProcessing" class="flex items-center gap-5">
                <div class="w-16 h-16 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                  <FeatherIcon name="loader" class="w-8 h-8 animate-spin" />
                </div>

                <div class="flex-1 min-w-0 lg:min-w-0">
                  <p class="font-semibold text-gray-900 truncate">
                    {{ prescriptionUploadFileName }}
                  </p>

                  <p class="text-sm text-gray-500 mt-1">Uploading and extracting prescription…</p>
                </div>
              </div>

              <!-- No existing prescription -->
              <div v-else class="border-2 border-dashed border-gray-300 rounded-xl bg-white p-8 text-center">
                <FeatherIcon name="upload-cloud" class="w-10 h-10 mx-auto text-gray-400" />

                <p class="mt-4 text-base font-semibold text-gray-800">Upload prescription image</p>

                <p class="mt-1 text-sm text-gray-500">Please upload the patient's prescription here.</p>

                <p class="mt-1 text-xs text-gray-400">JPG or PNG</p>

                <button type="button" class="mt-5 px-5 py-3 rounded-xl bg-amber-500 text-white font-semibold hover:bg-amber-600" @click="consultationRef?.triggerUpload">Upload Prescription</button>
              </div>
            </div>
          </div>
        </section>

        <div class="mt-4">
          <Consultation
            ref="consultationRef"
            :selected-consultation="selectedConsultation"
            @prescription-loaded="handlePrescriptionLoaded"
            @prescription-upload-processing="handlePrescriptionUploadProcessing"
          />
        </div>
      </main>

      <!-- Empty state -->
      <main v-else class="h-full min-h-full bg-white border border-gray-200 rounded-2xl flex items-center justify-center p-8">
        <div class="text-center max-w-md">
          <div class="w-16 h-16 mx-auto rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <FeatherIcon name="clipboard" class="w-7 h-7" />
          </div>

          <h2 class="mt-5 text-xl font-bold text-gray-900">Select a consultation</h2>

          <p class="mt-2 text-sm text-gray-500">Choose a consultation from the left to open the patient workspace.</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';
import { useRouter, useRoute } from 'vue-router';
import Consultation from './Consultation.vue';

const router = useRouter();
const route = useRoute();

const consultationsResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.get_teleconsultation_appointments',
  auto: true,
});

const startConsultationResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.start_consultation',
});

const consultationRef = ref(null);

const statusFilter = ref('Upcoming');
const selectedConsultation = ref(null);
const expandedReasons = ref(new Set());
const joiningConsultation = ref(false);

const showPrescriptionPreview = ref(false);
const uploadedPrescriptionVisible = ref(false);

const prescriptionUploadProcessing = ref(false);
const prescriptionUploadCompleted = ref(false);
const prescriptionUploadFileName = ref('');
const prescriptionSubmitted = ref(false);

function handlePrescriptionLoaded(prescription) {
  if (!prescription) {
    uploadedPrescriptionVisible.value = false;
    prescriptionUploadProcessing.value = false;
    prescriptionUploadCompleted.value = false;
    prescriptionUploadFileName.value = '';
    prescriptionSubmitted.value = false;
    return;
  }

  uploadedPrescriptionVisible.value = true;
  prescriptionUploadProcessing.value = false;
  prescriptionUploadCompleted.value = true;

  prescriptionUploadFileName.value = prescription.file_url?.split('/').pop() || 'Prescription already uploaded';

  prescriptionSubmitted.value = prescription.workflow_state === 'Confirmed' || prescription.workflow_state === 'Complete';
}

function handlePrescriptionUploadProcessing(payload) {
  uploadedPrescriptionVisible.value = true;
  prescriptionUploadProcessing.value = true;
  prescriptionUploadCompleted.value = false;
  prescriptionUploadFileName.value = payload?.fileName || 'Prescription';
}

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
    hour: 'numeric',
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
    prescriptionWorkflowState: appointment.prescription_workflow_state,
    mode: 'Video',
    reason: appointment.main_complaints || 'No reason provided',
    workflow: 'Clinical consultation',
    appointment: appointment.name,
    scheduledTime: appointment.scheduled_time,
  }));
});

const filteredConsultations = computed(() => {
  if (statusFilter.value === 'All') {
    return consultations.value;
  }

  if (statusFilter.value === 'Upcoming') {
  return consultations.value.filter(
    (consultation) =>
      consultation.bookingStatus !== 'Completed' &&
      consultation.paymentStatus === 'Paid'
  );
}

  if (statusFilter.value === 'Completed') {
    return consultations.value.filter((consultation) => consultation.bookingStatus === 'Completed');
  }

  if (statusFilter.value === 'Payment Pending') {
    return consultations.value.filter((consultation) => consultation.paymentStatus !== 'Paid');
  }

  return consultations.value;
});

function selectConsultation(consultation) {
  selectedConsultation.value = consultation;

  showPrescriptionPreview.value = false;
  uploadedPrescriptionVisible.value = false;

  prescriptionUploadProcessing.value = false;
  prescriptionUploadCompleted.value = false;
  prescriptionUploadFileName.value = '';

  const currentId = route.params.bookingId || route.query.bookingId || route.query.appointment;
  if (currentId !== consultation.id) {
    router.replace({ name: 'ConsultationDetails', params: { bookingId: consultation.id } });
  }
}

function isReasonExpanded(id) {
  return expandedReasons.value.has(id);
}

function toggleReason(id) {
  const next = new Set(expandedReasons.value);

  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }

  expandedReasons.value = next;
}

function statusClass(consultation) {
  if (consultation.bookingStatus === 'Completed') {
    return 'bg-emerald-100 text-emerald-700';
  }

  if (consultation.paymentStatus !== 'Paid') {
    return 'bg-amber-100 text-amber-700';
  }

  if (consultation.bookingStatus === 'In-Progress') {
    return 'bg-blue-100 text-blue-700';
  }

  return 'bg-gray-100 text-gray-700';
}

async function joinConsultation(consultation, isResume = false) {
  if (!consultation?.id || joiningConsultation.value) {
    return;
  }

  joiningConsultation.value = true;

  try {
    const response = await startConsultationResource.submit({
      appointmentId: consultation.id,
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
        resume: isResume ? '1' : '0',
      },
    });
  } catch (error) {
    console.error('Failed to start consultation:', error);
  } finally {
    joiningConsultation.value = false;
  }
}

function previewPrescription() {
  uploadedPrescriptionVisible.value = false;

  if (consultationRef.value?.previewTemplate) {
    consultationRef.value.previewTemplate();
    return;
  }

  console.warn('Prescription preview is not available.');
}

function openExistingPreview() {
  if (consultationRef.value?.previewTemplate) {
    consultationRef.value.previewTemplate();
    return;
  }

  showPrescriptionPreview.value = true;
}

function uploadPrescription() {
  uploadedPrescriptionVisible.value = true;
}

async function handlePrescriptionUpload(event) {
  const file = event.target.files?.[0];

  if (!file) {
    return;
  }

  prescriptionUploadFileName.value = file.name;
  prescriptionUploadProcessing.value = true;
  prescriptionUploadCompleted.value = false;
  uploadedPrescriptionVisible.value = true;

  try {
    await consultationRef.value?.handlePrescriptionFile(event);
  } catch (error) {
    console.error('Prescription upload failed:', error);
    prescriptionUploadProcessing.value = false;
    prescriptionUploadCompleted.value = false;
  } finally {
    event.target.value = '';
  }
}

function saveConsultation() {
  if (consultationRef.value?.saveConsultation) {
    consultationRef.value.saveConsultation();
    return;
  }

  if (consultationRef.value?.savePrescription) {
    consultationRef.value.savePrescription();
    return;
  }

  console.warn('Save action is not exposed by Consultation.vue yet.');
}

async function publishPrescription() {
  if (consultationRef.value?.finalizePrescription) {
    await consultationRef.value.finalizePrescription();
    return;
  }

  console.warn('Publish action is not exposed by Consultation.vue.');
}

watch(
  filteredConsultations,
  (items) => {
    if (!items.length) {
      selectedConsultation.value = null;
      return;
    }

    const appointmentIdFromUrl = route.query.bookingId || route.params.bookingId || route.query.appointment;

    if (appointmentIdFromUrl) {
      const searchId = String(appointmentIdFromUrl).toLowerCase();
      const matchingConsultation = items.find((item) => String(item.id).toLowerCase() === searchId);

      if (matchingConsultation) {
        selectConsultation(matchingConsultation);
        return;
      }
    }

    const selectedStillExists = items.some((item) => item.id === selectedConsultation.value?.id);

    if (!selectedStillExists) {
      selectConsultation(items[0]);
    }
  },
  { immediate: true }
);
</script>
