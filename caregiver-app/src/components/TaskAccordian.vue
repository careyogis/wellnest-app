<template>
  <!-- Component: Outline accordion -->
  <section class="w-full bg-white border divide-y rounded divide-slate-200 border-slate-200">
    <details class="p-3 group" closed>
      <summary
        class="[&::-webkit-details-marker]:hidden flex justify-between items-center relative font-medium list-none cursor-pointer text-slate-700 focus-visible:outline-none transition-colors duration-300 group-hover:text-slate-900"
      >
        <div class="order-2 text-[#070707] font-semibold text-center">{{ title }}</div>
        <div class="order-3 flex justify-between items-center">
          <div>
            <FeatherIcon class="w-6 mr-1 stroke-[#78abaf] stroke-2" name="clock" />
          </div>
          <div v-if="prescribedTime" class="text-[#070707] font-semibold">
            <!-- {{ prescribedTime.slice(0, 5) }} -->
            {{ formattedPrescribedTime.slice(0, 5) }}
          </div>
        </div>
        <FeatherIcon class="transition duration-300 stroke-slate-700 group-open:rotate-90 w-5 stroke-[#070707] stroke-2" name="chevron-right" />
      </summary>
      <div class="mt-4 px-7 text-slate-500">
        <div class="text-[#070707] font-semibold">Activity Data (Optional)</div>
        <div class="flex">
          <TextInput :type="'text'" size="lg" variant="outline" placeholder="" v-model="activityData" />
        </div>
        <br />
        <div class="text-[#070707] font-semibold">Completion Time</div>
        <div class="flex">
          <TextInput :type="'time'" size="lg" variant="outline" placeholder="" :value="currentReactiveTime" v-model="taskCompletionTime" />
        </div>
        <br />
        <div v-if="taskProof">
          <FeatherIcon class="inline-block w-3 -rotate-45 mr-1 stroke-[blue] stroke-1" name="paperclip" />
          <a class="inline-block my-5 text-blue-500" :href="taskProof.data || taskProof">Uploaded Image</a>
        </div>
        <div class="text-[#070707] font-semibold">Notes:</div>
        <div>{{ notes }}</div>
        <FileUploader class="mt-5" :fileTypes="['image/*']" @success="onSuccess">
          <template #default="{ file, uploading, progress, uploaded, message, error, total, success, openFileSelector }">
            <button class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1 disabled:border-gray-200" @click="openFileSelector" :loading="updloading" :disabled="checkedOut">
              {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
            </button>
          </template>
        </FileUploader>

        <div v-if="completionTime" class="flex justify-between items-center">
          <button class="text-xl font-medium border-2 border-gray-500 rounded w-2/3 py-2 mb-2 disabled:border-gray-200" :disabled="checkedOut" @click="sendRequest">Update</button>
          <div class="order-3 flex justify-between items-center">
            <FeatherIcon class="w-6 mr-1 stroke-[#78abaf] stroke-2" name="clock" />
            <div class="text-[#070707] font-semibold">
              {{ completionTime }}
            </div>
          </div>
        </div>
        <button v-else class="text-xl font-medium border-2 border-gray-500 rounded w-2/3 py-2 mb-2 disabled:border-gray-200" :disabled="checkedOut" @click="sendRequest">Mark as Completed</button>
      </div>
    </details>
  </section>
  <!-- End Outlined accordion -->
</template>

<script setup>
import { reactive, ref } from 'vue';
import { TextInput, FileUploader, Button, FeatherIcon } from 'frappe-ui';
import { createResource, createListResource, createDocumentResource } from 'frappe-ui';
import { getCurrentFormattedTime } from '../utils';

const props = defineProps(['title', 'id', 'engagementId', 'taskName', 'proof', 'taskResource', 'prescribedTime', 'notes', 'completionDateTime', 'checkedOut']);

const activityData = ref();
const taskCompletionTime = ref();
let activityCompletionResponse = null;
let formattedPrescribedTime = props.prescribedTime[4] === ':' ? '0' + props.prescribedTime : props.prescribedTime;
let completionTime = props.completionDateTime ? ref(props.completionDateTime.slice(10, 16)) : ref(null);
let taskProof = ref(props.proof || null);

const currentReactiveTime = ref(getCurrentFormattedTime);
const updateClock = () => {
  currentReactiveTime.value = getCurrentFormattedTime();
};

setInterval(() => {
  if (!taskCompletionTime.value) {
    updateClock();
  } else {
    clearInterval(updateClock);
    currentReactiveTime.value = taskCompletionTime.value;
  }
}, 1000);

async function sendRequest() {
  try {
    // Validate required data before making the API call
    // if (!props.taskName || !inputField.value) {
    if (!props.taskName) {
      console.warn('Missing required `taskName` or input field data.');
      return;
    }

    // Make the API request
    activityCompletionResponse = createResource({
      url: `/api/method/wellnest.api.setActivityData?taskName=${props.taskName}&data=${activityData.value}&time=${taskCompletionTime.value ? taskCompletionTime.value : 'default'}`,
      auto: true,
    });
    await activityCompletionResponse.promise;

    if (!activityCompletionResponse?.data) {
      console.warn('No response data received for activity completion.');
      return;
    }

    completionTime.value = activityCompletionResponse.data.slice(0, 5);
  } catch (error) {
    console.error('Failed to send activity completion request:', error);
    activityCompletionResponse = null;
  }
}

const onSuccess = (file) => {
  try {
    if (!props.taskName || !file?.file_url) {
      console.warn('Missing `taskName` or file URL in `onSuccess` handler.');
      return;
    }

    taskProof.value = createResource({
      url: `/api/method/wellnest.api.setFilePath?taskName=${props.taskName}&fileURL=${file.file_url}`,
      auto: true,
    });
  } catch (error) {
    console.error('Error handling file upload success:', error);
    taskProof.value = null;
  }
};
</script>
