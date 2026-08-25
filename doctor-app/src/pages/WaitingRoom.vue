<template>
  <div class="p-4 md:p-6">
    <!-- Header -->
    <div class="mb-4">
      <h1 class="text-2xl font-bold text-gray-900">
        Join consultation
      </h1>

      <p class="text-sm text-gray-500 mt-1">
        Review the consultation details before joining.
      </p>
    </div>

    <!-- Waiting Room -->
    <div class="max-w-5xl mx-auto bg-white border border-gray-200 rounded-2xl overflow-hidden">
      <div
        class="min-h-[420px] bg-gradient-to-br from-teal-500 to-teal-700
               text-white p-5 md:p-6 flex flex-col"
      >
        <!-- Consultation details -->
        <div>
          <span
            class="inline-flex px-3 py-1 rounded-lg
                   bg-white/90 text-gray-800
                   text-xs font-semibold"
          >
            Waiting room
          </span>

          <h2 class="text-3xl font-bold mt-4">
            {{ consultation.patient.name }}
          </h2>

          <p class="text-lg mt-2">
            {{ consultation.reason }}
          </p>

          <p class="mt-3 text-sm">
            {{ consultation.mode }} consult /
            {{ consultation.time }}
          </p>
        </div>

        <!-- Camera preview -->
        <div class="flex-1 flex items-center justify-center py-6">
          <div
            class="w-full max-w-2xl h-64 md:h-72 rounded-2xl
                   bg-black/20 border border-white/20
                   overflow-hidden flex items-center justify-center"
          >
            <video
              v-if="cameraStream && !isVideoOff"
              ref="videoElement"
              autoplay
              playsinline
              muted
              class="w-full h-full object-cover"
            ></video>

            <div v-else class="text-center">
              <FeatherIcon
                :name="isVideoOff ? 'video-off' : 'video'"
                class="w-10 h-10 mx-auto"
              />

              <p class="text-lg font-semibold mt-3">
                {{ isVideoOff ? 'Camera is off' : 'Camera preview unavailable' }}
              </p>

              <p class="text-sm text-white/80 mt-1">
                {{ statusMessage }}
              </p>
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="text-center mb-4">
          <p class="text-sm text-white/90">
            {{ statusMessage }}
          </p>
        </div>

        <!-- Controls -->
        <div class="flex justify-center items-center gap-3 flex-wrap">

          <!-- Microphone -->
          <button
            type="button"
            class="w-12 h-12 rounded-xl border border-white/40
                   flex items-center justify-center transition"
            :class="
              isMuted
                ? 'bg-red-500/80'
                : 'bg-white/10 hover:bg-white/20'
            "
            :aria-label="isMuted ? 'Unmute microphone' : 'Mute microphone'"
            :title="isMuted ? 'Unmute microphone' : 'Mute microphone'"
            @click="toggleMute"
          >
            <FeatherIcon
              :name="isMuted ? 'mic-off' : 'mic'"
              class="w-5 h-5"
            />
          </button>

          <!-- Camera -->
          <button
            type="button"
            class="w-12 h-12 rounded-xl border border-white/40
                   flex items-center justify-center transition"
            :class="
              isVideoOff
                ? 'bg-red-500/80'
                : 'bg-white/10 hover:bg-white/20'
            "
            :aria-label="isVideoOff ? 'Turn camera on' : 'Turn camera off'"
            :title="isVideoOff ? 'Turn camera on' : 'Turn camera off'"
            @click="toggleVideo"
          >
            <FeatherIcon
              :name="isVideoOff ? 'video-off' : 'video'"
              class="w-5 h-5"
            />
          </button>

          <!-- Screen sharing -->
          <button
            type="button"
            class="w-12 h-12 rounded-xl border border-white/40
                   flex items-center justify-center transition"
            :class="
              isScreenSharing
                ? 'bg-blue-500/80'
                : 'bg-white/10 hover:bg-white/20'
            "
            :aria-label="
              isScreenSharing
                ? 'Stop screen sharing'
                : 'Start screen sharing'
            "
            :title="
              isScreenSharing
                ? 'Stop screen sharing'
                : 'Start screen sharing'
            "
            @click="toggleScreenShare"
          >
            <FeatherIcon
              :name="isScreenSharing ? 'monitor-off' : 'monitor'"
              class="w-5 h-5"
            />
          </button>

          <!-- End consultation -->
          <button
            type="button"
            class="ml-2 px-5 py-3 rounded-xl
                   bg-red-500 text-white font-semibold
                   hover:bg-red-600 transition"
            @click="goBack"
          >
            End consultation
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

const isMuted = ref(false)
const isVideoOff = ref(true)
const isScreenSharing = ref(false)

const cameraStream = ref(null)
const screenStream = ref(null)
const videoElement = ref(null)

const statusMessage = ref(
  'Camera and microphone are currently off.'
)

const consultation = {
  patient: {
    name: 'Asha Mehta',
  },
  reason: 'Review glucose logs and BP readings',
  mode: 'Video',
  time: '10:30 AM',
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    })

    cameraStream.value = stream

    // Start with microphone on when camera is enabled.
    const audioTracks = stream.getAudioTracks()

    audioTracks.forEach((track) => {
      track.enabled = !isMuted.value
    })

    isVideoOff.value = false

    await nextTick()

    if (videoElement.value) {
      videoElement.value.srcObject = stream
    }

    statusMessage.value = 'Camera and microphone are ready.'
  } catch (error) {
    console.error('Camera/microphone access failed:', error)

    statusMessage.value =
      'Camera or microphone access was denied or is unavailable.'
  }
}

function stopCamera() {
  if (!cameraStream.value) {
    return
  }

  cameraStream.value.getTracks().forEach((track) => {
    track.stop()
  })

  cameraStream.value = null
  isVideoOff.value = true

  statusMessage.value = 'Camera is off.'
}

async function toggleVideo() {
  if (isVideoOff.value) {
    await startCamera()
    return
  }

  stopCamera()
}

function toggleMute() {
  isMuted.value = !isMuted.value

  if (!cameraStream.value) {
    statusMessage.value = isMuted.value
      ? 'Microphone is muted.'
      : 'Microphone is ready.'
    return
  }

  cameraStream.value.getAudioTracks().forEach((track) => {
    track.enabled = !isMuted.value
  })

  statusMessage.value = isMuted.value
    ? 'Microphone is muted.'
    : 'Microphone is on.'
}

async function toggleScreenShare() {
  if (isScreenSharing.value) {
    stopScreenShare()
    return
  }

  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: true,
    })

    screenStream.value = stream
    isScreenSharing.value = true
    statusMessage.value = 'Screen sharing is enabled.'

    const videoTrack = stream.getVideoTracks()[0]

    if (videoTrack) {
      videoTrack.onended = () => {
        stopScreenShare()
      }
    }
  } catch (error) {
    console.error('Screen sharing failed:', error)

    statusMessage.value = 'Screen sharing was cancelled.'
  }
}

function stopScreenShare() {
  if (screenStream.value) {
    screenStream.value.getTracks().forEach((track) => {
      track.stop()
    })

    screenStream.value = null
  }

  isScreenSharing.value = false
  statusMessage.value = 'Screen sharing is off.'
}

function goBack() {
  stopCamera()
  stopScreenShare()

  router.push({
    name: 'Consultations',
  })
}

onBeforeUnmount(() => {
  stopCamera()
  stopScreenShare()
})
</script>