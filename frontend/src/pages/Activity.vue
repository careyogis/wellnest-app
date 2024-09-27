<template>
  <div>
    <CaregiverNavbar title="Daily Tasks" />
    <div class="flex flex-col items-center my-3">
      <Avatar
        :shape="'circle'"
        :image="taskResource.data.customerDoc.image"
        label="EY"
        size="3xl"
      />
      <div class="text-xl text-[#070707] font-semibold">
         {{ taskResource.data.customerDoc.name }}
      </div>
      <div>
        <!-- TODO: fetch gender, age from backend -->
        Gender, Age
      </div>
    </div>
    <Tabs class="bro" v-model="state.index" :tabs="state.tabs">
      <template #default="{ tab }">
        <div class="p-5">
          <div>
            <div v-if="state.index === 0">
              <TaskAccordian v-for="task in taskResource.data.activities" :title="task.activity" :notes="task.activity_notes" :id="task.name"/>
            </div>
            <div v-else-if="state.index === 1">
              <div class="flex justify-between items-center w-full">
                <div>
                  <FeatherIcon
                    class="inline-block w-3 -rotate-45 mr-1 stroke-[blue] stroke-1"
                    name="paperclip"
                  />
                  <div class="inline-block my-5 text-blue-500">
                    reading1.png
                  </div>
                </div>
                <div class="text-sm"> 20 June 2024 </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Tabs>
  </div>
</template>

<script setup>
import { Tabs, FeatherIcon, Badge, Avatar } from 'frappe-ui'
import { computed, reactive, ref } from 'vue'
import { createDocumentResource, createResource } from 'frappe-ui'
import CaregiverNavbar from '../components/CaregiverNavbar.vue'
import TaskAccordian from '../components/TaskAccordian.vue'

const state = reactive({
  index: 0,
  tabs: [
    {
      label: 'Daily Tasks',
    },
    {
      label: 'Assessment',
    },
  ],
})

let taskResource = createResource({
  url: '/api/method/wellnest.api.activity',
  auto: true,
})

</script>
