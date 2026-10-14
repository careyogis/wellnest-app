
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
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search by name, condition, phone"
          class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-300"
        />

        <select
          v-model="selectedRisk"
          class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-white"
        >
          <option value="All">All risk levels</option>
          <option value="High">High risk</option>
          <option value="Medium">Medium risk</option>
          <option value="Low">Low risk</option>
        </select>

        <select
          v-model="sortBy"
          class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-white"
        >
          <option value="upcoming">Sort: upcoming consultation</option>
          <option value="name">Sort: patient name</option>
          <option value="age">Sort: age</option>
        </select>

        <button
          type="button"
          @click="showMoreFilters = !showMoreFilters"
          class="px-3 py-2.5 border border-amber-400 text-amber-700 rounded-lg text-sm font-semibold hover:bg-amber-50"
        >
          {{ showMoreFilters ? 'Hide filters' : 'More filters' }}
        </button>
      </div>

      <div v-if="showMoreFilters" class="mt-3 pt-3 border-t border-gray-100">
        <label class="text-sm text-gray-600">
          Gender
          <select
            v-model="selectedGender"
            class="ml-2 px-3 py-2 border border-gray-200 rounded-lg bg-white"
          >
            <option value="All">All genders</option>
            <option value="Female">Female</option>
            <option value="Male">Male</option>
            <option value="Other">Other</option>
          </select>
        </label>
        <button
          type="button"
          @click="resetFilters"
          class="ml-3 text-sm text-amber-700 font-semibold hover:underline"
        >
          Reset filters
        </button>
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

        <div class="mb-4">
          <div class="flex items-center justify-between text-xs text-gray-500 mb-2">
            <span>Medication adherence</span>
            <span>Not available</span>
          </div>
          <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-full w-0"></div>
          </div>
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
      <button
        type="button"
        @click="resetFilters"
        class="mt-4 text-sm font-semibold text-amber-700 hover:underline"
      >
        Clear filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';
import { useRouter } from 'vue-router';

const router = useRouter();

const searchQuery = ref('');
const selectedRisk = ref('All');
const selectedGender = ref('All');
const sortBy = ref('upcoming');
const showMoreFilters = ref(false);

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
    const matchesSearch = [
      patient.name,
      patient.phone,
      patient.conditions,
    ].some((value) => String(value || '').toLowerCase().includes(query));

    const matchesRisk =
      selectedRisk.value === 'All' ||
      patient.risk === selectedRisk.value;

    const matchesGender =
      selectedGender.value === 'All' ||
      patient.gender === selectedGender.value;

    return matchesSearch && matchesRisk && matchesGender;
  });

  return results.sort((a, b) => {
    if (sortBy.value === 'name') {
      return a.name.localeCompare(b.name);
    }

    if (sortBy.value === 'age') {
      return (b.age ?? -1) - (a.age ?? -1);
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
  // Connect this to Khushboo's confirmed Patient Details route.
  // Keep the patient identifier available for the integration.
  router.push({
    name: 'PatientDetails',
    query: { patient: patient.id },
  }).catch((error) => {
    if (error?.name !== 'NavigationDuplicated') {
      console.info('Patient Details route is not integrated yet.');
    }
  });
}

function messagePatient(patient) {
  // Patient chat currently requires an appointment identifier.
  // Wire this after matching the patient to an authorized appointment.
  console.info('Patient messaging integration pending:', patient.id);
}
</script>
