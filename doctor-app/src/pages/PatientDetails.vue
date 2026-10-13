<template>
  <div class="p-5 md:p-8">
    <!-- Header -->
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">
          {{ patient.name }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          Longitudinal care record aligned with the currently selected consultation workspace.
        </p>
      </div>

      <div class="flex gap-2">
        <button class="rounded-lg border border-amber-400 px-4 py-2 text-sm font-semibold text-amber-700">
          Message
        </button>
        <button class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white">
          Open booked consult
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-5 xl:grid-cols-[0.8fr_1.8fr]">
      <!-- Left column -->
      <div class="space-y-5">
        <section class="rounded-xl border border-gray-200 bg-white p-5">
          <div class="text-center">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-emerald-600 text-xl font-bold text-white">
              {{ initials(patient.name) }}
            </div>
            <h2 class="mt-3 text-xl font-semibold">{{ patient.name }}</h2>
            <p class="mt-2 text-sm text-gray-500">
              {{ patient.age }} yrs · {{ patient.gender }} · {{ patient.location }}
            </p>
            <span class="mt-4 inline-block rounded-md bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
              {{ patient.risk }}
            </span>
          </div>

          <div class="my-5 border-t"></div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500">Adherence</p>
              <p class="font-semibold">{{ patient.adherence }}%</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Next visit</p>
              <p class="font-semibold">{{ patient.nextVisit }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-xl border border-gray-200 bg-white p-5">
          <h2 class="text-lg font-semibold">Emergency contact</h2>
          <p class="mt-3 text-sm">
            <strong>{{ patient.emergencyContact }}</strong>,
            {{ patient.emergencyRelationship }}
          </p>
          <p class="mt-2 text-sm text-gray-500">{{ patient.emergencyPhone }}</p>
        </section>

        <section class="rounded-xl border border-gray-200 bg-white p-5">
          <h2 class="text-lg font-semibold">Current consult linkage</h2>
          <div class="mt-3 rounded-lg border bg-gray-50 p-4">
            <p class="font-semibold">{{ patient.consultationReason }}</p>
            <p class="mt-2 text-sm text-gray-500">{{ patient.consultationType }}</p>
            <p class="mt-2 text-sm text-gray-500">{{ patient.consultationDate }}</p>
          </div>
        </section>
      </div>

      <!-- Right column -->
      <div class="min-w-0">
        <div class="mb-4 flex flex-wrap gap-1 rounded-xl bg-gray-100 p-2">
          <button
            v-for="tab in tabs"
            :key="tab"
            @click="activeTab = tab"
            class="rounded-lg px-3 py-2 text-sm font-semibold"
            :class="activeTab === tab
              ? 'bg-white text-amber-600 shadow-sm'
              : 'text-gray-600 hover:bg-white'"
          >
            {{ tab }}
          </button>
        </div>

        <section class="min-h-64 rounded-xl border border-gray-200 bg-white p-5 md:p-6">
          <h2 class="mb-5 text-lg font-semibold">{{ activeTab }}</h2>

          <div v-if="activeTab === 'Timeline'" class="space-y-6">
            <div
              v-for="(item, index) in timeline"
              :key="index"
              class="relative border-l-2 border-gray-200 pb-1 pl-5"
            >
              <span class="absolute -left-[7px] top-1 h-3 w-3 rounded-full border-2 border-white bg-amber-400"></span>
              <p class="font-semibold">{{ item.title }}</p>
              <p class="mt-1 text-sm text-gray-500">{{ item.description }}</p>
            </div>
          </div>

          <p v-else class="text-sm text-gray-500">
            {{ activeTab }} content will be added in a future implementation.
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const activeTab = ref('Timeline');

const tabs = [
  'Timeline',
  'Conditions',
  'Medications',
  'Vitals',
  'Lab Reports',
  'Prescriptions',
  'Notes',
  'Care Plans',
  'Files',
];

const demoPatient = {
  id: 'asha-mehta-2',
  name: 'Asha Mehta',
  age: 58,
  gender: 'Female',
  location: 'New Delhi',
  risk: 'High risk',
  adherence: 78,
  nextVisit: '23 Jul 2026',
  emergencyContact: 'Vikram Mehta',
  emergencyRelationship: 'spouse',
  emergencyPhone: '+91 98112 44008',
  consultationReason: 'Review glucose logs and BP readings',
  consultationType: 'Video consultation',
  consultationDate: '23 Jul 2026',
};

const patient = computed(() => ({
  ...demoPatient,
  id: String(route.query.patient || demoPatient.id),
}));

const timeline = [
  {
    title: '23 Jul 2026',
    description: 'Video consultation selected in doctor workspace. Reason: Review glucose logs and BP readings.',
  },
  {
    title: 'Draft auto-saved 2 min ago',
    description: 'Digital draft: Doctor is writing directly in the app during the live consultation.',
  },
  {
    title: 'Today, 10:30 AM',
    description: 'HbA1c and lipid profile needs review.',
  },
  {
    title: 'Care plan',
    description: 'Upload fasting glucose for 7 days and review over video in 2 weeks.',
  },
];

function initials(name) {
  return String(name || 'P')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();
}
</script>