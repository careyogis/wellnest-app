<template>
  <div v-if="!caregiverResource.loading && caregiverResource.data">
    <CaregiverNavbar title="Profile" />
    <div class="my-3 flex flex-col items-center">
      <Avatar
        class="flex-auto"
        :shape="'circle'"
        :image="caregiverResource.data.passport_size_photo"
        label="EY"
        size="3xl"
      />
      <div class="text-xl text-[#070707] font-semibold">
        {{ caregiverResource.data.full_name }}
      </div>
      <div>
        {{ caregiverResource.data.caregiver_type }}
      </div>
      <div>Member Since: {{ caregiverResource.data.creation.slice(0, 11) }}</div>
    </div>

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
                  {{ caregiverResource.data.phone_number.slice(0, 3) }}
                  {{ caregiverResource.data.phone_number.slice(4) }}
                </div>
                <div>
                  <Badge :variant="'ghost'" theme="gray">
                    <template #prefix>
                      <FeatherIcon class="w-4" name="mail" />
                    </template>
                  </Badge>
                  {{ caregiverResource.data.email }}
                </div>
              </div>
              <!-- TODO: MAKE ALL THE BELOW INFO DYNAMIC -->
              <Agency :agencyName="caregiverResource.data.agency" />
              <div class="mySpecialities mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">
                  My Specialities
                </div>
                <div v-if="caregiverResource.data.caregiver_type === 'Attendant'">
                  <!-- make this dynamic for when it's attendant and when it's nursing -->
                  <span
                    v-for="specialization in caregiverResource.data.attendant_care"
                    class="mx-1"
                  >
                    <Badge
                      :variant="'solid'"
                      size="lg"
                      label="Badge"
                      theme="orange"
                    >
                      {{ specialization.link_ebyl }}
                    </Badge>
                  </span>
                </div>
                <div v-if="caregiverResource.data.caregiver_type === 'Nurse'">
                  <!-- make this dynamic for when it's attendant and when it's nursing -->
                  <span
                    v-for="specialization in caregiverResource.data.nursing_specialization"
                    class="mx-1"
                  >
                    <Badge
                      :variant="'solid'"
                      size="lg"
                      label="Badge"
                      theme="orange"
                    >
                      {{ specialization.link_liob}}
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
import { reactive } from 'vue'
import { Tabs, FeatherIcon, Badge, Avatar, createResource } from 'frappe-ui'
import { session } from '../data/session'
import CaregiverNavbar from '../components/CaregiverNavbar.vue'
import Agency from '../components/Agency.vue'

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

let caregiverResource = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'Caregiver',
    // fields: ['name', 'full_name', 'caregiver_type', 'phone_number', 'email', 'agency', 'nursing_specialization', 'passport_size_photo', 'creation', ],  
    filters: {
      user_id: session.user,
    },
  },
  auto: true,
})
</script>
