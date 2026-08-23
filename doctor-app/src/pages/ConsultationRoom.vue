<template>
  <div class="h-screen flex flex-col bg-gray-950 text-white overflow-hidden select-none">
    <!-- Top Bar -->
    <header class="h-14 sm:h-16 px-3 sm:px-6 bg-gray-900 border-b border-gray-800 flex items-center justify-between flex-shrink-0 z-20">
      <!-- Left: Patient Info & Back -->
      <div class="flex items-center gap-2 sm:gap-4 min-w-0">
        <button
          @click="leaveRoom"
          type="button"
          class="p-1.5 sm:p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors flex-shrink-0"
          title="Back to Dashboard"
        >
          <FeatherIcon name="arrow-left" class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
        <div class="min-w-0">
          <div class="flex items-center gap-1.5 sm:gap-2">
            <h1 class="font-bold text-sm sm:text-base text-white truncate">{{ patient.name }}</h1>
            <span class="px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs rounded-full bg-amber-500/20 text-amber-300 font-medium border border-amber-500/30 flex-shrink-0">
              {{ bookingId }}
            </span>
          </div>
          <p class="text-[11px] sm:text-xs text-gray-400 truncate">
            {{ patient.age }} yrs • {{ patient.gender }}
            <span class="hidden sm:inline"> • {{ patient.concern }}</span>
          </p>
        </div>
      </div>

      <!-- Center: Call Status / Timer -->
      <div class="flex items-center gap-1.5 sm:gap-3 flex-shrink-0 mx-2">
        <div class="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full bg-gray-800 border border-gray-700">
          <span
            class="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full animate-pulse flex-shrink-0"
            :class="remoteUserConnected ? 'bg-emerald-500' : 'bg-amber-400'"
          ></span>
          <span class="text-[11px] sm:text-xs font-mono font-medium text-gray-200">
            {{ remoteUserConnected ? formattedTime : (isMobileScreen ? 'Waiting...' : 'Waiting for patient...') }}
          </span>
        </div>
      </div>

      <!-- Right: Quick Actions -->
      <div class="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
        <!-- Chat Button -->
        <button
          @click="openDrawerTab('chat')"
          type="button"
          class="p-1.5 sm:p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors relative"
          title="In-call Chat"
        >
          <FeatherIcon name="message-square" class="w-4 h-4 sm:w-5 sm:h-5" />
          <span v-if="unreadChatCount > 0" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-black text-[10px] font-bold flex items-center justify-center">
            {{ unreadChatCount }}
          </span>
        </button>

        <!-- EHR / Notes Button (Mobile quick open) -->
        <button
          @click="openDrawerTab('summary')"
          type="button"
          class="p-1.5 sm:p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors lg:hidden"
          title="Patient EHR & Notes"
        >
          <FeatherIcon name="clipboard" class="w-4 h-4 sm:w-5 sm:h-5" />
        </button>

        <!-- Write Rx Button -->
        <button
          @click="openDrawerTab('rx')"
          type="button"
          class="px-2.5 sm:px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors flex items-center gap-1 sm:gap-1.5"
        >
          <FeatherIcon name="file-plus" class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span class="hidden sm:inline">Write </span>Rx
        </button>
      </div>
    </header>

    <!-- Main Workspace (Split Video + Clinical Drawer) -->
    <div class="flex-1 flex relative overflow-hidden">
      <!-- Left: Video Call Stage -->
      <div class="flex-1 relative bg-black flex flex-col justify-between p-2 sm:p-4 overflow-hidden min-w-0">
        <!-- Video Grid / Container -->
        <div class="flex-1 relative rounded-xl sm:rounded-2xl overflow-hidden bg-gray-900 border border-gray-800 flex items-center justify-center min-h-0">
          <!-- Remote Patient Video Stream -->
          <div
            id="remote-player"
            class="w-full h-full object-cover"
            v-show="remoteUserConnected"
          ></div>

          <!-- Waiting State if patient not connected -->
          <div v-if="!remoteUserConnected" class="text-center p-4 sm:p-8 max-w-md mx-auto">
            <div class="w-16 h-16 sm:w-24 sm:h-24 mx-auto mb-3 sm:mb-4 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center">
              <FeatherIcon name="user" class="w-8 h-8 sm:w-12 sm:h-12 text-gray-500" />
            </div>
            <h3 class="text-base sm:text-lg font-bold text-white mb-1">Waiting for Patient</h3>
            <p class="text-xs sm:text-sm text-gray-400 mb-3 sm:mb-4 px-2">
              {{ patient.name }} has been notified. Live video stream will start automatically when they connect.
            </p>
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
            <div v-if="isVideoOff" class="w-full h-full flex items-center justify-center bg-gray-900 text-gray-400 text-[10px] sm:text-xs font-medium">
              Camera Off
            </div>
            <div class="absolute bottom-1 left-1 sm:bottom-2 sm:left-2 px-1 sm:px-1.5 py-0.5 rounded bg-black/70 text-[9px] sm:text-[10px] font-medium text-white truncate max-w-[90%]">
              You
            </div>
          </div>

          <!-- Mobile floating drawer shortcut badge -->
          <button
            v-if="!isMobileDrawerOpen"
            @click="isMobileDrawerOpen = true"
            type="button"
            class="lg:hidden absolute bottom-3 left-3 px-3 py-1.5 rounded-full bg-gray-900/90 hover:bg-gray-800 text-amber-300 border border-amber-500/30 text-xs font-semibold backdrop-blur shadow-lg flex items-center gap-1.5 z-10"
          >
            <FeatherIcon name="sidebar" class="w-3.5 h-3.5" />
            <span>Copilot & Rx</span>
          </button>
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
          <button
            @click="toggleScreenShare"
            type="button"
            :class="isScreenSharing ? 'bg-amber-500 text-black border-amber-400' : 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700'"
            class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl border flex items-center justify-center transition-all shadow-lg flex-shrink-0"
            :title="isScreenSharing ? 'Stop Screen Share' : 'Share Screen'"
          >
            <FeatherIcon name="airplay" class="w-4 h-4 sm:w-5 sm:h-5" />
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
      <div
        v-if="isMobileDrawerOpen"
        @click="isMobileDrawerOpen = false"
        class="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-30 transition-opacity"
      ></div>

      <!-- Right: Clinical Copilot & Smart Rx Drawer -->
      <div
        :class="[
          'bg-gray-900 border-l border-gray-800 flex flex-col transition-all duration-300 ease-in-out',
          // Desktop sizing: standard sidebar
          'lg:relative lg:translate-x-0 lg:w-[380px] xl:w-[420px] lg:flex-shrink-0 lg:z-auto',
          // Mobile sizing: full slide-over overlay
          'fixed inset-y-0 right-0 z-40 w-full max-w-[420px] shadow-2xl lg:shadow-none',
          isMobileDrawerOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'
        ]"
      >
        <!-- Mobile Drawer Header Bar with Close Button -->
        <div class="lg:hidden flex items-center justify-between px-4 py-3 bg-gray-950 border-b border-gray-800">
          <div class="flex items-center gap-2">
            <FeatherIcon name="activity" class="w-4 h-4 text-amber-400" />
            <span class="font-bold text-sm text-white">Clinical Workspace</span>
          </div>
          <button
            @click="isMobileDrawerOpen = false"
            type="button"
            class="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 flex items-center gap-1 text-xs"
          >
            <FeatherIcon name="x" class="w-4 h-4" />
            <span>Return to Call</span>
          </button>
        </div>

        <!-- Drawer Tabs -->
        <div class="flex border-b border-gray-800 bg-gray-950/60 p-1.5 gap-1 flex-shrink-0">
          <button
            @click="activeTab = 'summary'"
            :class="activeTab === 'summary' ? 'bg-gray-800 text-white font-bold' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-2 text-xs rounded-lg transition-colors text-center truncate px-1"
          >
            Summary & EHR
          </button>
          <button
            @click="activeTab = 'chat'"
            :class="activeTab === 'chat' ? 'bg-gray-800 text-white font-bold' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-2 text-xs rounded-lg transition-colors text-center relative truncate px-1"
          >
            Chat
            <span v-if="unreadChatCount > 0" class="ml-1 px-1.5 py-0.2 rounded-full bg-amber-500 text-black text-[9px] font-bold">
              {{ unreadChatCount }}
            </span>
          </button>
          <button
            @click="activeTab = 'rx'"
            :class="activeTab === 'rx' ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-2 text-xs rounded-lg transition-colors text-center truncate px-1"
          >
            Smart Rx
          </button>
        </div>

        <!-- Tab 1: Summary & Patient EHR -->
        <div v-show="activeTab === 'summary'" class="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4 text-sm">
          <!-- Vitals Card -->
          <div class="bg-gray-950 rounded-xl p-3 sm:p-3.5 border border-gray-800">
            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 sm:mb-2.5">Recorded Vitals</h4>
            <div class="grid grid-cols-3 gap-1.5 sm:gap-2 text-center">
              <div class="bg-gray-900 p-2 rounded-lg border border-gray-800">
                <span class="text-[10px] text-gray-400">BP</span>
                <p class="font-bold text-xs sm:text-sm text-emerald-400">122/80</p>
              </div>
              <div class="bg-gray-900 p-2 rounded-lg border border-gray-800">
                <span class="text-[10px] text-gray-400">Heart Rate</span>
                <p class="font-bold text-xs sm:text-sm text-amber-400">74 bpm</p>
              </div>
              <div class="bg-gray-900 p-2 rounded-lg border border-gray-800">
                <span class="text-[10px] text-gray-400">SpO2</span>
                <p class="font-bold text-xs sm:text-sm text-blue-400">98%</p>
              </div>
            </div>
          </div>

          <!-- Medical History -->
          <div class="bg-gray-950 rounded-xl p-3 sm:p-3.5 border border-gray-800">
            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Conditions & Allergies</h4>
            <div class="space-y-1.5 text-xs text-gray-300">
              <p><span class="text-gray-500">Known Conditions:</span> Type 2 Diabetes (5 yrs), Hypertension</p>
              <p><span class="text-gray-500">Allergies:</span> Penicillin (Mild skin rash)</p>
              <p><span class="text-gray-500">Ongoing Meds:</span> Metformin 500mg, Telmisartan 40mg</p>
            </div>
          </div>

          <!-- Consultation Notes -->
          <div class="bg-gray-950 rounded-xl p-3 sm:p-3.5 border border-gray-800">
            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Doctor's Private Notes</h4>
            <textarea
              v-model="doctorNotes"
              rows="4"
              placeholder="Type clinical observations, patient reported symptoms, differential diagnosis..."
              class="w-full bg-gray-900 border border-gray-800 rounded-lg p-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-amber-500"
            ></textarea>
          </div>
        </div>

        <!-- Tab 2: In-Call Live Chat -->
        <div v-show="activeTab === 'chat'" class="flex-1 flex flex-col overflow-hidden">
          <div class="flex-1 overflow-y-auto p-3 sm:p-4 space-y-2.5 sm:space-y-3">
            <div
              v-for="(msg, idx) in chatMessages"
              :key="idx"
              :class="msg.sender === 'Doctor' ? 'ml-auto bg-amber-500/20 text-amber-200 border-amber-500/30' : 'mr-auto bg-gray-800 text-gray-200 border-gray-700'"
              class="max-w-[85%] sm:max-w-[80%] rounded-xl p-2.5 border text-xs"
            >
              <div class="font-bold text-[10px] text-gray-400 mb-0.5">{{ msg.sender }} • {{ msg.time }}</div>
              <p class="break-words">{{ msg.text }}</p>
            </div>
          </div>

          <div class="p-2.5 sm:p-3 bg-gray-950 border-t border-gray-800 flex gap-2 flex-shrink-0">
            <input
              v-model="newChatMessage"
              @keyup.enter="sendChatMessage"
              type="text"
              placeholder="Type message to patient..."
              class="flex-1 bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-amber-500"
            />
            <button
              @click="sendChatMessage"
              type="button"
              class="p-2 rounded-lg bg-amber-500 text-black font-bold hover:bg-amber-400 flex-shrink-0"
            >
              <FeatherIcon name="send" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Tab 3: Smart Prescription Generator -->
        <div v-show="activeTab === 'rx'" class="flex-1 flex flex-col overflow-hidden">
          <div class="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-gray-300 uppercase tracking-wider">Prescribed Medicines</h4>
              <button
                @click="addMedicine"
                type="button"
                class="px-2 py-1 rounded bg-gray-800 hover:bg-gray-700 text-amber-400 text-xs font-bold flex items-center gap-1"
              >
                <FeatherIcon name="plus" class="w-3 h-3" /> Add Drug
              </button>
            </div>

            <!-- Medicine List -->
            <div class="space-y-2.5">
              <div
                v-for="(med, idx) in medicines"
                :key="idx"
                class="bg-gray-950 p-2.5 sm:p-3 rounded-xl border border-gray-800 space-y-2"
              >
                <div class="flex items-center justify-between gap-2">
                  <input
                    v-model="med.name"
                    type="text"
                    placeholder="Medicine Name (e.g. Metformin 500mg)"
                    class="flex-1 bg-gray-900 border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:border-amber-500 font-medium"
                  />
                  <button @click="removeMedicine(idx)" class="p-1 text-gray-500 hover:text-red-400 flex-shrink-0" title="Remove Medicine">
                    <FeatherIcon name="trash-2" class="w-3.5 h-3.5" />
                  </button>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1.5 text-xs sm:text-[11px]">
                  <input
                    v-model="med.dosage"
                    type="text"
                    placeholder="Dosage (e.g. 1 tab)"
                    class="bg-gray-900 border border-gray-800 rounded px-2 py-1.5 text-white focus:outline-none focus:border-amber-500"
                  />
                  <input
                    v-model="med.timing"
                    type="text"
                    placeholder="Timing (e.g. After Meals)"
                    class="bg-gray-900 border border-gray-800 rounded px-2 py-1.5 text-white focus:outline-none focus:border-amber-500"
                  />
                  <input
                    v-model="med.duration"
                    type="text"
                    placeholder="Duration (e.g. 30 Days)"
                    class="bg-gray-900 border border-gray-800 rounded px-2 py-1.5 text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>
            </div>

            <!-- Advice / Lifestyle -->
            <div class="bg-gray-950 p-2.5 sm:p-3 rounded-xl border border-gray-800">
              <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Doctor's Advice / Diet</h4>
              <textarea
                v-model="adviceNotes"
                rows="3"
                placeholder="e.g. 45 mins brisk walk daily. Avoid sugar and refined carbs. Re-check fasting sugar in 2 weeks."
                class="w-full bg-gray-900 border border-gray-800 rounded-lg p-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-amber-500"
              ></textarea>
            </div>
          </div>

          <!-- Bottom Action: Sign & Dispatch Rx -->
          <div class="p-2.5 sm:p-3 bg-gray-950 border-t border-gray-800 flex-shrink-0">
            <button
              @click="submitPrescription"
              type="button"
              class="w-full py-2.5 sm:py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all shadow-lg"
            >
              <FeatherIcon name="check-circle" class="w-4 h-4" />
              Sign & Publish Smart Rx to Patient
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { FeatherIcon } from 'frappe-ui';
import { AgoraService } from '@/utils/agora';

const route = useRoute();
const router = useRouter();

const bookingId = computed(() => route.params.bookingId || 'room_doc_doc_1');
// const channelName = computed(() => `room_${bookingId.value.replace(/[^a-zA-Z0-9_]/g, '_')}`);
const channelName = bookingId;
// Call State
const agora = new AgoraService();
const isMuted = ref(false);
const isVideoOff = ref(false);
const isScreenSharing = ref(false);
const remoteUserConnected = ref(false);
const activeTab = ref('summary');
const unreadChatCount = ref(0);
const isMobileDrawerOpen = ref(false);
const isMobileScreen = ref(false);

function handleResize() {
  if (typeof window !== 'undefined') {
    isMobileScreen.value = window.innerWidth < 1024;
  }
}

function openDrawerTab(tab) {
  activeTab.value = tab;
  isMobileDrawerOpen.value = true;
}

// Timer
const callDurationSeconds = ref(0);
let timerInterval = null;

const formattedTime = computed(() => {
  const mins = Math.floor(callDurationSeconds.value / 60).toString().padStart(2, '0');
  const secs = (callDurationSeconds.value % 60).toString().padStart(2, '0');
  return `${mins}:${secs}`;
});

// Patient EHR Data
const patient = ref({
  name: 'Randhir',
  age: 42,
  gender: 'Male',
  concern: 'Follow-up for Blood Sugar Control & Routine Health Check',
});

// Notes & Chat
const doctorNotes = ref('');
const newChatMessage = ref('');
const chatMessages = ref([
  { sender: 'System', text: 'Encrypted channel active.', time: 'Just now' },
]);

// Smart Rx Data
const medicines = ref([
  { name: 'Metformin 500mg', dosage: '1 tablet', timing: 'After Breakfast & Dinner', duration: '30 Days' },
  { name: 'Glimepiride 1mg', dosage: '1 tablet', timing: 'Before Breakfast', duration: '30 Days' },
]);
const adviceNotes = ref('Maintain 45 mins morning walk daily. Check fasting blood sugar twice a week.');

onMounted(async () => {
  handleResize();
  window.addEventListener('resize', handleResize);
  await joinRoom();
});

onUnmounted(async () => {
  window.removeEventListener('resize', handleResize);
  clearInterval(timerInterval);
  await agora.leave();
});

async function joinRoom() {
  try {
    // TODO: Remove this after testing
    const tmpToken = '007eJxTYLi5siNm5uxV3yJbbO4/k+4/qa/67EnnB9nWC7OP1T1bar1JgSE1Oc0y2SLJPNnCwsjEOM0sKcnSwiItMS0lzTglJdHEZIdFZ1ZDICPDrWBdZkYGCATx+RiK8vNz41Pyk0FY15CBAQAMJycy';
    const { localVideoTrack } = await agora.join({
      channelName: channelName.value,
      token: tmpToken,
      uid: 2001,
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
}

async function toggleVideo() {
  isVideoOff.value = !isVideoOff.value;
  await agora.toggleVideo(!isVideoOff.value);
}

async function toggleScreenShare() {
  if (isScreenSharing.value) {
    await agora.stopScreenShare();
    isScreenSharing.value = false;
    // Replay local camera in local player
    if (agora.localVideoTrack) {
      const localElement = document.getElementById('local-player');
      if (localElement) agora.localVideoTrack.play(localElement);
    }
  } else {
    const screenTrack = await agora.startScreenShare();
    if (screenTrack) {
      isScreenSharing.value = true;
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

function addMedicine() {
  medicines.value.push({ name: '', dosage: '1 tablet', timing: 'After Meals', duration: '15 Days' });
}

function removeMedicine(index) {
  medicines.value.splice(index, 1);
}

function submitPrescription() {
  alert('Smart Prescription signed and delivered to patient app successfully!');
  activeTab.value = 'summary';
}

function confirmEndCall() {
  if (confirm('Are you sure you want to conclude this teleconsultation?')) {
    leaveRoom();
  }
}

async function leaveRoom() {
  clearInterval(timerInterval);
  await agora.leave();
  router.push({ name: 'Dashboard' });
}
</script>
