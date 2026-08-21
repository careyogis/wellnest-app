<template>
  <div class="h-screen flex flex-col bg-gray-950 text-white overflow-hidden">
    <!-- Top Bar -->
    <header class="h-16 px-6 bg-gray-900 border-b border-gray-800 flex items-center justify-between flex-shrink-0">
      <div class="flex items-center gap-4">
        <button
          @click="leaveRoom"
          type="button"
          class="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          title="Back to Dashboard"
        >
          <FeatherIcon name="arrow-left" class="w-5 h-5" />
        </button>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="font-bold text-base text-white">{{ patient.name }}</h1>
            <span class="px-2 py-0.5 text-xs rounded-full bg-amber-500/20 text-amber-300 font-medium border border-amber-500/30">
              {{ bookingId }}
            </span>
          </div>
          <p class="text-xs text-gray-400">{{ patient.age }} yrs • {{ patient.gender }} • {{ patient.concern }}</p>
        </div>
      </div>

      <!-- Call Status / Timer -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800 border border-gray-700">
          <span
            class="w-2.5 h-2.5 rounded-full animate-pulse"
            :class="remoteUserConnected ? 'bg-emerald-500' : 'bg-amber-400'"
          ></span>
          <span class="text-xs font-mono font-medium text-gray-200">
            {{ remoteUserConnected ? formattedTime : 'Waiting for patient...' }}
          </span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center gap-2">
        <button
          @click="activeTab = 'chat'"
          type="button"
          class="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors relative"
          title="In-call Chat"
        >
          <FeatherIcon name="message-square" class="w-5 h-5" />
          <span v-if="unreadChatCount > 0" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-black text-[10px] font-bold flex items-center justify-center">
            {{ unreadChatCount }}
          </span>
        </button>
        <button
          @click="activeTab = 'rx'"
          type="button"
          class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors flex items-center gap-1.5"
        >
          <FeatherIcon name="file-plus" class="w-4 h-4" />
          Write Rx
        </button>
      </div>
    </header>

    <!-- Main Workspace (Split Video + Clinical Drawer) -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left: Video Call Stage -->
      <div class="flex-1 relative bg-black flex flex-col justify-between p-4">
        <!-- Video Grid / Container -->
        <div class="flex-1 relative rounded-2xl overflow-hidden bg-gray-900 border border-gray-800 flex items-center justify-center">
          <!-- Remote Patient Video Stream -->
          <div
            id="remote-player"
            class="w-full h-full object-cover"
            v-show="remoteUserConnected"
          ></div>

          <!-- Waiting State if patient not connected -->
          <div v-if="!remoteUserConnected" class="text-center p-8">
            <div class="w-24 h-24 mx-auto mb-4 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center">
              <FeatherIcon name="user" class="w-12 h-12 text-gray-500" />
            </div>
            <h3 class="text-lg font-bold text-white mb-1">Waiting for Patient</h3>
            <p class="text-sm text-gray-400 max-w-sm mb-4">
              {{ patient.name }} has been notified. Live video stream will start automatically when they connect.
            </p>
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 text-amber-300 text-xs border border-amber-500/20">
              <span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
              Room ID: {{ channelName }}
            </div>
          </div>

          <!-- Local Doctor Video (Self PiP) -->
          <div
            class="absolute top-4 right-4 w-44 h-32 rounded-xl overflow-hidden bg-gray-950 border-2 border-gray-700 shadow-2xl z-20 group"
          >
            <div id="local-player" class="w-full h-full object-cover"></div>
            <div v-if="isVideoOff" class="w-full h-full flex items-center justify-center bg-gray-900 text-gray-400 text-xs font-medium">
              Camera Off
            </div>
            <div class="absolute bottom-2 left-2 px-1.5 py-0.5 rounded bg-black/60 text-[10px] font-medium text-white">
              You (Dr. Sharma)
            </div>
          </div>
        </div>

        <!-- In-Call Controls Floating Dock -->
        <div class="h-20 flex items-center justify-center gap-4 mt-3">
          <!-- Mic Toggle -->
          <button
            @click="toggleAudio"
            type="button"
            :class="isMuted ? 'bg-red-500/20 text-red-400 border-red-500/40 hover:bg-red-500/30' : 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700'"
            class="w-12 h-12 rounded-2xl border flex items-center justify-center transition-all shadow-lg"
            :title="isMuted ? 'Unmute Mic' : 'Mute Mic'"
          >
            <FeatherIcon :name="isMuted ? 'mic-off' : 'mic'" class="w-5 h-5" />
          </button>

          <!-- Video Toggle -->
          <button
            @click="toggleVideo"
            type="button"
            :class="isVideoOff ? 'bg-red-500/20 text-red-400 border-red-500/40 hover:bg-red-500/30' : 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700'"
            class="w-12 h-12 rounded-2xl border flex items-center justify-center transition-all shadow-lg"
            :title="isVideoOff ? 'Turn Video On' : 'Turn Video Off'"
          >
            <FeatherIcon :name="isVideoOff ? 'video-off' : 'video'" class="w-5 h-5" />
          </button>

          <!-- Screen Share Toggle -->
          <button
            @click="toggleScreenShare"
            type="button"
            :class="isScreenSharing ? 'bg-amber-500 text-black border-amber-400' : 'bg-gray-800 text-white border-gray-700 hover:bg-gray-700'"
            class="w-12 h-12 rounded-2xl border flex items-center justify-center transition-all shadow-lg"
            :title="isScreenSharing ? 'Stop Screen Share' : 'Share Screen'"
          >
            <FeatherIcon name="airplay" class="w-5 h-5" />
          </button>

          <!-- End Call Button -->
          <button
            @click="confirmEndCall"
            type="button"
            class="px-6 h-12 rounded-2xl bg-red-600 hover:bg-red-500 text-white font-bold text-sm flex items-center gap-2 transition-all shadow-xl shadow-red-600/30"
          >
            <FeatherIcon name="phone-off" class="w-5 h-5" />
            End Call
          </button>
        </div>
      </div>

      <!-- Right: Clinical Copilot & Smart Rx Drawer -->
      <div class="w-96 md:w-[420px] bg-gray-900 border-l border-gray-800 flex flex-col flex-shrink-0">
        <!-- Drawer Tabs -->
        <div class="flex border-b border-gray-800 bg-gray-950/60 p-1.5 gap-1">
          <button
            @click="activeTab = 'summary'"
            :class="activeTab === 'summary' ? 'bg-gray-800 text-white font-bold' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-2 text-xs rounded-lg transition-colors text-center"
          >
            Summary & EHR
          </button>
          <button
            @click="activeTab = 'chat'"
            :class="activeTab === 'chat' ? 'bg-gray-800 text-white font-bold' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-2 text-xs rounded-lg transition-colors text-center relative"
          >
            Chat
          </button>
          <button
            @click="activeTab = 'rx'"
            :class="activeTab === 'rx' ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-2 text-xs rounded-lg transition-colors text-center"
          >
            Smart Rx
          </button>
        </div>

        <!-- Tab 1: Summary & Patient EHR -->
        <div v-show="activeTab === 'summary'" class="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
          <!-- Vitals Card -->
          <div class="bg-gray-950 rounded-xl p-3.5 border border-gray-800">
            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2.5">Recorded Vitals</h4>
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="bg-gray-900 p-2 rounded-lg border border-gray-800">
                <span class="text-[10px] text-gray-400">BP</span>
                <p class="font-bold text-sm text-emerald-400">122/80</p>
              </div>
              <div class="bg-gray-900 p-2 rounded-lg border border-gray-800">
                <span class="text-[10px] text-gray-400">Heart Rate</span>
                <p class="font-bold text-sm text-amber-400">74 bpm</p>
              </div>
              <div class="bg-gray-900 p-2 rounded-lg border border-gray-800">
                <span class="text-[10px] text-gray-400">SpO2</span>
                <p class="font-bold text-sm text-blue-400">98%</p>
              </div>
            </div>
          </div>

          <!-- Medical History -->
          <div class="bg-gray-950 rounded-xl p-3.5 border border-gray-800">
            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Conditions & Allergies</h4>
            <div class="space-y-1.5 text-xs text-gray-300">
              <p><span class="text-gray-500">Known Conditions:</span> Type 2 Diabetes (5 yrs), Hypertension</p>
              <p><span class="text-gray-500">Allergies:</span> Penicillin (Mild skin rash)</p>
              <p><span class="text-gray-500">Ongoing Meds:</span> Metformin 500mg, Telmisartan 40mg</p>
            </div>
          </div>

          <!-- Consultation Notes -->
          <div class="bg-gray-950 rounded-xl p-3.5 border border-gray-800">
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
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div
              v-for="(msg, idx) in chatMessages"
              :key="idx"
              :class="msg.sender === 'Doctor' ? 'ml-auto bg-amber-500/20 text-amber-200 border-amber-500/30' : 'mr-auto bg-gray-800 text-gray-200 border-gray-700'"
              class="max-w-[80%] rounded-xl p-2.5 border text-xs"
            >
              <div class="font-bold text-[10px] text-gray-400 mb-0.5">{{ msg.sender }} • {{ msg.time }}</div>
              <p>{{ msg.text }}</p>
            </div>
          </div>

          <div class="p-3 bg-gray-950 border-t border-gray-800 flex gap-2">
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
              class="p-2 rounded-lg bg-amber-500 text-black font-bold hover:bg-amber-400"
            >
              <FeatherIcon name="send" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Tab 3: Smart Prescription Generator -->
        <div v-show="activeTab === 'rx'" class="flex-1 flex flex-col overflow-hidden">
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
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
                class="bg-gray-950 p-3 rounded-xl border border-gray-800 space-y-2"
              >
                <div class="flex items-center justify-between gap-2">
                  <input
                    v-model="med.name"
                    type="text"
                    placeholder="Medicine Name (e.g. Metformin 500mg)"
                    class="flex-1 bg-gray-900 border border-gray-800 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-amber-500 font-medium"
                  />
                  <button @click="removeMedicine(idx)" class="text-gray-500 hover:text-red-400">
                    <FeatherIcon name="trash-2" class="w-3.5 h-3.5" />
                  </button>
                </div>
                <div class="grid grid-cols-3 gap-1.5 text-[11px]">
                  <input
                    v-model="med.dosage"
                    type="text"
                    placeholder="Dosage (1 tab)"
                    class="bg-gray-900 border border-gray-800 rounded px-2 py-1 text-white focus:outline-none focus:border-amber-500"
                  />
                  <input
                    v-model="med.timing"
                    type="text"
                    placeholder="Timing (After Meals)"
                    class="bg-gray-900 border border-gray-800 rounded px-2 py-1 text-white focus:outline-none focus:border-amber-500"
                  />
                  <input
                    v-model="med.duration"
                    type="text"
                    placeholder="Duration (30 Days)"
                    class="bg-gray-900 border border-gray-800 rounded px-2 py-1 text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>
            </div>

            <!-- Advice / Lifestyle -->
            <div class="bg-gray-950 p-3 rounded-xl border border-gray-800">
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
          <div class="p-3 bg-gray-950 border-t border-gray-800">
            <button
              @click="submitPrescription"
              type="button"
              class="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg"
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

const bookingId = computed(() => route.params.bookingId || 'room_doc_Doc-1');
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
  name: 'Randhir (Self)',
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
  await joinRoom();
});

onUnmounted(async () => {
  clearInterval(timerInterval);
  await agora.leave();
});

async function joinRoom() {
  try {
    const tmpToken = '007eJxTYFiwe6KOlQ8P3zmDf4k5Xx/Ytx7TeWLeHhbxrXvlrMnz1zIqMKQmp1kmWySZJ1tYGJkYp5klJVlaWKQlpqWkGaekJJqYiBi3ZzUEMjJ869nCwAiFID4fQ1F+fm58Sn4yCOsaMjAAAPRjJHU=';
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
