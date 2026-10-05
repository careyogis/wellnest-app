<template>
  <div class="h-screen flex flex-col bg-gray-950 text-white overflow-hidden select-none">
    <!-- Top Bar -->
    <header class="h-14 md:h-16 px-3 md:px-6 bg-gray-900 border-b border-gray-800 flex items-center flex-shrink-0 z-20">
      <!-- CareYogi Branding -->
      <!-- CareYogi Branding -->
      <div class="flex items-center gap-1.5 md:gap-2 flex-shrink-0 order-2 md:order-none mx-4 md:mx-8">
        <img :src="logoUrl" alt="CareYogi" class="h-8 w-10 md:h-10 md:w-14 object-contain opacity-100" style="filter: brightness(1.2) contrast(1.15)" />

        <div class="hidden md:block leading-tight">
          <p class="text-sm font-extrabold text-white tracking-wide">CAREYOGI</p>
          <p class="text-[10px] text-gray-400">Teleconsultation</p>
        </div>
      </div>
      <!-- Left: Patient Info & Back -->
      <div class="flex items-center gap-2 md:gap-4 min-w-0 flex-1 order-1 md:order-none mr-4 md:mr-8">
        <button @click="leaveRoom" type="button" class="p-1.5 sm:p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors flex-shrink-0" title="Back to Dashboard">
          <FeatherIcon name="arrow-left" class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <div class="min-w-0 max-w-[38vw] md:max-w-none">
          <div class="flex items-center gap-1.5 sm:gap-2">
            <h1 class="font-bold text-xs sm:text-base text-white truncate max-w-[90px] sm:max-w-none">
              {{ patient.full_name }}
            </h1>

            <span class="hidden sm:inline-flex px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs rounded-full bg-amber-500/20 text-amber-300 font-medium border border-amber-500/30 flex-shrink-0">
              {{ bookingId }}
            </span>
          </div>
          <p class="text-[10px] sm:text-xs text-gray-400 truncate">
            {{ patient.age }} yrs • {{ patient.gender }}
            <span class="hidden sm:inline"> • {{ patient.concern }}</span>
          </p>
        </div>
      </div>

      <!-- Center: Call Status / Timer -->
      <div class="sm:flex items-center gap-1.5 sm:gap-3 flex-shrink-0 mx-2">
        <div class="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 sm:py-1.5 rounded-full bg-gray-800 border border-gray-700">
          <span class="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full animate-pulse flex-shrink-0" :class="remoteUserConnected ? 'bg-emerald-500' : 'bg-amber-400'"></span>
          <span class="text-[10px] sm:text-xs font-mono font-medium text-gray-200">
            {{ remoteUserConnected ? formattedTime : isMobileScreen ? 'Waiting...' : 'Waiting for patient...' }}
          </span>
        </div>
      </div>

      <!-- Right: Quick Actions -->
      <div class="flex items-center gap-1 md:gap-2 flex-shrink-0 order-3 md:order-none">
        <!-- Chat Button -->
        <!--
<button @click="openDrawerTab('chat')" type="button" class="p-1.5 sm:p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors relative" title="In-call Chat">
  <FeatherIcon name="message-square" class="w-4 h-4 sm:w-5 sm:h-5" />
  <span v-if="unreadChatCount > 0" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-black text-[10px] font-bold flex items-center justify-center">
    {{ unreadChatCount }}
  </span>
</button>
-->

        <!-- EHR / Notes Button (Mobile quick open) -->
        <!-- <button @click="openDrawerTab('summary')" type="button" class="p-1.5 sm:p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors lg:hidden" title="Patient EHR & Notes">
          <FeatherIcon name="clipboard" class="w-4 h-4 sm:w-5 sm:h-5" />
        </button> -->
      </div>
    </header>

    <!-- Main Workspace (Split Video + Clinical Drawer) -->
    <div class="flex-1 flex relative overflow-hidden">
      <!-- Left: Video Call Stage -->
      <div class="flex-1 relative bg-black flex flex-col justify-between p-2 sm:p-4 overflow-hidden min-w-0">
        <!-- Video Grid / Container -->
        <div class="flex-1 relative rounded-xl sm:rounded-2xl overflow-hidden bg-gray-900 border border-gray-800 flex items-center justify-center min-h-0">
          <!-- Remote Patient Video Stream -->
          <div id="remote-player" class="w-full h-full object-cover" v-show="remoteUserConnected"></div>

          <!-- Waiting State if patient not connected -->
          <div v-if="!remoteUserConnected" class="text-center p-4 sm:p-8 max-w-md mx-auto">
            <div class="w-16 h-16 sm:w-24 sm:h-24 mx-auto mb-3 sm:mb-4 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center">
              <FeatherIcon name="user" class="w-8 h-8 sm:w-12 sm:h-12 text-gray-500" />
            </div>
            <h3 class="text-base sm:text-lg font-bold text-white mb-1">Waiting for Patient</h3>
            <p class="text-xs sm:text-sm text-gray-400 mb-3 sm:mb-4 px-2">{{ patient.full_name }} has been notified. Live video stream will start automatically when they connect.</p>
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 text-amber-300 text-xs border border-amber-500/20">
              <span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
              Room: {{ channelName }}
            </div>
          </div>

          <!-- Local Doctor Video (Self PiP) -->
          <div
            class="absolute top-2 right-2 sm:top-4 sm:right-4 w-28 h-20 sm:w-36 sm:h-28 md:w-44 md:h-32 rounded-lg sm:rounded-xl overflow-hidden bg-gray-950 border sm:border-2 border-gray-700 shadow-2xl z-10 group"
          >
            <div id="local-player" class="w-full h-full object-cover"></div>
            <div v-if="isVideoOff" class="w-full h-full flex items-center justify-center bg-gray-900 text-gray-400 text-[10px] sm:text-xs font-medium">Camera Off</div>
            <div class="absolute bottom-1 left-1 sm:bottom-2 sm:left-2 px-1 sm:px-1.5 py-0.5 rounded bg-black/70 text-[9px] sm:text-[10px] font-medium text-white truncate max-w-[90%]">You</div>
          </div>
        </div>

        <!-- In-Call Controls Floating Dock -->
        <div class="h-16 sm:h-20 flex items-center justify-center gap-2 sm:gap-4 mt-2 sm:mt-3 flex-shrink-0">
          <!-- Mic Toggle -->
          <button
            @click="toggleAudio"
            type="button"
            :class="isMuted ? 'bg-red-500/20 text-red-400 border-red-500/40 hover:bg-red-500/30' : 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700'"
            class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl border flex items-center justify-center transition-all shadow-lg flex-shrink-0"
            :title="isMuted ? 'Unmute Mic' : 'Mute Mic'"
          >
            <FeatherIcon :name="isMuted ? 'mic-off' : 'mic'" class="w-4 h-4 sm:w-5 sm:h-5" />
          </button>

          <!-- Video Toggle -->
          <button
            @click="toggleVideo"
            type="button"
            :class="isVideoOff ? 'bg-red-500/20 text-red-400 border-red-500/40 hover:bg-red-500/30' : 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700'"
            class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl border flex items-center justify-center transition-all shadow-lg flex-shrink-0"
            :title="isVideoOff ? 'Turn Video On' : 'Turn Video Off'"
          >
            <FeatherIcon :name="isVideoOff ? 'video-off' : 'video'" class="w-4 h-4 sm:w-5 sm:h-5" />
          </button>

          <!-- Screen Share Toggle -->

          <!-- End Call Button -->
          <button
            @click="confirmEndCall"
            type="button"
            class="px-3 sm:px-6 h-10 sm:h-12 rounded-xl sm:rounded-2xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs sm:text-sm flex items-center gap-1.5 sm:gap-2 transition-all shadow-xl shadow-red-600/30 flex-shrink-0"
          >
            <FeatherIcon name="phone-off" class="w-4 h-4 sm:w-5 sm:h-5" />
            <span class="hidden xs:inline sm:inline">End Call</span>
          </button>
        </div>
      </div>

      <!-- Backdrop overlay for mobile drawer -->
      <div v-if="isMobileDrawerOpen" @click="isMobileDrawerOpen = false" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 transition-opacity"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { FeatherIcon, createResource } from 'frappe-ui';
import { AgoraService } from '@/utils/agora';
import logoUrl from '@/assets/images/logo-01.png';
import { io } from 'socket.io-client';

const route = useRoute();
const router = useRouter();

let frappeSocket = null;

const endConsultationResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.end_consultation',
});

// const bookingId = computed(() => route.params.bookingId || 'room_doc_doc_1');
const bookingId = computed(() => route.params.bookingId);
// const channelName = computed(() => `room_${bookingId.value.replace(/[^a-zA-Z0-9_]/g, '_')}`);
const channelName = bookingId;

function logCallEvent(event, metadata = {}) {
  console.log('CALL EVENT:', event, metadata);
  createResource({
    url: 'wellnest.api.logger.log_call_event',
  })
    .submit({
      event,
      appointment_id: bookingId.value,
      ...metadata,
    })
    .catch((error) => {
      console.error(`Failed to log call event: ${event}`, error);
    });
}

// Call State
const agora = new AgoraService();
const isMuted = ref(false);
const isVideoOff = ref(false);
const isScreenSharing = ref(false);
const remoteUserConnected = ref(false);
const isMobileScreen = ref(false);

function handleResize() {
  if (typeof window !== 'undefined') {
    isMobileScreen.value = window.innerWidth < 1024;
  }
}

// Timer
const callDurationSeconds = ref(0);
let timerInterval = null;

const formattedTime = computed(() => {
  const mins = Math.floor(callDurationSeconds.value / 60)
    .toString()
    .padStart(2, '0');
  const secs = (callDurationSeconds.value % 60).toString().padStart(2, '0');
  return `${mins}:${secs}`;
});

// Patient EHR Data
const patient = ref({
  patient_id: 'PAT-00001',
  full_name: 'Randhir',
  age: 42,
  gender: 'Male',
  concern: 'Follow-up for Blood Sugar Control & Routine Health Check',
});

// Notes & Chat
const doctorNotes = ref('');
const newChatMessage = ref('');
const chatMessages = ref([{ sender: 'System', text: 'Encrypted channel active.', time: 'Just now' }]);


function triggerRxCamera() {
  rxPasteStatus.value = null;
  rxCameraInput.value?.click();
}

function triggerRxGallery() {
  rxPasteStatus.value = null;
  rxGalleryInput.value?.click();
}

function requestRxImageCapture(skipConfirmation = false) {
  if (!skipConfirmation && hasManualPrescriptionDetails()) {
    showUploadConfirmation.value = true;
    return;
  }

  const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

  if (isMobile) {
    showImageSourceChoice.value = true;
  } else {
    rxDesktopGalleryInput.value?.click();
  }
}

function selectRxCamera() {
  rxPasteStatus.value = null;
  rxCameraInput.value?.click();
  showImageSourceChoice.value = false;
  triggerRxCamera();
}

function selectRxGallery() {
  rxPasteStatus.value = null;
  rxGalleryInput.value?.click();
  showImageSourceChoice.value = false;
  triggerRxGallery();
}

function cancelRxImageSourceChoice() {
  showImageSourceChoice.value = false;
}

function cancelUploadConfirmation() {
  showUploadConfirmation.value = false;
}

function confirmPrescriptionUpload() {
  showUploadConfirmation.value = false;
  requestRxImageCapture(true);
}

function onRxImageSelected(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  showImageSourceChoice.value = false;
  rxSelectedFile.value = file;
  if (rxImagePreview.value) {
    URL.revokeObjectURL(rxImagePreview.value);
  }
  rxImagePreview.value = URL.createObjectURL(file);
  event.target.value = '';
}

function populatePrescription(prescription) {
  investigations.value = prescription?.investigations || '';
  doctorAdvice.value = prescription?.doctor_advice || '';
  followUpInDays.value = prescription?.follow_up_in_days || '';
  examination.value = prescription?.examination || '';
  provisionalDiagnosis.value = prescription?.provisional_diagnosis || '';

  medicines.value = (prescription?.medicines || []).map((medicine) => ({
    name: medicine.medicine_name || '',
    dosage: medicine.dosage || '',
    timing: medicine.timing || '',
    instructions: medicine.instructions || '',
  }));

  prescriptionName.value = prescription?.name || null;
  prescriptionWorkflowState.value = prescription?.workflow_state || 'Draft';

  prescriptionParsed.value = true;
  isEditingPrescription.value = true;
  rxSubmitted.value = true;
}

async function submitRxImage() {
  if (!rxSelectedFile.value) return;

  rxParseLoading.value = true;
  rxProcessingStarted.value = false;
  rxParseStatus.value = null;

  try {
    const formData = new FormData();

    formData.append('file', rxSelectedFile.value);
    // formData.append('is_private', '1');

    console.log('>>> PRESCRIPTION UPLOAD START');

    const uploadResponse = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: {
        'X-Frappe-CSRF-Token': window.csrf_token,
      },
      body: formData,
    });

    if (!uploadResponse.ok) {
      throw new Error(`Prescription image upload failed (${uploadResponse.status})`);
    }

    const uploadResult = await uploadResponse.json();

    const fileUrl = uploadResult?.message?.file_url;

    if (!fileUrl) {
      throw new Error('Prescription image upload succeeded, but no file URL was returned.');
    }

    console.log('>>> PRESCRIPTION UPLOAD SUCCESS:', fileUrl);

    console.log('>>> PRESCRIPTION OCR QUEUE REQUEST START');

    const parseResponse = await fetch('/api/method/wellnest.api.prescription.parse_and_create_prescription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token,
      },
      body: JSON.stringify({
        file_url: fileUrl,
        patient_appointment: bookingId.value,
      }),
    });

    const parseResult = await parseResponse.json();

    if (!parseResponse.ok) {
      throw new Error(parseResult?.exception || parseResult?.message || 'Failed to start prescription processing.');
    }

    const result = parseResult?.message || parseResult;

    console.log('>>> PRESCRIPTION OCR QUEUE RESPONSE:', result);

    if (result?.status === 'already_exists') {
      prescriptionName.value = result.name || null;
      prescriptionWorkflowState.value = result.workflow_state || null;

      console.log('>>> Existing prescription returned:', prescriptionName.value, prescriptionWorkflowState.value);

      // Reload persisted state from backend.
      await loadExistingPrescription();

      if (prescriptionWorkflowState.value === 'Processing') {
        rxProcessingStarted.value = true;

        rxParseStatus.value = {
          type: 'success',
          message: 'Prescription submitted earlier. Processing is still running in the background.',
        };
      }

      return;
    }

    if (result?.status !== 'queued') {
      throw new Error(result?.message || 'Prescription processing could not be started.');
    }

    prescriptionName.value = result.name || null;

    prescriptionWorkflowState.value = result.workflow_state || 'Processing';

    rxProcessingStarted.value = true;
    rxSubmitted.value = false;

    rxPersistedImage.value = fileUrl;

    if (rxImagePreview.value) {
      URL.revokeObjectURL(rxImagePreview.value);
    }

    rxImagePreview.value = null;
    rxSelectedFile.value = null;

    rxParseStatus.value = {
      type: 'success',
      message: 'Prescription submitted. Processing has started in the background. You can continue with the consultation.',
    };

    console.log('>>> PRESCRIPTION OCR JOB ACCEPTED');
    console.log('>>> Smart Prescription:', prescriptionName.value);
    console.log('>>> Workflow state:', prescriptionWorkflowState.value);
  } catch (error) {
    console.error('>>> PRESCRIPTION SUBMISSION FAILED:', error);

    rxProcessingStarted.value = false;

    rxParseStatus.value = {
      type: 'error',
      message: error?.message || 'Failed to submit prescription. Please try again.',
    };
  } finally {
    rxParseLoading.value = false;
  }
}

function clearRxImage() {
  if (rxImagePreview.value) URL.revokeObjectURL(rxImagePreview.value);
  rxImagePreview.value = null;
  rxSelectedFile.value = null;
}

onMounted(async () => {
  handleResize();
  window.addEventListener('resize', handleResize);

  frappeSocket = io({
    path: '/socket.io',
    transports: ['websocket', 'polling'],
  });

  frappeSocket.on('connect', () => {
    console.log('>>> Frappe Socket.IO connected:', frappeSocket.id);
  });

  frappeSocket.on('connect_error', (error) => {
    console.error('>>> Frappe Socket.IO connection error:', error);
  });

  await getPatient();
  await joinRoom();
});

onUnmounted(async () => {
  window.removeEventListener('resize', handleResize);

  if (frappeSocket) {
    frappeSocket.disconnect();
    frappeSocket = null;
  }

  clearInterval(timerInterval);
  await agora.leave();
});

async function joinRoom() {
  try {
    const { channelName: backendChannelName, uid, rtcToken, appId } = route.query;

    if (!backendChannelName || !uid || rtcToken === undefined) {
      throw new Error('Missing consultation session details');
    }

    const { localVideoTrack } = await agora.join({
      appId,
      channelName: backendChannelName,
      token: rtcToken || null,
      uid: Number(uid),
      onUserPublished: async (user, mediaType) => {
        await agora.client.subscribe(user, mediaType);
        if (mediaType === 'video') {
          remoteUserConnected.value = true;
          // Play remote video in DOM element #remote-player
          setTimeout(() => {
            const playerElement = document.getElementById('remote-player');
            if (playerElement && user.videoTrack) {
              user.videoTrack.play(playerElement);
            }
          }, 100);
          startTimer();
        }
        if (mediaType === 'audio') {
          user.audioTrack.play();
        }
      },
      onUserUnpublished: (user, mediaType) => {
        if (mediaType === 'video') {
          remoteUserConnected.value = false;
        }
      },
    });

    const isResume = route.query.resume === '1';

    logCallEvent(isResume ? 'doctor_resumed_call' : 'doctor_joined_rtc_channel', {
      channel: backendChannelName,
      uid: Number(uid),
    });

    // Play local camera feed in #local-player
    setTimeout(() => {
      const localElement = document.getElementById('local-player');
      if (localElement && localVideoTrack) {
        localVideoTrack.play(localElement);
      }
    }, 100);
  } catch (error) {
    console.error('Failed to join Agora channel:', error);
  }
}

function startTimer() {
  if (timerInterval) return;
  timerInterval = setInterval(() => {
    callDurationSeconds.value++;
  }, 1000);
}

async function toggleAudio() {
  isMuted.value = !isMuted.value;
  await agora.toggleAudio(!isMuted.value);

  // logCallEvent(isMuted.value ? 'doctor_muted' : 'doctor_unmuted');
}

async function toggleVideo() {
  isVideoOff.value = !isVideoOff.value;
  await agora.toggleVideo(!isVideoOff.value);

  // logCallEvent(isVideoOff.value ? 'doctor_video_disabled' : 'doctor_video_enabled');
}

async function toggleScreenShare() {
  if (isScreenSharing.value) {
    await agora.stopScreenShare();
    isScreenSharing.value = false;

    // logCallEvent('screen_share_stopped');

    // Replay local camera in local player
    if (agora.localVideoTrack) {
      const localElement = document.getElementById('local-player');
      if (localElement) agora.localVideoTrack.play(localElement);
    }
  } else {
    const screenTrack = await agora.startScreenShare();
    if (screenTrack) {
      isScreenSharing.value = true;

      // logCallEvent('screen_share_started');
    }
  }
}

function sendChatMessage() {
  const text = newChatMessage.value.trim();
  if (!text) return;
  chatMessages.value.push({
    sender: 'Doctor',
    text,
    time: formattedTime.value,
  });
  newChatMessage.value = '';
}


async function confirmEndCall() {
  await endConsultation();
}

async function endConsultation() {
  if (!confirm('Are you sure you want to conclude this teleconsultation?')) {
    return;
  }

  try {
    await endConsultationResource.submit({
      appointment: bookingId.value,
    });

    logCallEvent('call_ended', {
      duration_seconds: callDurationSeconds.value,
      doctor_joined: true,
    });

    await leaveRoom();
  } catch (error) {
    console.error('Failed to end consultation:', error);
  }
}

async function leaveRoom() {
  clearInterval(timerInterval);
  await agora.leave();

  logCallEvent('doctor_left_rtc_channel', {
    duration_seconds: callDurationSeconds.value,
  });

  router.push({
    name: 'Consultations',
    query: {
    status: 'Completed',
    bookingId: bookingId.value,
  },
  });
}

const getPatientResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.get_appointment_details',
});

async function getPatient() {
  try {
    const res = await getPatientResource.submit({
      appointment: bookingId.value,
    });

    const result = res?.message || res || {};

    patient.value = {
      patient_id: result.patient || 'Unknown Patient Id',
      full_name: result.full_name || 'Unknown Patient Name',
      age: result.date_of_birth ? Math.floor((new Date() - new Date(result.date_of_birth)) / (365.25 * 24 * 60 * 60 * 1000)) : 'n/a',
      gender: result.gender || 'n/a',
      concern: result.main_complaints || '',
    };
  } catch (error) {
    console.error('Failed to get appointment details: ', error);
  }
}
</script>

<style scoped>
.date-input::-webkit-calendar-picker-indicator {
  filter: invert(1);
}
</style>
