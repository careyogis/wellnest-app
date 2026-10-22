
<template>
  <div class="p-5 md:p-8">
    <!-- Page header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Patients</h1>
        <p class="mt-1 text-sm text-gray-500">
          Search, filter, and manage patients connected through your consultations.
        </p>
      </div>

      <button
        type="button"
        @click="router.push({ name: 'Messages' })"
        class="px-4 py-2 rounded-lg border border-amber-400 text-amber-700 text-sm font-semibold hover:bg-amber-50"
      >
        <FeatherIcon name="message-circle" class="w-4 h-4 inline mr-1" />
        Open messages
      </button>
    </div>

    <!-- Search and filters -->
    <div class="bg-white border border-gray-200 rounded-xl p-3 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search by name"
          class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-300"
        />

        <select
          v-model="sortBy"
          class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-white"
        >
          <option value="upcoming">Sort: upcoming consultation</option>
          <option value="name">Sort: patient name</option>
        </select>
      </div>
    </div>

    <!-- Results summary -->
    <div class="flex items-center justify-between mb-4">
      <p class="text-sm text-gray-500">
        {{ filteredPatients.length }} patients
      </p>
    </div>

    <!-- Loading state -->
    <div
       v-if="patientsResource.loading"
      class="bg-white border border-gray-200 rounded-xl p-10 text-center text-sm text-gray-500"
    >
    Loading patients...
    </div>

    <!-- Patient cards -->
    <div  v-else-if="filteredPatients.length"
          class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
    >
      <article
        v-for="patient in filteredPatients"
        :key="patient.id"
        class="bg-white border border-gray-200 rounded-xl p-4 hover:border-amber-300 transition-colors"
      >
        <div class="flex items-start justify-between gap-3 mb-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-11 h-11 shrink-0 rounded-full bg-gradient-to-br from-amber-400 to-emerald-600 text-white flex items-center justify-center font-bold">
              {{ initials(patient.name) }}
            </div>

            <div class="min-w-0">
              <h2 class="font-semibold text-gray-900 truncate">
                {{ patient.name }}
              </h2>
              <p class="text-xs text-gray-500 mt-1">
                {{ patient.age != null ? patient.age + ' yrs' : 'Age unavailable' }}
                <span v-if="patient.gender"> · {{ patient.gender }}</span>
              </p>
            </div>
          </div>

          <span
            v-if="patient.risk"
            class="shrink-0 px-2 py-1 rounded text-xs font-semibold"
            :class="riskClass(patient.risk)"
          >
            {{ patient.risk }}
          </span>
        </div>

        <p class="text-sm text-gray-700 min-h-10 mb-3">
          {{ patient.conditions || 'No condition details available' }}
        </p>

        <div class="flex flex-wrap gap-2 mb-4 text-xs">
          <span class="px-2 py-1 rounded bg-gray-100 text-gray-600">
            Last: {{ patient.lastVisit || 'Not available' }}
          </span>
          <span class="px-2 py-1 rounded bg-gray-100 text-gray-600">
            Next: {{ patient.nextVisit || 'Not scheduled' }}
          </span>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="openRecord(patient)"
            class="px-3 py-2 rounded-lg bg-amber-500 text-white text-sm font-semibold hover:bg-amber-600"
          >
            Open record
          </button>

          <button
            v-if="patient.prescriptionWorkflowState === 'Complete'"
            type="button"
            @click="messagePatient(patient)"
            class="px-3 py-2 rounded-lg border border-amber-400 text-amber-700 text-sm font-semibold hover:bg-amber-50"
          >
            Message
          </button>
        </div>
      </article>
    </div>

    <!-- Empty state -->
    <div
      v-else
      class="bg-white border border-gray-200 rounded-xl p-10 text-center"
    >
      <FeatherIcon name="users" class="w-9 h-9 mx-auto text-gray-300 mb-3" />
      <h2 class="font-semibold text-gray-800">No patients found</h2>
      <p class="text-sm text-gray-500 mt-1">
        Try changing your search or filters.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';
import { useRouter } from 'vue-router';

const router = useRouter();

const searchQuery = ref('');
const sortBy = ref('upcoming');

// Temporary UI data only.
// Replace this array with authorized backend patient data.

const patientsResource = createResource({
  url: 'wellnest.wellnest.doctype.patient_appointment.patient_appointment.get_doctor_patients',
  auto: true,
});

const patients = computed(() => patientsResource.data || [])

const filteredPatients = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();

const results = patients.value.filter((patient) => {
  return String(patient.name || '')
    .toLowerCase()
    .includes(query);
});

  return results.sort((a, b) => {
    if (sortBy.value === 'name') {
      return (a.name || '').localeCompare(b.name || '');
    }

    return (a.nextVisitDate || '9999-12-31')
      .localeCompare(b.nextVisitDate || '9999-12-31');
  });
});

function initials(name) {
  return String(name || 'P')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();
}

function riskClass(risk) {
  return {
    High: 'bg-red-100 text-red-700',
    Medium: 'bg-amber-100 text-amber-700',
    Low: 'bg-emerald-100 text-emerald-700',
  }[risk] || 'bg-gray-100 text-gray-600';
}

function resetFilters() {
  searchQuery.value = '';
  selectedRisk.value = 'All';
  selectedGender.value = 'All';
  sortBy.value = 'upcoming';
}


function openRecord(patient) {
  router.push({
    name: 'PatientDetails',
    query: {
      patient: patient.id,
      appointment: patient.appointmentId,
    },
  }).catch((error) => {
    if (error?.name !== 'NavigationDuplicated') {
      console.error('Unable to open patient details:', error);
    }
  });
}

function messagePatient(patient) {
  router.push({
    name: 'Messages',
    query: {
      patient: patient.id,
    },
  });
}
</script>
