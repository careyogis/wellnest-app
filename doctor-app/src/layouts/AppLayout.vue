<template>
  <div class="flex min-h-screen bg-[#f5f7fb]">
    <div v-if="sidebarOpen" class="fixed inset-0 bg-black/40 z-30 md:hidden" @click="closeSidebar"></div>
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-40 w-52 shrink-0 bg-white border-r border-gray-200 flex flex-col transform transition-transform duration-300 ease-in-out md:z-auto md:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex items-center justify-center px-5 py-6 border-b border-gray-100">
        <img :src="logoUrl" alt="CareYogi" class="w-full max-w-[140px] h-auto object-contain" />
      </div>

      <nav class="flex-1 overflow-y-auto px-3 py-4">
        <div class="text-[11px] font-semibold text-gray-400 tracking-wide px-3 mb-2">WORKSPACE</div>

        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="{ name: item.name }"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium mb-1 transition-colors"
          :class="isActive(item.name) ? 'bg-amber-50 text-amber-600' : 'text-gray-600 hover:bg-gray-50'"
          @click="closeSidebar"
        >
          <FeatherIcon :name="item.icon" class="w-4 h-4" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- PWA Install Button -->
      <div v-if="canInstall" class="px-3 pb-2">
        <button
          type="button"
          @click="installApp"
          class="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-teal-600 text-white text-xs font-semibold hover:bg-teal-700 transition-colors shadow-sm"
        >
          <FeatherIcon name="download" class="w-4 h-4" />
          <span>Install Doctor App</span>
        </button>
      </div>

      <div class="m-3 p-4 rounded-xl bg-amber-50 border border-amber-100">
        <div class="flex items-center gap-2 mb-1">
          <FeatherIcon name="zap" class="w-4 h-4 text-amber-600" />
          <span class="text-sm font-bold text-gray-900">CareYogi AI</span>
        </div>
        <p class="text-xs text-gray-500 mb-3">Summaries, OCR, follow-up drafts, and care nudges.</p>
        <button type="button" class="w-full text-center px-3 py-2 rounded-lg border border-amber-300 text-amber-700 text-xs font-semibold hover:bg-amber-100 transition-colors">Open AI panel</button>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col min-w-0 md:ml-52">
      <header class="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
        <div class="flex items-center gap-3">
          <button type="button" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 md:hidden" aria-label="Toggle menu" @click="toggleSidebar">
            <FeatherIcon name="menu" class="w-5 h-5" />
          </button>
          <div>
            <div class="text-sm font-bold text-gray-900 leading-tight">Doctor Workspace</div>
            <div class="text-xs text-gray-400 leading-tight">Continuity of care after discharge</div>
          </div>
        </div>

        <div class="flex items-center gap-4">
         <div class="relative">
  <button
    type="button"
    class="relative p-2 rounded-lg hover:bg-gray-100 text-gray-500"
    aria-label="Notifications"
    aria-haspopup="true"
    :aria-expanded="notificationsOpen"
    @click="toggleNotifications"
  >
    <FeatherIcon name="bell" class="w-5 h-5" />
    <span
      v-if="notifications.length"
      class="absolute -top-1 -right-1 min-w-4 h-4 px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center"
    >
    {{ notifications.length > 99 ? '99+' : notifications.length }}
    </span>
  </button>

  <div
    v-if="notificationsOpen"
    class="absolute right-0 top-full mt-2 w-80 max-w-[calc(100vw-2rem)] bg-white rounded-xl border border-gray-200 shadow-lg z-50"
  >
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
      <h3 class="text-sm font-semibold text-gray-900">Notifications</h3>
      <button
        type="button"
        class="text-xs text-gray-500 hover:text-gray-800"
        @click="notificationsOpen = false"
      >
        Close
      </button>
    </div>

    <div class="max-h-80 overflow-y-auto">
      <div v-if="notificationsLoading" class="px-4 py-6 text-center text-sm text-gray-500">
        Loading notifications...
      </div>

      <div v-else-if="notificationsError" class="px-4 py-6 text-center text-sm text-red-600">
        {{ notificationsError }}
        <button
          type="button"
          class="block mx-auto mt-2 text-teal-700 font-medium"
          @click="loadNotifications"
        >
          Try again
        </button>
      </div>

      <div v-else-if="!notifications.length" class="px-4 py-8 text-center">
        <FeatherIcon name="bell" class="w-6 h-6 mx-auto mb-2 text-gray-300" />
        <p class="text-sm text-gray-500">No new notifications</p>
      </div>

      <div
        v-for="notification in notifications"
        :key="notification.name"
       type="button"
  class="block w-full px-4 py-3 border-b border-gray-100 last:border-b-0 text-left hover:bg-gray-50 transition-colors"
  @click="openAppointment(notification)"
      >
        <p class="text-sm font-medium text-gray-800">
          New appointment
        </p>
        <p class="mt-1 text-sm text-gray-600">
          {{ notification.patient_name }}
        </p>
        <p class="mt-1 text-xs text-gray-400">
          {{ formatNotificationDate(notification.scheduled_time) }}
        </p>
      </div>
    </div>
  </div>
</div>

          <RouterLink :to="{ name: 'Profile' }" class="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div class="w-9 h-9 rounded-full bg-teal-100 text-teal-700 font-bold flex items-center justify-center text-sm overflow-hidden shrink-0">
              <img v-if="doctorPhoto" :src="doctorPhoto" class="w-full h-full object-cover" alt="Profile photo" />
              <span v-else>{{ doctorInitials }}</span>
            </div>
            <div class="hidden sm:block">
              <div class="text-sm font-semibold text-gray-900 leading-tight">{{ doctorName }}</div>
              <div class="text-xs text-gray-400 leading-tight">{{ doctorSpecialty || '\u00A0' }}</div>
            </div>
          </RouterLink>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter, RouterLink } from 'vue-router';
import { profileData } from '@/data/doctorProfile';
import logoUrl from '@/assets/images/logo-01.png';

const doctorName = computed(() => profileData.data?.doctor?.full_name?.trim() || 'Doctor');
const doctorSpecialty = computed(() => profileData.data?.doctor?.doctor_type || '');
const doctorPhoto = computed(() => profileData.data?.doctor?.photo || '');
const doctorInitials = computed(() => {
  const first = profileData.data?.doctor?.first_name?.charAt(0) || '';
  const last = profileData.data?.doctor?.last_name?.charAt(0) || '';
  return first + last || 'DR';
});
import { FeatherIcon } from 'frappe-ui';

const route = useRoute();
const router = useRouter();
const sidebarOpen = ref(false);
const deferredPrompt = ref(null);
const canInstall = ref(false);
const notificationsOpen = ref(false);
const notifications = ref([]);
const notificationsLoading = ref(false);
const notificationsError = ref('');

async function loadNotifications() {
  notificationsLoading.value = true;
  notificationsError.value = '';

  try {
    const response = await fetch(
      '/api/method/wellnest.api.notifications.get_doctor_appointment_notifications',
      {
        credentials: 'include',
        headers: {
          Accept: 'application/json',
        },
      },
    );

    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }

    const result = await response.json();

    if (result.exc) {
      throw new Error('Unable to load notifications.');
    }

    notifications.value = Array.isArray(result.message)
      ? result.message
      : [];
  } catch (error) {
    console.error('Failed to load doctor notifications:', error);
    notificationsError.value = 'Could not load notifications.';
  } finally {
    notificationsLoading.value = false;
  }
}

function toggleNotifications() {
  notificationsOpen.value = !notificationsOpen.value;

  if (notificationsOpen.value) {
    loadNotifications();
  }
}

function formatNotificationDate(value) {
  if (!value) return 'Appointment time unavailable';

  const date = new Date(value.replace(' ', 'T'));

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString([], {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

function openAppointment(notification) {
  notificationsOpen.value = false;

  router.push({
     name: 'Consultations',
    query: {
      status: 'Upcoming',
      appointment: notification.name,
       _notification: Date.now().toString(),
    },
  });
}

let notificationRefreshInterval;

onMounted(() => {
  loadNotifications();

  notificationRefreshInterval = window.setInterval(() => {
    loadNotifications();
  }, 30000);

  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  window.addEventListener('appinstalled', handleAppInstalled);
});

function handleBeforeInstallPrompt(e) {
  e.preventDefault();
  deferredPrompt.value = e;
  canInstall.value = true;
}

function handleAppInstalled() {
  canInstall.value = false;
  deferredPrompt.value = null;
}

onUnmounted(() => {
  window.clearInterval(notificationRefreshInterval);
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  window.removeEventListener('appinstalled', handleAppInstalled);
});

async function installApp() {
  if (!deferredPrompt.value) return;
  deferredPrompt.value.prompt();
  const choiceResult = await deferredPrompt.value.userChoice;
  if (choiceResult?.outcome === 'accepted') {
    canInstall.value = false;
  }
  deferredPrompt.value = null;
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar() {
  sidebarOpen.value = false;
}

const navItems = [
  { name: 'Dashboard', label: 'Dashboard', icon: 'grid' },
  { name: 'Patients', label: 'Patients', icon: 'users' },
  { name: 'Schedule', label: 'Schedule', icon: 'calendar' },
  { name: 'Consultations', label: 'Consultations', icon: 'video' },
  { name: 'Messages', label: 'Messages', icon: 'message-circle' },
  { name: 'Referrals', label: 'Referrals', icon: 'share-2' },
  { name: 'Earnings', label: 'Earnings', icon: 'briefcase' },
  { name: 'Notifications', label: 'Notifications', icon: 'bell' },
  { name: 'Profile', label: 'Profile', icon: 'user' },
  { name: 'Settings', label: 'Settings', icon: 'settings' },
];

function isActive(name) {
  return route.name === name;
}
</script>
