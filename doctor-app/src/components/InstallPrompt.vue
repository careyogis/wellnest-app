<template>
  <!-- Install PWA dialog for Android / Desktop -->
  <Dialog v-model="showDialog">
    <template #body-title>
      <h2 class="text-lg font-bold text-gray-900">{{ __('Install CareYogi Doctor App') }}</h2>
    </template>
    <template #body-content>
      <p class="text-sm text-gray-600 mt-2">
        {{ __('Get the app on your device for fast access, push alerts, and an optimal clinical workspace experience!') }}
      </p>
    </template>
    <template #actions>
      <Button variant="solid" @click="install" class="py-2.5 w-full bg-teal-600 hover:bg-teal-700 text-white font-medium">
        <template #prefix>
          <FeatherIcon name="download" class="w-4 h-4 mr-2" />
        </template>
        {{ __('Install App') }}
      </Button>
    </template>
  </Dialog>

  <!-- iOS Safari installation instructions -->
  <transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-8 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100"
    leave-to-class="transform translate-y-8 opacity-0"
  >
    <div
      v-if="iosInstallMessage"
      class="fixed bottom-4 inset-x-4 max-w-md mx-auto z-50 flex flex-col gap-3 rounded-2xl p-4 bg-white border border-teal-200 shadow-2xl"
    >
      <div class="flex flex-row items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center">
            <FeatherIcon name="download" class="w-4 h-4 text-teal-600" />
          </div>
          <span class="text-sm text-gray-900 font-bold">
            {{ __('Install CareYogi Doctor App') }}
          </span>
        </div>
        <button
          type="button"
          class="text-gray-400 hover:text-gray-600 p-1 rounded-md"
          @click="iosInstallMessage = false"
          aria-label="Close"
        >
          <FeatherIcon name="x" class="h-4 w-4" />
        </button>
      </div>
      <div class="text-xs text-gray-600">
        <div class="flex flex-col gap-2">
          <span>
            {{ __('Install the app on your iPhone or iPad for quick access and a full-screen experience.') }}
          </span>
          <div class="flex items-center gap-1.5 font-medium text-teal-900 bg-teal-50 p-2.5 rounded-xl border border-teal-100">
            <span>{{ __('Tap') }}</span>
            <FeatherIcon name="share" class="h-4 w-4 text-teal-600 inline shrink-0" />
            <span>{{ __('and then select "Add to Home Screen"') }}</span>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Dialog, Button, FeatherIcon } from 'frappe-ui'

const __ = (text) => (typeof window !== 'undefined' && window.__ ? window.__(text) : text)

const deferredPrompt = ref(null)
const showDialog = ref(false)
const iosInstallMessage = ref(false)

const isIos = () => {
  if (typeof window === 'undefined') return false
  const userAgent = window.navigator.userAgent.toLowerCase()
  return /iphone|ipad|ipod/.test(userAgent)
}

const isInStandaloneMode = () => {
  if (typeof window === 'undefined') return false
  return (
    ('standalone' in window.navigator && window.navigator.standalone) ||
    window.matchMedia('(display-mode: standalone)').matches
  )
}

onMounted(() => {
  // Show iOS install message on iOS if not already installed as standalone
  if (isIos() && !isInStandaloneMode()) {
    iosInstallMessage.value = true
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing automatically on mobile
    e.preventDefault()
    // Stash the event so it can be triggered later.
    deferredPrompt.value = e
    if (isIos() && !isInStandaloneMode()) {
      iosInstallMessage.value = true
    } else {
      showDialog.value = true
    }
  })

  window.addEventListener('appinstalled', () => {
    showDialog.value = false
    deferredPrompt.value = null
  })
})

async function install() {
  if (deferredPrompt.value) {
    deferredPrompt.value.prompt()
    const choiceResult = await deferredPrompt.value.userChoice
    if (choiceResult?.outcome === 'accepted') {
      showDialog.value = false
    }
    deferredPrompt.value = null
  }
  showDialog.value = false
}
</script>
