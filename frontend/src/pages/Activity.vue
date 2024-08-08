<template>
  <div>
    <CaregiverNavbar title="Daily Tasks" />
    <div class="flex flex-col items-center my-3">
      <!-- TODO: fetch avatar image from backend -->
      <Avatar
        :shape="'circle'"
        :image="'https://lh5.googleusercontent.com/proxy/gXCFTaGwqD6OXUkJWgLLGw5vAFyJUTnFQjRGF9N_n9dH7alWLedGpd_6mPfAMrJWyVw5fmx_4zMNhUnP-CFnDVe7HLbbWrAQgpgrf7aR32eoZ3euxAX48BrCXtGajHMd'"
        label="EY"
        size="3xl"
      />
      <div class="text-xl text-[#070707] font-semibold">
        <!-- TODO: fetch name from backend -->
        <!-- {{ caregiverResource.data.full_name }} -->
        Beneficiary Name
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
              <!-- TODO: fetch this from the backend as well as make this a slot(vue) to take in variables and produce accrordians dynamically -->
              <TaskAccordian />
              <TaskAccordian />
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
import { createDocumentResource } from 'frappe-ui'
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
</script>
