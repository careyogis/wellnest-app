<template>
  <div v-if="activityResource.data">
    <CaregiverNavbar title="Daily Tasks" />
    <div class="flex flex-col items-center my-3">
      <Avatar :shape="'circle'" :image="customerRecord.data.image" :label="customerRecord.data.name" size="3xl" />
      <div class="text-xl text-[#070707] font-semibold">
        {{ customerRecord.data.name }}
      </div>
      <div v-if="customerRecord.data.gender || customerRecord.data.custom_age">
        {{ customerRecord.data.gender }}, {{ customerRecord.data.custom_age }}
      </div>
    </div>
    <Tabs class="bro" v-model="state.index" :tabs="state.tabs">
      <template #default="{ tab }">
        <div class="p-3">
          <div>
            <div v-if="state.index === 0">
              <!-- <div class="mb-2 text-xl text-[#070707] font-semibold">Non-Vital Tasks</div> -->
              <TodoRow v-for="task in engagementRecord.data.required_activity" :key="task.name"
                :dailyRecordId="props.dailyRecordId" :title="task.activity" :checked="false" :taskId="task.name" />
              <TodoRow v-for="task in dailyEngagementRecord.data.performed_activities"
                :dailyRecordId="props.dailyRecordId" :title="task.activity" :key="task.name" :checked="true"
                :taskId="task.name" />
              <!-- <div class="mt-8 mb-2 text-xl text-[#070707] font-semibold">Vital Tasks</div> -->
              <!-- <VitalTask v-for="task in vitalTasks.data" :title="task.activity" :dailyRecordId="props.dailyRecordId" :completionTime="task.completion_time" /> -->
            </div>
            <div v-else-if="state.index === 1">
              <div class="flex justify-between items-center w-full">
                <div>
                  <FeatherIcon class="inline-block w-3 -rotate-45 mr-1 stroke-[blue] stroke-1" name="paperclip" />
                  <div class="inline-block my-5 text-blue-500">reading1.png</div>
                </div>
                <div class="text-sm">20 June 2024</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Tabs>
  </div>
</template>

<script setup>
import { Tabs, FeatherIcon, Badge, Avatar } from 'frappe-ui';
import { computed, reactive, ref, provide } from 'vue';
import { createDocumentResource, createResource } from 'frappe-ui';
import CaregiverNavbar from '../components/CaregiverNavbar.vue';
import TodoRow from '../components/TodoRow.vue';
// import VitalTask from '../components/VitalTask.vue';

const props = defineProps({ dailyRecordId: String });

const state = reactive({
  index: 0,
  // Currently only showing Daily Tasks Tab
  tabs: [{ label: 'Daily Tasks' }],
  // tabs: [{ label: 'Daily Tasks' }, { label: 'Assessment' }],
});

const activityResource = reactive({
  data: null,
  loading: false,
})

const customerRecord = reactive({
  data: null,
})

const engagementRecord = reactive({
  data: null,
});
const dailyEngagementRecord = reactive({
  data: null,
});

// const vitalTasks = reactive({
//   data: [],
//   loading: false
// })

function filterCompletedActivities() {
  engagementRecord.data.required_activity = JSON.parse(JSON.stringify(activityResource.data.engagementRecord.required_activity));
  if (dailyEngagementRecord.data.performed_activities) {
    engagementRecord.data.required_activity = engagementRecord.data.required_activity.filter((task) => {
      return !dailyEngagementRecord.data.performed_activities.some((activity) => task.activity === activity.activity);
    });
  }
}

// Initial API call
apiCall();

async function apiCall() {
  try {
    if (!props.dailyRecordId) {
      console.warn('Missing `dailyRecordId` in props.');
      return;
    }

    // Fetch daily task data from Engagement Daily Record
    activityResource.loading = true;
    const activityResourceResponse = createResource({
      url: `/api/method/wellnest.api.activity?dailyRecordId=${props.dailyRecordId}`,
      auto: true,
    });
    activityResource.data = await activityResourceResponse.promise
    activityResource.loading = false;

    dailyEngagementRecord.data = JSON.parse(JSON.stringify(activityResource.data.dailyEngagementRecord));
    customerRecord.data = JSON.parse(JSON.stringify(activityResource.data.customerDoc));
    engagementRecord.data = JSON.parse(JSON.stringify(activityResource.data.engagementRecord));

    // Compare the activities from engagements to that of daily record and show only those that aren't in daily record
    filterCompletedActivities();

    // vitalTasks.data = JSON.parse(JSON.stringify(activityResource.data.vitalTasks));

    // Validate the fetched data
    if (!activityResourceResponse?.data) {
      console.warn('No data available for the provided `EngagementId`.');
    }
    // console.log(vitalTasks.data);
  } catch (error) {
    console.error('API call failed:', error);
    engagementRecord.data = null;
  }
}
provide('tasks', { filterCompletedActivities, dailyEngagementRecord });
</script>
