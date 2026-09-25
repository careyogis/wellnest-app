<template>
  <div class="p-4 md:p-6 lg:p-8">
    <!-- Page Header -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Consultations</h1>
        <p class="text-gray-500 mt-1">Select a consultation to open the patient workspace.</p>
      </div>

      <button
        type="button"
        class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700 transition"
        @click="showCancelAllModal = true"
      >
        <FeatherIcon name="x-circle" class="w-4 h-4" />
        Cancel All Consultations
      </button>
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
                  <template v-if="selectedConsultation.bookingStatus === 'Cancelled by Doctor' || selectedConsultation.bookingStatus === 'Cancelled'">
                    <span class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gray-100 text-gray-600 font-semibold">
                      <FeatherIcon name="x-circle" class="w-4 h-4" />
                      Cancelled
                    </span>
                  </template>

                  <button
                    v-else
                    type="button"
                    class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-teal-600 text-white font-semibold hover:bg-teal-700 transition"
                    :disabled="joiningConsultation"
                    @click="joinConsultation(selectedConsultation, selectedConsultation.bookingStatus === 'In-Progress')"
                  >
                    <FeatherIcon :name="selectedConsultation.bookingStatus === 'In-Progress' ? 'play' : 'video'" class="w-4 h-4" />

                    {{ selectedConsultation.bookingStatus === 'In-Progress' ? 'Continue Call' : 'Join Call' }}
                  </button>
                </template>
                <!-- Cancel Consultation -->
                <button
                  v-if="selectedConsultation.bookingStatus === 'Scheduled'"
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-red-300 bg-white text-red-600 font-semibold hover:bg-red-50 transition"
                  @click="showCancelModal = true"
                >
                  <FeatherIcon name="x-circle" class="w-4 h-4" />
                  Cancel Consultation
                </button>

                <!-- Preview -->
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
                  @click="previewPrescription"
                >
                  <FeatherIcon name="eye" class="w-4 h-4" />
                  Preview Prescription
                </button>

                <!-- Prescription History -->
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
                  @click="uploadPrescription"
                >
                  <FeatherIcon name="file-text" class="w-4 h-4" />
                  Prescription
                </button>

                <!-- Health Vault -->
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
                  @click="openHealthVault"
                >
                  <FeatherIcon name="clipboard" class="w-4 h-4" />
                  Health Vault
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
              <h3 class="text-lg font-bold text-gray-900">Prescription</h3>

              <p class="text-sm text-gray-500 mt-1">Review the current prescription or manage previous prescriptions.</p>
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
                  <button type="button" class="px-5 py-3 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition" @click="openPatientHistory">
                    Previous Prescriptions
                  </button>
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

                <p class="mt-4 text-base font-semibold text-gray-800">No prescription for this consultation</p>

                <p class="mt-1 text-sm text-gray-500">You can upload a new prescription or view previous prescriptions for this patient.</p>

                <div class="mt-5 flex flex-col sm:flex-row items-center justify-center gap-2">
                  <button
                    v-if="hasPreviousPrescriptions"
                    type="button"
                    class="px-5 py-3 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
                    @click="openPatientHistory"
                  >
                    Previous Prescriptions
                  </button>

                  <button type="button" class="px-5 py-3 rounded-xl bg-amber-500 text-white font-semibold hover:bg-amber-600" @click="consultationRef?.triggerUpload">Upload New Prescription</button>
                </div>
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

  <!-- Patient Prescription History Modal -->
  <div v-if="showPatientHistoryModal" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="showPatientHistoryModal = false">
    <div class="w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Previous Prescriptions</h2>

          <p class="text-sm text-gray-500 mt-1">
            {{ selectedConsultation?.patient || 'Patient' }}
          </p>
        </div>

        <button type="button" class="text-gray-500 hover:text-gray-900 text-2xl" @click="showPatientHistoryModal = false">×</button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto p-6">
        <!-- Loading -->
        <div v-if="patientHistoryLoading" class="py-12 text-center">
          <FeatherIcon name="loader" class="w-8 h-8 mx-auto text-amber-500 animate-spin" />

          <p class="mt-3 text-sm text-gray-500">Loading previous prescriptions...</p>
        </div>

        <!-- Prescription list -->
        <div v-else-if="patientHistory.smart_prescriptions.length" class="space-y-3">
          <div v-for="prescription in patientHistory.smart_prescriptions" :key="prescription.name" class="border border-gray-200 rounded-xl p-4 hover:bg-gray-50 transition">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <!-- Prescription information -->
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <FeatherIcon name="file-text" class="w-5 h-5 text-amber-600 shrink-0" />

                  <p class="font-semibold text-gray-900">Prescription</p>
                </div>

                <div class="mt-2 space-y-1 text-sm text-gray-500">
                  <p>
                    <span class="font-medium text-gray-700">Date:</span>
                    {{ formatPrescriptionDate(prescription.prescription_date || prescription.creation) }}
                  </p>

                  <p>
                    <span class="font-medium text-gray-700">Doctor:</span>
                    {{ prescription.practitioner_name || prescription.practitioner || 'Not Available' }}
                  </p>

                  <p v-if="prescription.workflow_state">
                    <span class="font-medium text-gray-700">Status:</span>
                    {{ prescription.workflow_state }}
                  </p>
                </div>
              </div>

              <!-- View -->
              <button
                type="button"
                class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 shrink-0"
                @click="viewHistoricalPrescription(prescription)"
              >
                <FeatherIcon name="eye" class="w-4 h-4" />
                View
              </button>
            </div>
          </div>
        </div>

        <!-- Empty -->
        <div v-else class="py-12 text-center">
          <div class="w-12 h-12 mx-auto rounded-full bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="file-text" class="w-6 h-6 text-gray-400" />
          </div>

          <p class="mt-4 font-semibold text-gray-900">No previous prescriptions</p>

          <p class="mt-1 text-sm text-gray-500">No historical prescriptions were found for this patient.</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-white shrink-0">
        <button type="button" class="px-5 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200" @click="showPatientHistoryModal = false">Close</button>
      </div>
    </div>
  </div>

  <!-- Historical Prescription Viewer -->
  <div v-if="showHistoricalPrescriptionModal" class="fixed inset-0 z-[60] bg-black/50 flex items-center justify-center p-4" @click.self="closeHistoricalPrescription">
    <div class="w-full max-w-5xl max-h-[90vh] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Previous Prescription</h2>

          <p v-if="selectedHistoricalPrescription" class="text-sm text-gray-500 mt-1">
            {{ selectedHistoricalPrescription.practitioner_name || 'Doctor not available' }}
            <span class="mx-1">•</span>
            {{ formatPrescriptionDate(selectedHistoricalPrescription.prescription_date) }}
          </p>
        </div>

        <button type="button" class="text-gray-500 hover:text-gray-900 text-2xl" @click="closeHistoricalPrescription">×</button>
      </div>

      <!-- Loading -->
      <div v-if="historicalPrescriptionLoading" class="flex-1 flex items-center justify-center py-16">
        <div class="text-center">
          <FeatherIcon name="loader" class="w-8 h-8 mx-auto text-amber-500 animate-spin" />

          <p class="mt-3 text-sm text-gray-500">Loading prescription...</p>
        </div>
      </div>

      <!-- Prescription -->
      <div v-else-if="selectedHistoricalPrescription" class="flex-1 overflow-y-auto p-6">
        <!-- Prescription metadata -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div class="border border-gray-200 rounded-xl p-4 bg-gray-50">
            <p class="text-xs text-gray-500">Patient</p>
            <p class="font-semibold text-gray-900 mt-1">
              {{ selectedConsultation?.patient || 'Not Available' }}
            </p>
          </div>

          <div class="border border-gray-200 rounded-xl p-4 bg-gray-50">
            <p class="text-xs text-gray-500">Doctor</p>
            <p class="font-semibold text-gray-900 mt-1">
              {{ selectedHistoricalPrescription.practitioner_name || 'Not Available' }}
            </p>
          </div>

          <div class="border border-gray-200 rounded-xl p-4 bg-gray-50">
            <p class="text-xs text-gray-500">Prescription Date</p>
            <p class="font-semibold text-gray-900 mt-1">
              {{ selectedHistoricalPrescription.prescription_date || 'Not Available' }}
            </p>
          </div>

          <div class="border border-gray-200 rounded-xl p-4 bg-gray-50">
            <p class="text-xs text-gray-500">Status</p>
            <p class="font-semibold text-gray-900 mt-1">
              {{ selectedHistoricalPrescription.workflow_state || 'Not Available' }}
            </p>
          </div>
        </div>

        <!-- Original Uploaded Prescription -->
        <div v-if="selectedHistoricalPrescription?.original_uploaded_prescription" class="mt-6 rounded-xl border border-gray-200 bg-gray-50 p-5">
          <div class="flex items-center justify-between gap-4">
            <div>
              <h3 class="text-base font-bold text-gray-900">Original Uploaded Prescription</h3>

              <p class="mt-1 text-sm text-gray-500">View the prescription image/document that was originally uploaded.</p>
            </div>

            <a
              :href="selectedHistoricalPrescription.original_uploaded_prescription"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
            >
              <FeatherIcon name="external-link" class="w-4 h-4" />
              Open Original
            </a>
          </div>
        </div>

        <!-- Examination -->
        <section v-if="selectedHistoricalPrescription.examination" class="mb-6">
          <h3 class="text-lg font-bold text-gray-900">Examination</h3>

          <div class="mt-2 rounded-xl border border-gray-200 p-4">
            <p class="text-sm text-gray-700 whitespace-pre-wrap">
              {{ selectedHistoricalPrescription.examination }}
            </p>
          </div>
        </section>

        <!-- Provisional Diagnosis -->
        <section v-if="selectedHistoricalPrescription.provisional_diagnosis" class="mb-6">
          <h3 class="text-lg font-bold text-gray-900">Provisional Diagnosis</h3>

          <div class="mt-2 rounded-xl border border-gray-200 p-4">
            <p class="text-sm text-gray-700 whitespace-pre-wrap">
              {{ selectedHistoricalPrescription.provisional_diagnosis }}
            </p>
          </div>
        </section>

        <!-- Diagnosis -->
        <section v-if="selectedHistoricalPrescription.diagnosis" class="mb-6">
          <h3 class="text-lg font-bold text-gray-900">Diagnosis</h3>

          <div class="mt-2 rounded-xl border border-gray-200 p-4">
            <p class="text-sm text-gray-700 whitespace-pre-wrap">
              {{ selectedHistoricalPrescription.diagnosis }}
            </p>
          </div>
        </section>

        <!-- Investigations -->
        <section v-if="selectedHistoricalPrescription.investigations" class="mb-6">
          <h3 class="text-lg font-bold text-gray-900">Investigations</h3>

          <div class="mt-2 rounded-xl border border-gray-200 p-4">
            <p class="text-sm text-gray-700 whitespace-pre-wrap">
              {{ selectedHistoricalPrescription.investigations }}
            </p>
          </div>
        </section>

        <!-- Medicines -->
        <section class="mb-6">
          <h3 class="text-lg font-bold text-gray-900">Treatment / Medication</h3>

          <div v-if="selectedHistoricalPrescription.medicines?.length" class="mt-3 overflow-x-auto border border-gray-200 rounded-xl">
            <table class="w-full text-left text-sm">
              <thead>
                <tr class="bg-gray-50 border-b border-gray-200">
                  <th class="px-4 py-3 font-semibold text-gray-900">Medicine</th>

                  <th class="px-4 py-3 font-semibold text-gray-900">Dose</th>

                  <th class="px-4 py-3 font-semibold text-gray-900">Frequency</th>

                  <th class="px-4 py-3 font-semibold text-gray-900">Instructions</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="medicine in selectedHistoricalPrescription.medicines" :key="medicine.name" class="border-b border-gray-100 last:border-b-0">
                  <td class="px-4 py-3 text-gray-800">
                    {{ medicine.medicine_name || '—' }}
                  </td>

                  <td class="px-4 py-3 text-gray-800">
                    {{ medicine.dosage || '—' }}
                  </td>

                  <td class="px-4 py-3 text-gray-800">
                    {{ medicine.timing || '—' }}
                  </td>

                  <td class="px-4 py-3 text-gray-800">
                    {{ medicine.instructions || '—' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="mt-3 rounded-xl border border-gray-200 p-4 text-sm text-gray-500">No medicines recorded.</div>
        </section>

        <!-- Follow-up -->
        <section v-if="selectedHistoricalPrescription.follow_up_advice || selectedHistoricalPrescription.follow_up_duration" class="mb-6">
          <h3 class="text-lg font-bold text-gray-900">Follow-up Advice</h3>

          <div class="mt-2 rounded-xl border border-gray-200 p-4 space-y-3">
            <div v-if="selectedHistoricalPrescription.follow_up_advice">
              <p class="text-xs font-semibold text-gray-500">Advice</p>

              <p class="text-sm text-gray-700 mt-1 whitespace-pre-wrap">
                {{ selectedHistoricalPrescription.follow_up_advice }}
              </p>
            </div>

            <div v-if="selectedHistoricalPrescription.follow_up_duration">
              <p class="text-xs font-semibold text-gray-500">Follow-up In</p>

              <p class="text-sm text-gray-700 mt-1">
                {{ selectedHistoricalPrescription.follow_up_duration }}
              </p>
            </div>
          </div>
        </section>

        <!-- General Instructions -->
        <section v-if="selectedHistoricalPrescription.general_instructions" class="mb-6">
          <h3 class="text-lg font-bold text-gray-900">General Instructions</h3>

          <div class="mt-2 rounded-xl border border-gray-200 p-4">
            <p class="text-sm text-gray-700 whitespace-pre-wrap">
              {{ selectedHistoricalPrescription.general_instructions }}
            </p>
          </div>
        </section>
      </div>

      <!-- Footer -->
      <div class="flex justify-end px-6 py-4 border-t border-gray-200 bg-white shrink-0">
        <button type="button" class="px-5 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200" @click="closeHistoricalPrescription">Close</button>
      </div>
    </div>
  </div>

  <!-- Health Vault Modal -->
  <div v-if="showHealthVaultModal" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="closeHealthVault">
    <div class="w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Health Vault</h2>

          <p class="text-sm text-gray-500 mt-1">
            {{ selectedConsultation?.patient || 'Patient' }}
          </p>
        </div>

        <button type="button" class="text-gray-500 hover:text-gray-900 text-2xl" @click="closeHealthVault">×</button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto p-6">
        <!-- Loading -->
        <div v-if="patientHistoryLoading" class="py-12 text-center">
          <FeatherIcon name="loader" class="w-8 h-8 mx-auto text-amber-500 animate-spin" />

          <p class="mt-3 text-sm text-gray-500">Loading Health Vault documents...</p>
        </div>

        <!-- Documents -->
        <div v-else-if="patientHistory.health_vault.length" class="space-y-3">
          <div v-for="document in patientHistory.health_vault" :key="document.name" class="border border-gray-200 rounded-xl p-4 hover:bg-gray-50 transition">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <!-- Document information -->
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <FeatherIcon name="file" class="w-5 h-5 text-amber-600 shrink-0" />

                  <p class="font-semibold text-gray-900 truncate">
                    {{ document.document_type || 'Health Document' }}
                  </p>
                </div>

                <div class="mt-2 space-y-1 text-sm text-gray-500">
                  <p v-if="document.document">
                    <span class="font-medium text-gray-700">Document:</span>
                    {{ document.document.split('/').pop() }}
                  </p>

                  <p v-if="document.creation">
                    <span class="font-medium text-gray-700">Date:</span>
                    {{ formatPrescriptionDate(document.creation) }}
                  </p>

                  <p v-if="document.batch_number">
                    <span class="font-medium text-gray-700">Batch:</span>
                    {{ document.batch_number }}
                  </p>
                </div>
              </div>

              <!-- Actions -->
              <div v-if="document.document" class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 shrink-0">
                <!-- Open -->
                <a
                  :href="document.document_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-gray-300 bg-white text-gray-700 font-semibold hover:bg-gray-50 transition"
                >
                  <FeatherIcon name="eye" class="w-4 h-4" />
                  Open
                </a>

                <!-- Download -->
                <a
                  :href="document.document_url"
                  download
                  class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 text-white font-semibold hover:bg-amber-600 transition"
                >
                  <FeatherIcon name="download" class="w-4 h-4" />
                  Download
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty -->
        <div v-else class="py-12 text-center">
          <div class="w-12 h-12 mx-auto rounded-full bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="folder" class="w-6 h-6 text-gray-400" />
          </div>

          <p class="mt-4 font-semibold text-gray-900">No Health Vault documents</p>

          <p class="mt-1 text-sm text-gray-500">No documents were found for this patient.</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end px-6 py-4 border-t border-gray-200 bg-white shrink-0">
        <button type="button" class="px-5 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200" @click="closeHealthVault">Close</button>
      </div>
    </div>
  </div>

  <!-- Cancel Consultation Modal -->
  <div v-if="showCancelModal" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="showCancelModal = false">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden">
      <!-- Modal Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-900">Cancel Consultation</h2>

        <button type="button" class="text-gray-500 hover:text-gray-900 text-2xl" @click="showCancelModal = false">×</button>
      </div>

      <!-- Modal Body -->
      <div class="px-6 py-5">
        <p class="text-sm text-gray-600 mb-4">Please select a reason for cancelling this consultation.</p>

        <div class="space-y-3">
          <label
            v-for="reason in ['Emergency', 'Health Issues', 'Personal Commitment', 'Technical Issues', 'Others']"
            :key="reason"
            class="flex items-center gap-3 p-3 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-50"
          >
            <input v-model="cancelReason" type="radio" name="cancelReason" :value="reason" class="w-4 h-4" />

            <span class="text-sm font-medium text-gray-700">
              {{ reason }}
            </span>
          </label>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="flex justify-end gap-3 px-6 py-4 border-t border-gray-200">
        <button type="button" class="px-5 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200" @click="showCancelModal = false">Close</button>

        <button
          type="button"
          class="px-5 py-3 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!cancelReason"
          @click="cancelConsultation"
        >
          Confirm Cancellation
        </button>
      </div>
    </div>
  </div>

  <!-- Cancel All Consultations Modal -->
  <div v-if="showCancelAllModal" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" @click.self="showCancelAllModal = false">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden">
      <!-- Modal Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-900">Cancel All Consultations</h2>

        <button type="button" class="text-gray-500 hover:text-gray-900 text-2xl" @click="showCancelAllModal = false">×</button>
      </div>

      <!-- Modal Body -->
      <div class="px-6 py-5">
        <p class="text-sm text-gray-600 mb-5">Select the date and reason for cancelling the consultations.</p>

        <!-- Date -->
        <div class="mb-5">
          <label class="block text-sm font-semibold text-gray-700 mb-2"> Consultation Date </label>

          <input v-model="cancelAllDate" type="date" class="w-full px-3 py-3 rounded-xl border border-gray-300 bg-white text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-amber-200" />
        </div>

        <!-- Reason -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-3"> Cancellation Reason </label>

          <div class="space-y-3">
            <label
              v-for="reason in ['Emergency', 'Health Issues', 'Personal Commitment', 'Technical Issues', 'Others']"
              :key="reason"
              class="flex items-center gap-3 p-3 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-50"
            >
              <input v-model="cancelAllReason" type="radio" name="cancelAllReason" :value="reason" class="w-4 h-4" />

              <span class="text-sm font-medium text-gray-700">
                {{ reason }}
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="flex justify-end gap-3 px-6 py-4 border-t border-gray-200">
        <button type="button" class="px-5 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200" @click="showCancelAllModal = false">Close</button>

        <button
          type="button"
          class="px-5 py-3 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!cancelAllDate || !cancelAllReason"
          @click="
            showCancelAllModal = false;
            showCancelAllConfirmation = true;
          "
        >
          Continue
        </button>
      </div>
    </div>
  </div>

  <!-- Cancel All Confirmation Modal -->
  <div v-if="showCancelAllConfirmation" class="fixed inset-0 z-[60] bg-black/50 flex items-center justify-center p-4" @click.self="showCancelAllConfirmation = false">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-900">Confirm Cancellation</h2>

        <button type="button" class="text-gray-500 hover:text-gray-900 text-2xl" @click="showCancelAllConfirmation = false">×</button>
      </div>

      <!-- Body -->
      <div class="px-6 py-6">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 text-red-600 flex items-center justify-center">
            <FeatherIcon name="alert-triangle" class="w-5 h-5" />
          </div>

          <div>
            <p class="text-base font-semibold text-gray-900">Are you sure you want to cancel all consultations?</p>

            <p class="mt-2 text-sm text-gray-600">
              This will cancel all scheduled consultations for
              <span class="font-semibold"> {{ cancelAllDate.split('-').reverse().join('-') }} </span>.
            </p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-3 px-6 py-4 border-t border-gray-200">
        <button
          type="button"
          class="px-5 py-3 rounded-xl bg-gray-100 text-gray-800 font-semibold hover:bg-gray-200"
          @click="
            showCancelAllConfirmation = false;
            showCancelAllModal = true;
          "
        >
          No, Go Back
        </button>

        <button type="button" class="px-5 py-3 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700" @click="cancelAllConsultations">Yes, Cancel All</button>
      </div>
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

const cancelConsultationResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.cancel_consultation',
});

const cancelAllConsultationsResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.cancel_all_consultations',
});

const patientHistoryResource = createResource({
  url: 'wellnest.api.patient_history.get_patient_history',
});

const historicalPrescriptionResource = createResource({
  url: 'wellnest.api.patient_history.get_historical_prescription',
});

const consultationRef = ref(null);

const statusFilter = ref('Upcoming');
const selectedConsultation = ref(null);
const expandedReasons = ref(new Set());
const joiningConsultation = ref(false);

const showCancelModal = ref(false);
const cancelReason = ref('');

const showCancelAllModal = ref(false);
const cancelAllReason = ref('');
const showCancelAllConfirmation = ref(false);
const cancelAllDate = ref('');

const showPrescriptionPreview = ref(false);
const uploadedPrescriptionVisible = ref(false);

const prescriptionUploadProcessing = ref(false);
const prescriptionUploadCompleted = ref(false);
const prescriptionUploadFileName = ref('');
const prescriptionSubmitted = ref(false);

const showPatientHistoryModal = ref(false);
const showHistoricalPrescriptionModal = ref(false);
const showHealthVaultModal = ref(false);

const patientHistory = ref({
  smart_prescriptions: [],
  health_vault: [],
});

const hasPreviousPrescriptions = computed(() => {
  return patientHistory.value.smart_prescriptions?.length > 0;
});

const selectedHistoricalPrescription = ref(null);
const patientHistoryLoading = ref(false);
const historicalPrescriptionLoading = ref(false);

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

async function uploadPrescription() {
  uploadedPrescriptionVisible.value = true;

  await loadPatientHistory();
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

function formatPrescriptionDate(value) {
  if (!value) return 'Not Available';

  const date = new Date(value.replace(' ', 'T'));

  if (Number.isNaN(date.getTime())) {
    return value;
  }

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
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return consultations.value.filter((consultation) => {
      const isUpcomingStatus =
        consultation.bookingStatus !== 'Completed' && consultation.bookingStatus !== 'Cancelled' && consultation.bookingStatus !== 'Cancelled by Doctor' && consultation.bookingStatus !== 'No Show';

      if (!isUpcomingStatus) return false;

      // Preserve the existing develop behavior:
      // Upcoming consultations must be paid.
      if (consultation.paymentStatus !== 'Paid') return false;

      if (consultation.scheduledTime) {
        const dateStr = String(consultation.scheduledTime).trim().split(' ')[0];
        const parts = dateStr.split('-');

        if (parts.length === 3) {
          const appointmentDate = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));

          return appointmentDate >= today;
        }
      }

      return true;
    });
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

  patientHistory.value = {
    smart_prescriptions: [],
    health_vault: [],
  };

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

async function cancelConsultation() {
  if (!selectedConsultation.value?.id || !cancelReason.value) {
    return;
  }

  try {
    await cancelConsultationResource.submit({
      appointment: selectedConsultation.value.id,
      reason: cancelReason.value,
    });

    showCancelModal.value = false;
    cancelReason.value = '';

    await consultationsResource.reload();
  } catch (error) {
    console.error('Failed to cancel consultation:', error);
  }
}

async function cancelAllConsultations() {
  if (!cancelAllDate.value || !cancelAllReason.value) {
    return;
  }

  try {
    await cancelAllConsultationsResource.submit({
      date: cancelAllDate.value,
      reason: cancelAllReason.value,
    });

    showCancelAllConfirmation.value = false;
    cancelAllReason.value = '';
    cancelAllDate.value = '';

    await consultationsResource.reload();
  } catch (error) {
    console.error('Failed to cancel all consultations:', error);
  }
}

async function loadPatientHistory() {
  const appointment = selectedConsultation.value?.appointment;

  if (!appointment) {
    return;
  }

  patientHistoryLoading.value = true;

  try {
    const response = await patientHistoryResource.submit({
      patient_appointment: appointment,
    });

    const history = response?.message || response || {};

    patientHistory.value = {
      smart_prescriptions: history.smart_prescriptions || [],
      health_vault: history.health_vault || [],
    };
  } catch (error) {
    console.error('Failed to load patient history:', error);

    patientHistory.value = {
      smart_prescriptions: [],
      health_vault: [],
    };
  } finally {
    patientHistoryLoading.value = false;
  }
}

async function openPatientHistory() {
  showPatientHistoryModal.value = true;

  await loadPatientHistory();
}

async function openHealthVault() {
  showHealthVaultModal.value = true;

  await loadPatientHistory();
}

function closeHealthVault() {
  showHealthVaultModal.value = false;
}

async function viewHistoricalPrescription(prescription) {
  const appointment = selectedConsultation.value?.appointment;

  if (!appointment || !prescription?.name) {
    return;
  }

  historicalPrescriptionLoading.value = true;
  selectedHistoricalPrescription.value = null;
  showHistoricalPrescriptionModal.value = true;

  try {
    const response = await historicalPrescriptionResource.submit({
      patient_appointment: appointment,
      prescription_name: prescription.name,
    });

    selectedHistoricalPrescription.value = response?.message || response || null;
  } catch (error) {
    console.error('Failed to load historical prescription:', error);

    showHistoricalPrescriptionModal.value = false;
    alert('Failed to load historical prescription.');
  } finally {
    historicalPrescriptionLoading.value = false;
  }
}

function closeHistoricalPrescription() {
  showHistoricalPrescriptionModal.value = false;
  selectedHistoricalPrescription.value = null;
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
