<template>
  <div class="flex min-h-screen bg-[#f5f7fb]">
    <div v-if="sidebarOpen" class="fixed inset-0 bg-black/40 z-30 md:hidden" @click="closeSidebar"></div>
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-40 w-52 shrink-0 bg-white border-r border-gray-200 flex flex-col transform transition-transform duration-300 ease-in-out md:relative md:z-auto md:translate-x-0"
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
    <div class="flex-1 flex flex-col min-w-0">
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
          <button type="button" class="relative p-2 rounded-lg hover:bg-gray-100 text-gray-500" aria-label="Notifications">
            <FeatherIcon name="bell" class="w-5 h-5" />
          </button>

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
import { computed, ref } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
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
const sidebarOpen = ref(false);

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
