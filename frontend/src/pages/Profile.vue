<template>
  <div v-if="caregiver">
    <CaregiverNavbar />
    <Tabs class="bro" v-model="state.index" :tabs="state.tabs">
      <template #default="{ tab }">
        <div class="p-5">
          <div>
            <div v-if="state.index === 0">
              <div class="mb-7">
                <div class="text-xl text-[#070707] font-semibold mb-3">
                  Contact Information
                </div>
                <div class="mb-3">
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-4" name="phone" />
                    </template>
                  </Badge>
                  {{ caregiver.phone_number.slice(0, 3) }}
                  {{ caregiver.phone_number.slice(4) }}
                </div>
                <div v-if="caregiver.email">
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-4" name="phone" />
                    </template>
                  </Badge>
                  {{ caregiver.email }}
                </div>
                <div v-else-if="caregiver.email === null">
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-4" name="mail" />
                    </template>
                  </Badge>
                  None
                </div>
              </div>
              <!-- TODO: MAKE ALL THE BELOW INFO DYNAMIC -->
              <div class="agencyDetails mb-7">
                <div class="text-xl text-[#070707] font-semibold mb-3">
                  Agency Details
                </div>
                <div class="mb-3">
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-5" name="user" />
                    </template>
                  </Badge>
                  Agency Name Here
                  <!-- {{ agency.agency_name }} -->
                </div>
                <div class="mb-3">
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-4" name="phone" />
                    </template>
                  </Badge>
                  Agency Number Here
                </div>
                <div>
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-4" name="map-pin" />
                    </template>
                  </Badge>
                  Agency Adress here
                </div>
              </div>
              <div class="mySpecialities mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">
                  My Specialities
                </div>
                <div>
                  <span
                    v-for="specialization in caregiver.nursing_specialization"
                    class="mx-1"
                  >
                    <Badge
                      :variant="'solid'"
                      size="lg"
                      label="Badge"
                      theme="orange"
                    >
                      {{ specialization.link_liob }}
                    </Badge>
                  </span>
                </div>
              </div>
              <div class="mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">
                  Important Documents
                </div>
              </div>
            </div>
            <div v-else-if="state.index === 1"></div>
            <div v-else-if="state.index === 2"></div>
          </div>
        </div>
      </template>
    </Tabs>
    <div></div>
  </div>
</template>

<script setup>
import { Tabs, FeatherIcon, Badge } from 'frappe-ui'
import { computed, reactive, ref, watch } from 'vue'
import { createDocumentResource } from 'frappe-ui'
import CaregiverNavbar from '../components/CaregiverNavbar.vue'
import { createResource } from 'frappe-ui'

// TODO: Need to get the doctype instance not just the doctype list
// let todos = createResource({
//   url: '/api/method/frappe.client.get_list',
//   // url: '/api/method/frappe.get_doc',
//   // url: '/api/v2/document/Caregiver',
//   // method: 'GET',
//   params: {
//     doctype: 'Caregiver',
//     name: 'Caregiver-0009'
//   },
// })
// todos.fetch()

const state = reactive({
  index: 0,
  tabs: [
    {
      label: 'General',
    },
    {
      label: 'Earnings',
    },
    {
      label: 'Ratings',
    },
  ],
})

let caregiverResource = createDocumentResource({
  doctype: 'Caregiver',
  name: 'Caregiver-0009',
  auto: true,
  // onSuccess(data) {
  //   let agency = agencyResource(data.agency)
  // },
})

const caregiver = computed(() => {
  if (caregiverResource.doc) {
    return caregiverResource.doc
  }
})

let agencyResource = (agency_name) => {
  let agency_resource = createDocumentResource({
    doctype: 'Agency',
    name: agency_name,
    auto: true,
  })
  return agency_resource
}

watch(caregiver, () => {
  console.log(caregiver.value.agency)
  agencyResource(caregiver.value.agency)
  console.log(agencyResource.doc)
})

console.log(agencyResource.doc)

let agency = computed(() => {
  if (agencyResource.doc) {
    console.log('agencyResource being read')
    return agencyResource.doc
  }
})
console.log(agency.value)
</script>
