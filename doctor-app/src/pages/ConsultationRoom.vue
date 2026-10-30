<template>
  <div class="h-screen flex flex-col bg-gray-950 text-white overflow-hidden select-none">
    <!-- Top Bar -->
    <header class="h-14 md:h-16 px-3 md:px-6 bg-gray-900 border-b border-gray-800 flex items-center flex-shrink-0 z-20">
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
        <button @click="handleBackClick" type="button" class="p-1.5 sm:p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors flex-shrink-0" title="Back to Dashboard">
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
      <div class="flex items-center gap-1 md:gap-2 flex-shrink-0 order-3 md:order-none"></div>
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

    <!-- Leave Consultation Confirmation Modal -->
    <div
      v-if="showLeaveModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      @click.self="showLeaveModal = false"
    >
      <div class="bg-gray-900 border border-gray-800 rounded-2xl max-w-md w-full p-5 sm:p-6 shadow-2xl text-white">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 flex-shrink-0">
            <FeatherIcon name="alert-triangle" class="w-5 h-5" />
          </div>
          <div>
            <h3 class="text-base font-bold text-white">Leave Consultation Room?</h3>
            <p class="text-xs text-gray-400">Choose how you would like to proceed</p>
          </div>
        </div>

        <p class="text-xs sm:text-sm text-gray-300 mb-5 leading-relaxed">
          Do you intend to return to this call, or would you like to conclude the consultation now?
        </p>

        <div class="flex flex-col gap-3">
          <!-- Option 1: Step Away / Return Later (calls goBack) -->
          <button
            @click="handleStepAway"
            type="button"
            class="w-full p-3.5 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 text-left transition-colors flex items-center justify-between group"
          >
            <div>
              <p class="text-xs sm:text-sm font-semibold text-white group-hover:text-amber-300 transition-colors">
                Step Away & Return Later
              </p>
              <p class="text-[11px] text-gray-400 mt-0.5">
                Keeps patient connected. Mutes mic & camera. You can resume from dashboard.
              </p>
            </div>
            <FeatherIcon name="arrow-right" class="w-4 h-4 text-gray-400 group-hover:text-amber-300 ml-2 flex-shrink-0" />
          </button>

          <!-- Option 2: Leave & End Consultation (calls endConsultation) -->
          <button
            @click="handleEndConsultationFromModal"
            :disabled="isEndingConsultation"
            type="button"
            class="w-full p-3.5 rounded-xl bg-red-600/15 hover:bg-red-600/25 border border-red-500/30 text-left transition-colors flex items-center justify-between group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div>
              <p class="text-xs sm:text-sm font-semibold text-red-400 group-hover:text-red-300 transition-colors flex items-center gap-2">
                <span v-if="isEndingConsultation" class="w-3 h-3 rounded-full border-2 border-red-400 border-t-transparent animate-spin"></span>
                {{ isEndingConsultation ? 'Ending Consultation...' : 'End Consultation Completely' }}
              </p>
              <p class="text-[11px] text-red-400/80 mt-0.5">
                Disconnects the call and takes you to prescription / consultation summary.
              </p>
            </div>
            <FeatherIcon v-if="!isEndingConsultation" name="phone-off" class="w-4 h-4 text-red-400 group-hover:text-red-300 ml-2 flex-shrink-0" />
          </button>
        </div>

        <!-- Cancel / Stay in call -->
        <div class="mt-4 pt-3 border-t border-gray-800 flex justify-end">
          <button
            @click="showLeaveModal = false"
            type="button"
            class="px-4 py-2 rounded-lg text-xs font-medium text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            Stay in Call
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { FeatherIcon, createResource } from 'frappe-ui';
import { getAgoraService } from '@/utils/agora';
import logoUrl from '@/assets/images/logo-01.png';

const route = useRoute();
const router = useRouter();

// Reusable Frappe resources
const endConsultationResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.end_consultation',
});

const getPatientResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.get_appointment_details',
});

const logCallEventResource = createResource({
  url: 'wellnest.api.logger.log_call_event',
});

const bookingId = computed(() => route.params.bookingId || route.query.bookingId || route.query.channelName || '');
const channelName = bookingId;

function logCallEvent(event, metadata = {}) {
  console.log('CALL EVENT:', event, metadata);
  logCallEventResource
    .submit({
      event,
      appointment_id: metadata.appointment_id || bookingId.value,
      ...metadata,
    })
    .catch((error) => {
      console.error(`Failed to log call event: ${event}`, error);
    });
}

// Call State
const agora = getAgoraService();
const isBackgrounded = ref(false);
const isMuted = ref(false);
const isVideoOff = ref(false);
const isScreenSharing = ref(false);
const remoteUserConnected = ref(false);
const isMobileScreen = ref(false);
const isMobileDrawerOpen = ref(false);
const showLeaveModal = ref(false);
const isEndingConsultation = ref(false);
let isLeavingRoom = false;

function handleBackClick() {
  showLeaveModal.value = true;
}

function confirmEndCall() {
  showLeaveModal.value = true;
}

async function handleStepAway() {
  showLeaveModal.value = false;
  await goBack();
}

async function handleEndConsultationFromModal() {
  if (isEndingConsultation.value) return;
  isEndingConsultation.value = true;
  try {
    await endConsultation();
  } finally {
    isEndingConsultation.value = false;
    showLeaveModal.value = false;
  }
}

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

function startTimer() {
  if (timerInterval) return;

  // Record the moment the call actually started (patient connected).
  // Stored on singleton so it survives component unmount/remount.
  if (!agora.callStartedAt) {
    agora.callStartedAt = Date.now();
  }

  // Seed elapsed time in case we're resuming after a navigation away.
  callDurationSeconds.value = Math.floor((Date.now() - agora.callStartedAt) / 1000);

  timerInterval = setInterval(() => {
    callDurationSeconds.value = Math.floor((Date.now() - agora.callStartedAt) / 1000);
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

// Helper to remove active playback into DOM video elements
function stopVideoDomRendering() {
  if (agora.localVideoTrack) {
    agora.localVideoTrack.stop();
  }
  if (agora.client?.remoteUsers) {
    for (const user of agora.client.remoteUsers) {
      if (user.videoTrack) {
        user.videoTrack.stop();
      }
    }
  }
}

// Patient EHR Data
const patient = ref({
  patient_id: '',
  full_name: 'Patient',
  age: '',
  gender: '',
  concern: '',
});

async function joinRoom() {
  try {
    const { channelName: backendChannelName, uid, rtcToken, appId } = route.query;

    if (!backendChannelName || !uid || rtcToken === undefined) {
      throw new Error('Missing consultation session details');
    }

    // Doctor came back before the background timeout — cancel the auto-leave.
    agora.clearBackgroundTimeout();

    const { localVideoTrack } = await agora.join({
      appId,
      channelName: backendChannelName,
      token: rtcToken || null,
      uid: Number(uid),
      onUserPublished: async (user, mediaType) => {
        await agora.client.subscribe(user, mediaType);
        if (mediaType === 'video') {
          remoteUserConnected.value = true;
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
      onUserUnpublished: () => {
        // User turned off camera or mic but is still in the channel
      },
      onUserLeft: () => {
        remoteUserConnected.value = false;
      },
    });

    const isResume = route.query.resume === '1';

    logCallEvent(isResume ? 'doctor_resumed_call' : 'doctor_joined_rtc_channel', {
      channel: backendChannelName,
      uid: Number(uid),
    });

    // Play local camera feed in #local-player (first join only;
    // resume re-plays it after restoring mic/camera below).
    if (!isResume) {
      setTimeout(() => {
        const localElement = document.getElementById('local-player');
        if (localElement && localVideoTrack) {
          localVideoTrack.play(localElement);
        }
      }, 100);
    } else {
      // Restore A/V that was silenced when the doctor stepped away.
      await agora.toggleAudio(true);
      await agora.toggleVideo(true);
      isMuted.value = false;
      isVideoOff.value = false;

      setTimeout(() => {
        // Re-render local video into the PiP element.
        const localElement = document.getElementById('local-player');
        if (localElement && agora.localVideoTrack) {
          agora.localVideoTrack.play(localElement);
        }

        // Re-render any remote streams already in the channel.
        for (const user of agora.client.remoteUsers) {
          if (user.videoTrack) {
            remoteUserConnected.value = true;
            const playerElement = document.getElementById('remote-player');
            if (playerElement) user.videoTrack.play(playerElement);
            startTimer();
          }
          if (user.audioTrack) {
            user.audioTrack.play();
          }
        }
      }, 200);
    }
  } catch (error) {
    console.error('Failed to join Agora channel:', error);
  }
}

async function toggleAudio() {
  isMuted.value = !isMuted.value;
  await agora.toggleAudio(!isMuted.value);
}

async function toggleVideo() {
  isVideoOff.value = !isVideoOff.value;
  await agora.toggleVideo(!isVideoOff.value);
}

async function endConsultation() {
  try {
    if (bookingId.value) {
      await endConsultationResource.submit({
        appointment: bookingId.value,
      });

      logCallEvent('call_ended', {
        duration_seconds: callDurationSeconds.value,
        doctor_joined: true,
      });
    }
  } catch (error) {
    console.error('Failed to end consultation on backend:', error);
  } finally {
    await leaveRoom();
  }
}

// Navigate back to the dashboard WITHOUT leaving the Agora channel,
// so the patient stays connected while the doctor reviews their documents.
// Mic and camera are muted while away so the doctor isn't inadvertently broadcasting.
// A 5-minute safety timeout auto-closes the channel if the doctor doesn't return.
const BACKGROUND_TIMEOUT_MS = 5 * 60 * 1000;

async function goBack() {
  isBackgrounded.value = true;
  stopTimer();

  // Stop screen sharing if active
  if (isScreenSharing.value) {
    await agora.stopScreenShare();
    isScreenSharing.value = false;
  }

  // Pause A/V — keeps the RTC slot alive but stops transmitting.
  await agora.toggleAudio(false);
  await agora.toggleVideo(false);
  isMuted.value = true;
  isVideoOff.value = true;

  // Stop rendering to DOM elements to avoid detached DOM node leaks
  stopVideoDomRendering();

  // Auto-close if the doctor doesn't come back within the timeout window.
  // Capture primitive strings/numbers to avoid retaining component closures.
  const appointmentId = bookingId.value;
  const durationSeconds = callDurationSeconds.value;

  agora.scheduleBackgroundTimeout(async () => {
    try {
      await endConsultationResource.submit({ appointment: appointmentId });
    } catch (error) {
      console.error('Failed to end abandoned consultation:', error);
    }
    logCallEvent('doctor_abandoned_call', {
      appointment_id: appointmentId,
      duration_seconds: durationSeconds,
    });
    await agora.leave();
  }, BACKGROUND_TIMEOUT_MS);

  router.push({
    name: 'Consultations',
    query: {
      status: 'Upcoming',
      bookingId: bookingId.value,
      resume: '1',
    },
  });
}

async function leaveRoom() {
  if (isLeavingRoom) return;
  isLeavingRoom = true;

  stopTimer();
  stopVideoDomRendering();

  try {
    await agora.leave();
  } catch (error) {
    console.warn('Error during agora.leave():', error);
  }

  logCallEvent('doctor_left_rtc_channel', {
    duration_seconds: callDurationSeconds.value,
  });

  try {
    await router.push({
      name: 'Consultations',
      query: {
        status: 'Prescription due',
        bookingId: bookingId.value,
      },
    });
  } catch (routerError) {
    console.error('Router push failed, falling back to location replace:', routerError);
    window.location.href = `/doctor-app/consultations?status=Prescription+due&bookingId=${encodeURIComponent(bookingId.value)}`;
  }
}

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

onMounted(async () => {
  handleResize();
  window.addEventListener('resize', handleResize);

  await getPatient();
  await joinRoom();
});

onUnmounted(async () => {
  window.removeEventListener('resize', handleResize);
  stopTimer();
  stopVideoDomRendering();

  // Only fully leave the Agora channel on true teardown if not already left
  if (!isBackgrounded.value && !isLeavingRoom) {
    await agora.leave();
  }
});
</script>

<style scoped>
.date-input::-webkit-calendar-picker-indicator {
  filter: invert(1);
}
</style>
