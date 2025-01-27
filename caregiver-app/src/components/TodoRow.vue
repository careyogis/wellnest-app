<template>
  <section class="w-full bg-white border divide-y rounded divide-slate-200 border-slate-200 p-2 mb-2">
    <div class="flex justify-between">
      <div>{{ title }}</div>
      <!-- <div v-if="props.checkbox == true"> -->
      <div v-if="props.checkbox">
        <Checkbox size="xl" :value="false" v-model="checkbox" label="" />
      </div>
      <div v-else class="ml-1">✔</div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch, inject } from 'vue';
import { createResource } from 'frappe-ui';
import { Checkbox } from 'frappe-ui';

const props = defineProps(['dailyRecordId', 'title', 'checkbox']);

const checkbox = ref(false);

// const { apiCall, dailyRecordId, taskResource, dailyEngagementRecord } = inject('tasks');
const { apiCall, filterCompletedActivities, taskResource, dailyEngagementRecord } = inject('tasks');

watch(
  () => checkbox.value,
  (value) => {
    if (value === true) {
      sendRequest();
    }
  }
);

async function sendRequest() {
  try {
    // Make the API request
    const response = createResource({
      url: `/api/method/wellnest.api.addActivityToDailyRecord?dailyRecordId=${props.dailyRecordId}&activity=${props.title}&completion_time=default`,
      auto: true,
    });
    await response.promise;
    // Manually adding it to the local memory to lessen server calls -
    dailyEngagementRecord.data.engagementRecord.performed_activities.push({ activity: props.title })
    filterCompletedActivities();
  } catch (error) {
    console.error('Failed to send activity completion request:', error);
  }
}
</script>
