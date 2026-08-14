<template>
  <div class="p-6 md:p-8">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
      <div>
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-1">Today's Workspace</h2>
        <p class="text-gray-500 text-sm md:text-base">A calm command center for booked consultations, follow-ups, reports, and patient messages.</p>
      </div>

      <div class="flex items-center gap-3">
        <button type="button" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500 text-white text-sm font-semibold hover:bg-amber-600 transition-colors">
          <FeatherIcon name="video" class="w-4 h-4" />
          View bookings
        </button>
        <button type="button" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-amber-400 text-amber-600 text-sm font-semibold hover:bg-amber-50 transition-colors">
          Publish availability
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-500">Today's consultations</span>
          <div class="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
            <FeatherIcon name="video" class="w-4 h-4" />
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-1">0</div>
        <div class="text-xs text-gray-400">No consultations yet</div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-500">Unread messages</span>
          <div class="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
            <FeatherIcon name="message-circle" class="w-4 h-4" />
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-1">0</div>
        <div class="text-xs text-gray-400">No messages yet</div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-500">Reports uploaded</span>
          <div class="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
            <FeatherIcon name="file-text" class="w-4 h-4" />
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-1">0</div>
        <div class="text-xs text-gray-400">No reports yet</div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-500">Monthly earnings</span>
          <div class="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
            <FeatherIcon name="briefcase" class="w-4 h-4" />
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-1">₹0</div>
        <div class="text-xs text-gray-400">No earnings data yet</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div class="lg:col-span-2 bg-white rounded-2xl border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h5 class="text-lg font-bold text-gray-900">What needs attention</h5>
          <RouterLink :to="{ name: 'Consultations' }" class="text-sm font-semibold text-amber-600 hover:underline">View consultations</RouterLink>
        </div>

        <div class="text-center py-10 text-gray-400 text-sm">Nothing needs your attention right now.</div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200 p-6">
        <h5 class="text-lg font-bold text-gray-900 mb-4">Quick actions</h5>

        <div class="grid grid-cols-2 gap-3">
          <button
            v-for="action in quickActions"
            :key="action.label"
            type="button"
            class="flex flex-col items-start gap-2 p-3 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors text-left"
          >
            <FeatherIcon :name="action.icon" class="w-4 h-4 text-amber-500" />
            <span class="text-sm font-medium text-gray-700">{{ action.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 bg-white rounded-2xl border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h5 class="text-lg font-bold text-gray-900">Patient activity</h5>
          <RouterLink :to="{ name: 'Patients' }" class="text-sm font-semibold text-amber-600 hover:underline">All patients</RouterLink>
        </div>

        <div class="text-center py-10 text-gray-400 text-sm">No recent patient activity.</div>
      </div>

      <div class="bg-amber-50 rounded-2xl border border-amber-100 p-6">
        <div class="flex items-center justify-between mb-2">
          <h5 class="text-lg font-bold text-gray-900">CareYogi AI</h5>
          <button type="button" class="px-3 py-1 rounded-lg border border-amber-300 text-amber-700 text-xs font-semibold hover:bg-amber-100 transition-colors">
            Open
          </button>
        </div>
        <p class="text-sm text-gray-500 mb-4">Prototype assistant panel for summarizing history, drafting consultation summaries, OCR review, and follow-up suggestions.</p>

        <div class="space-y-2">
          <div class="px-3 py-2 rounded-lg bg-white border border-amber-100 text-sm font-medium text-gray-700">Summarize patient history</div>
          <div class="px-3 py-2 rounded-lg bg-white border border-amber-100 text-sm font-medium text-gray-700">Generate post-consult summary</div>
          <div class="px-3 py-2 rounded-lg bg-white border border-amber-100 text-sm font-medium text-gray-700">Suggest medication reminders</div>
        </div>
      </div>
    </div>

    <div class="text-center text-gray-400 text-xs mt-10 pb-6">CareYogi Doctor App v1.0 prototype. Designed for doctor feedback, not clinical production use.</div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui';
import { RouterLink } from 'vue-router';

const quickActions = [
  { label: 'Join room', icon: 'video' },
  { label: 'Message patient', icon: 'send' },
  { label: 'Refer patient', icon: 'share-2' },
  { label: 'Availability', icon: 'calendar' },
  { label: 'Review report', icon: 'upload' },
  { label: 'Payouts', icon: 'briefcase' },
];
</script>