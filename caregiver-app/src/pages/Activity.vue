<template>
  <div v-if="dailyEngagementRecord.data">
    <CaregiverNavbar title="Daily Tasks" />
    <div class="flex flex-col items-center my-3">
      <Avatar :shape="'circle'" :image="dailyEngagementRecord.data.customerDoc.image"
        :label="dailyEngagementRecord.data.customerDoc.name" size="3xl" />
      <div class="text-xl text-[#070707] font-semibold">
        {{ dailyEngagementRecord.data.customerDoc.name }}
      </div>
      <div v-if="dailyEngagementRecord.data.customerDoc.gender || dailyEngagementRecord.data.customerDoc.custom_age">
        {{ dailyEngagementRecord.data.customerDoc.gender }}, {{ dailyEngagementRecord.data.customerDoc.custom_age }}
      </div>
    </div>
    <Tabs class="bro" v-model="state.index" :tabs="state.tabs">
      <template #default="{ tab }">
        <div class="p-3">
          <div>
            <div v-if="state.index === 0">
              <TodoRow v-for="task in taskResource.data" :key="task.name" :dailyRecordId="props.dailyRecordId"
                :title="task.activity" :checked="false" :taskId="task.name" />
              <TodoRow v-for="task in dailyEngagementRecord.data.engagementRecord.performed_activities"
                :dailyRecordId="props.dailyRecordId" :title="task.activity" :key="task.name" :checked="true"
                :taskId="task.name" />
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

const props = defineProps({ dailyRecordId: String });

const state = reactive({
  index: 0,
  // Currently only showing Daily Tasks Tab
  tabs: [{ label: 'Daily Tasks' }],
  // tabs: [{ label: 'Daily Tasks' }, { label: 'Assessment' }],
});

const taskResource = reactive({
  data: null,
  loading: false,
});
const dailyEngagementRecord = reactive({
  data: null,
  loading: false,
});

let taskResourceResponse;
let dailyEngagementRecordResponse;

function filterCompletedActivities() {
  taskResource.data = taskResourceResponse.data;
  if (dailyEngagementRecord.data.engagementRecord.performed_activities) {
    taskResource.data = taskResource.data.filter((task) => {
      return !dailyEngagementRecord.data.engagementRecord.performed_activities.some((activity) => task.activity === activity.activity);
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
    dailyEngagementRecord.loading = true;
    dailyEngagementRecordResponse = createResource({
      url: `/api/method/wellnest.api.activity?dailyRecordId=${props.dailyRecordId}`,
      auto: true,
    });
    dailyEngagementRecord.data = await dailyEngagementRecordResponse.promise;
    dailyEngagementRecord.loading = false;

    // Fetch daily task data from engagements
    taskResource.loading = true;
    taskResourceResponse = createResource({
      url: `/api/method/wellnest.api.fetchEngagementTasks?engagementId=${dailyEngagementRecord.data.engagementRecord.engagement}`,
      auto: true,
    });
    taskResource.data = await taskResourceResponse.promise;
    taskResource.loading = false;

    // Compare the engagements from engagements to that of daily record and show only those that aren't in daily record
    filterCompletedActivities();

    // Validate the fetched data
    if (!taskResource?.data) {
      console.warn('No data available for the provided `EngagementId`.');
    }
  } catch (error) {
    console.error('API call failed:', error);
    taskResource = null;
  }
}
provide('tasks', { filterCompletedActivities, dailyEngagementRecord });
</script>
