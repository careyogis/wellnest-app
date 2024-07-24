<template>
  <h1 class="text-gray-900 font-bold text-[32px]">Profile</h1>
  <div v-if="caregiver">
    <CaregiverNavbar />
    <Tabs v-model="state.index" :tabs="state.tabs">
      <template #default="{ tab }">
        <div class="p-5">
          <div>
            <div v-if="state.index === 0">
              <div class="contactInfo">
                <b>Contact Information</b>
                <div>
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
              <div class="agencyDetails">
                <b>Agency Info</b>
                <div>
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-5" name="user" />
                    </template>
                  </Badge>
                  Agency Name Here
                </div>
                <div>
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
              <div class="mySpecialities">
                <b>My Specialities</b>
                <div>
                  <span>
                    <Badge
                      :variant="'solid'"
                      size="sm"
                      label="Badge"
                      theme="orange"
                    >
                      Meal Preperation
                    </Badge>
                  </span>

                  <span>
                    <Badge
                      :variant="'solid'"
                      size="sm"
                      label="Badge"
                      theme="orange"
                    >
                      Bathing
                    </Badge>
                  </span>
                </div>
              </div>
            </div>
            <div v-else-if="state.index === 1"></div>
            <div v-else-if="state.index === 2"></div>
          </div>
        </div>
      </template>
    </Tabs>
    <div>
    </div>
  </div>
</template>

<script setup>
import { Tabs, FeatherIcon, Badge } from 'frappe-ui'
import { computed, reactive, ref } from 'vue'
import { createDocumentResource } from 'frappe-ui'
import CaregiverNavbar from '../components/CaregiverNavbar.vue'

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
  onSuccess(data) {
    let agency = agencyResource(data.agency)
  },
})

let agencyResource = (agency_name) => {
  return createDocumentResource({
    doctype: 'Agency',
    name: agency_name,
    auto: true,
  })
}

const caregiver = computed(() => {
  if (caregiverResource.doc) {
    return caregiverResource.doc
  }
})

// const agency = computed(() => {
//   if (agencyResource.doc) {
//     return agencyResource.doc
//   }
// })
</script>
