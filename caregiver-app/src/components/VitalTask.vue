<template>
  <div class="mb-3 p-4 rounded-xl shadow border bg-white">
    <div class="flex justify-between items-center">
      <div>
        <!-- Vital name display -->
        <div class="text-lg font-semibold text-gray-800">{{ title }}</div>

        <!-- Last recorded time (if available) -->
        <div class="text-sm text-gray-500" v-if="completionTimeLocal">
          Last recorded: {{ formattedTime }}
        </div>

        <!-- Message for non-recorded vitals -->
        <div class="text-sm text-gray-400" v-else>
          Not recorded yet
        </div>
      </div>

      <!-- Input field to enter new vital reading if not already submitted -->
      <div v-if="!submitted" class="flex items-center">
        <input
          v-model="inputValue"
          type="text"
          placeholder="Enter value"
          class="border p-1 rounded w-24"
        />
        <span class="ml-2 text-gray-500">{{ unit }}</span>
        <button @click="submitVital" class="ml-3 text-blue-500 underline">Save</button>
      </div>

      <!-- If already submitted, show the value with unit -->
      <div v-else class="text-xl font-bold text-blue-600">
        {{ value || inputValue }}
        <span class="text-base font-normal text-gray-500">{{ unit }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { call } from 'frappe-ui'

// Props passed to this component
const props = defineProps({
  title: String,           // Vital name (e.g., "Pulse rate")
  engagementId: String,    // Actual engagement ID (used when saving)
  dailyRecordId: String,   // ID of the Engagement Daily Record
  value: String,           // Previously recorded value
  completionTime: String   // Timestamp of last recorded entry
});

// Two-way bound input and status flag
const inputValue = ref(props.value || '');
const submitted = ref(false);

// Track last recorded time locally and update it after submission
const completionTimeLocal = ref(props.completionTime);

const formattedTime = computed(() => {
  if (!completionTimeLocal.value) return '';
  return new Date(completionTimeLocal.value).toLocaleString();
});

// Map for displaying appropriate units per vital type
const unitMap = {
  "Body temperature": "°F",
  "Pulse rate": "bpm",
  "Heart rate": "bpm",
  "Respiratory rate": "breaths/min",
  "Blood pressure": "mmHg",
  "Oxygen saturation": "%"
};
const unit = computed(() => unitMap[props.title] || '');

// Normalize vital type for backend (e.g., capitalize for validation)
const validTitleMap = {
  "Body temperature": "Body Temperature",
  "Pulse rate": "Pulse Rate",
  "Heart rate": "Heart Rate",
  "Respiratory rate": "Respiratory Rate",
  "Blood pressure": "Blood Pressure",
  "Oxygen saturation": "Oxygen Saturation"
};

// Submit the entered vital value to the backend API
async function submitVital() {
  // Don't proceed if no value is entered
  if (!inputValue.value) return;

  try {
    // Call backend API to save the new vital reading
    // We pass the normalized vital name, the engagement ID, and the value entered by the caregiver
    await call('wellnest.api.submit_vital_reading', {
      engagement: props.engagementId,  // This should be the main engagement ID (not daily record ID)
      vital_type: validTitleMap[props.title] || props.title,  // Convert UI label to valid backend value
      value: inputValue.value  // The actual reading entered by the caregiver
    });

    // Mark the reading as submitted so the input field is hidden and value is shown
    submitted.value = true;

    // Set current time as the "last recorded" timestamp
    // This ensures the UI reflects the update immediately without waiting for API re-fetch
    completionTimeLocal.value = new Date().toISOString();
  } catch (err) {
    // Log error and notify the caregiver if something goes wrong
    console.error("Failed to submit vital:", err);
    alert("Failed to save. Try again.");
  }
}

</script>
