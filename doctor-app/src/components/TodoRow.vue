<template>
  <section class="w-full bg-white border divide-y rounded divide-slate-200 border-slate-200 p-2 mb-2">
    <div class="flex justify-between">
      <div>{{ title }}</div>
      <Checkbox size="md" :checked="true" v-model="checkbox" label="" />
    </div>
  </section>
</template>

<script setup>
import { ref, watch, inject } from 'vue';
import { createResource } from 'frappe-ui';
import { Checkbox } from 'frappe-ui';

const props = defineProps(['dailyRecordId', 'title', 'checked', 'taskId']);

const checkbox = ref(props.checked ? true : false);

const { filterCompletedActivities, dailyEngagementRecord } = inject('tasks');

watch(
  () => checkbox.value,
  (value) => {
    if (value === true) {
      addToDailyEngagement();
    } else {
      removeFromDailyEngagement();
    }
  }
);

async function addToDailyEngagement() {
  try {
    // Make the API request
    const response = createResource({
      url: `/api/method/wellnest.api.addActivityToDailyRecord?dailyRecordId=${props.dailyRecordId}&activityName=${props.title}`,
      auto: true,
    });
    await response.promise;
    dailyEngagementRecord.data.performed_activities = JSON.parse(JSON.stringify(response.data));
    filterCompletedActivities();
  } catch (error) {
    console.error('Failed to send activity completion request:', error);
  }
}

async function removeFromDailyEngagement() {
  try {
    // Make the API request
    const response = createResource({
      url: `/api/method/wellnest.api.removeActivityFromDailyRecord?taskName=${props.taskId}&dailyRecordId=${props.dailyRecordId}`,
      auto: true,
    });
    await response.promise;
    dailyEngagementRecord.data.performed_activities = JSON.parse(JSON.stringify(response.data));
    filterCompletedActivities();
  } catch (error) {
    console.error('Failed to send activity completion request:', error);
  }
}
</script>
