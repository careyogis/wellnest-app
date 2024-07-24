<template>
  <div>
    <h1 class="text-gray-900 font-bold text-[32px]">Daily Tasks</h1>
    <div v-if="beneficiary">
      <BeneficiaryNavbar />
      <Tabs v-model="state.index" :tabs="state.tabs">
        <template #default="{ tab }">
          <div class="p-5">
            <div>
              <div v-if="state.index === 0">
                <TaskAccordian />
              </div>
              <div v-else-if="state.index === 1"></div>
              <div v-else-if="state.index === 2"></div>
            </div>
          </div>
        </template>
      </Tabs>
    </div>
  </div>
</template>

<script setup>
import { Tabs, FeatherIcon, Badge } from 'frappe-ui'
import { computed, reactive, ref } from 'vue'
import { createDocumentResource } from 'frappe-ui'
import BeneficiaryNavbar from '../components/BeneficiaryNavbar.vue'
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

let beneficiaryResource = createDocumentResource({
  doctype: 'Beneficiary',
  name: 'Ben-0010',
  auto: true,
})

const beneficiary = computed(() => {
  if (beneficiaryResource.doc) {
    return beneficiaryResource.doc
  }
})
</script>
