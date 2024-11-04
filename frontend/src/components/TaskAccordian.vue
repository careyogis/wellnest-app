<template>
  <!-- Component: Outline accordion -->
  <section
    class="w-full bg-white border divide-y rounded divide-slate-200 border-slate-200"
  >
    <details class="p-3 group" open>
      <summary
        class="[&::-webkit-details-marker]:hidden flex justify-between items-center relative font-medium list-none cursor-pointer text-slate-700 focus-visible:outline-none transition-colors duration-300 group-hover:text-slate-900"
      >
        <div class="order-2 text-[#070707] font-semibold">{{ title }}</div>
        <div class="order-3 flex justify-between items-center">
          <div>
            <FeatherIcon
              class="w-6 mr-1 stroke-[#78abaf] stroke-2"
              name="clock"
            />
          </div>
          <!-- <div class="text-[#070707] font-semibold">10 AM</div> -->
          <div v-if="prescribedTime" class="text-[#070707] font-semibold">
            {{ prescribedTime.slice(0, 4) }}
          </div>
        </div>
        <FeatherIcon
          class="transition duration-300 stroke-slate-700 group-open:rotate-90 w-5 stroke-[#070707] stroke-2"
          name="chevron-right"
        />
      </summary>
      <div class="mt-4 px-7 text-slate-500">
        <div class="flex">
          <TextInput
            :type="'text'"
            size="lg"
            variant="outline"
            placeholder="120/65"
            v-model="inputField"
          />
          <div class="self-end">mm/hg</div>
        </div>
        <div v-if="proof">
          <FeatherIcon
            class="inline-block w-3 -rotate-45 mr-1 stroke-[blue] stroke-1"
            name="paperclip"
          />
          <a class="inline-block my-5 text-blue-500" :href="proof"
            >Uploaded Image</a
          >
        </div>
        <div class="text-[#070707] font-semibold">Notes:</div>
        <div>{{ notes }}</div>
        <FileUploader
          class="mt-5"
          :fileTypes="['image/*']"
          @success="onSuccess"
        >
          <template
            #default="{
              file,
              uploading,
              progress,
              uploaded,
              message,
              error,
              total,
              success,
              openFileSelector,
            }"
          >
            <button
              class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1"
              @click="openFileSelector"
              :loading="updloading"
            >
              {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
            </button>
          </template>
        </FileUploader>
        <div class="flex justify-between items-center">
          <button
            class="text-xl font-medium border-2 border-gray-500 rounded w-2/3 py-2 mb-2"
            @click="sendRequest"
          >
            Mark as Completed
          </button>
          <div class="order-3 flex justify-between items-center">
            <FeatherIcon
              class="w-6 mr-1 stroke-[#78abaf] stroke-2"
              name="clock"
            />
            <div class="text-[#070707] font-semibold">10 AM</div>
            <!-- <div v-if="activityCompletionTime" class="text-[#070707] font-semibold">{{ activityCompletionTime }}</div> -->
          </div>
        </div>
      </div>
    </details>
  </section>
  <!-- End Outlined accordion -->
</template>

<script setup>
import { TextInput, FileUploader, Button, FeatherIcon } from 'frappe-ui'
import {
  createResource,
  createListResource,
  createDocumentResource,
} from 'frappe-ui'

const props = defineProps([
  'title',
  'id',
  'engagementId',
  'taskName',
  'proof',
  'taskResource',
  'prescribedTime',
  'notes',
])

const inputField = defineModel()
let activityCompletionTime
function sendRequest() {
  let time = new Date()
  time = time.getTime()
  activityCompletionTime = createResource({
    url: `/api/method/wellnest.api.setActivityData?taskName=${props.taskName}&data=${inputField.value}`,
    auto: true,
  })
}

const onSuccess = (file) => {
  activityCompletionTime = createResource({
    url: `/api/method/wellnest.api.setFilePath?taskName=${props.taskName}&fileURL=${file.file_url}`,
    auto: true,
  })
  props.taskResource.reload()
}
</script>
