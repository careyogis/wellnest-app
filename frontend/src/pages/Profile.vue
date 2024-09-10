<template>
  <div v-if="!caregiverResource.loading && caregiverResource.data">
    <CaregiverNavbar title="Profile" />
    <div class="my-3 flex flex-col items-center">
      <Avatar
        class="flex-auto w-20 h-20 mb-2.5"
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
      <div>
        Member Since: {{ caregiverResource.data.creation.slice(0, 11) }}
      </div>
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
                <div class="mb-3 flex gap-2">
                  <FeatherIcon class="w-4" name="phone" />
                  <div>
                    <!-- {{ caregiverResource.data.phone_number.slice(0, 3) }}
                    {{ caregiverResource.data.phone_number.slice(4) }} -->
                    {{ caregiverResource.data.phone_number }}
                  </div>
                </div>
                <div class="flex gap-2">
                  <FeatherIcon class="w-4 mt-0.5" name="mail" />
                  <div>
                    {{ caregiverResource.data.email }}
                  </div>
                </div>
              </div>
              <!-- TODO: MAKE ALL THE BELOW INFO DYNAMIC -->
              <Agency :agencyName="caregiverResource.data.supplier" />
              <div class="mySpecialities mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">
                  My Specialities
                </div>
                <div
                  v-if="caregiverResource.data.caregiver_type === 'Attendant'"
                >
                  <!-- make this dynamic for when it's attendant and when it's nursing -->
                  <span
                    v-for="specialization in caregiverResource.data
                      .proficient_activities"
                    class="mx-1"
                  >
                    <Badge
                      :variant="'solid'"
                      size="lg"
                      label="Badge"
                      theme="orange"
                    >
                      {{ specialization.activity }}
                    </Badge>
                  </span>
                </div>
                <div v-if="caregiverResource.data.caregiver_type === 'Nurse'">
                  <!-- make this dynamic for when it's attendant and when it's nursing -->
                  <span
                    v-for="specialization in caregiverResource.data
                      .nursing_specialization"
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
            <div v-else-if="state.index === 1">
              <!-- TODO: MAKE THIS AS A SETTLEMENT COMPONENT => FETCH FROM PAYMENT DOCTYPE -->
              <div
                class="block max-w py-5 px-6 border border-gray-400 rounded-lg"
              >
                <p class="text-xl text-[#070707] font-semibold mb-1">
                  Total Earnings
                </p>
                <p class="text-[36px] text-[#070707] font-semibold mb-2">
                  {{ formatCurrency(165000, 'INR') }}
                </p>
                <div class="grid grid-cols-2 grid-rows-2">
                  <div>Next Settlement</div>
                  <div class="flex gap-2">
                    <FeatherIcon
                      class="w-4 stroke-[#78abaf] stroke-2"
                      name="calendar"
                    />
                    <div class="font-semibold text-[#78abaf]">15 July 2024</div>
                  </div>
                  <div>Amount</div>
                  <div class="flex gap-2">
                    <div class="font-semibold text-[#78abaf] ml-1">
                      {{ formatCurrency(0, 'INR').slice(0, 1) }}
                    </div>
                    <div class="font-semibold text-[#78abaf] ml-0.5">
                      {{ formatCurrency(65000, 'INR').slice(1) }}
                    </div>
                  </div>
                </div>
                <button
                  class="bg-[#DB7706] text-white rounded-sm w-full mr-5 mt-15"
                >
                  <div class="flex justify-center gap-1">
                    <FeatherIcon
                      class="w-4 mr-1 stroke-[#ffffff] stroke-2"
                      name="rotate-ccw"
                    />
                    Settlement History
                  </div>
                </button>
              </div>
            </div>
            <!-- RATINGS SECTION -->
            <div v-else-if="state.index === 2">
              <div class="flex justify-between">
                <div class="text-3xl font-semibold">Overall Rating</div>
                <div class="flex">
                  <FeatherIcon
                    v-for="heart in 4"
                    class="w-4 mr-1 fill-current text-[#DB7706] stroke-2"
                    name="heart"
                  />
                  <FeatherIcon class="w-4 mr-1 stroke-1" name="heart" />
                </div>
                <!-- <div>
                  <star-rating :increment="0.5" :rating="4"></star-rating>
                </div> -->
              </div>
              <div v-for="rater in caregiverResource.data.rating">
                <div class="mt-8 grid grid-cols-8">
                  <Avatar
                    class=""
                    :shape="'circle'"
                    :image="caregiverResource.data.passport_size_photo"
                    :label="rater.rater"
                    size="xl"
                  />
                  <div class="col-span-7 flex-col">
                    <div class="flex mb-2 items-end gap-2">
                      <div class="text-sm text-[#78abaf] font-semibold">
                        {{ rater.rater }}
                      </div>
                      <div class="text-sm">20 June 2024</div>
                    </div>
                    <p class="col-span-2 text-sm mb-2">
                      {{ rater.comment }}
                    </p>
                    <div class="flex">
                      <FeatherIcon
                        v-for="heart in 5"
                        class="w-4 mr-1 fill-current text-[#DB7706] stroke-2"
                        name="heart"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Tabs>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Tabs, FeatherIcon, Badge, Avatar, createResource } from 'frappe-ui'
import { session } from '../data/session'
import CaregiverNavbar from '../components/CaregiverNavbar.vue'
import Agency from '../components/Agency.vue'
import { formatCurrency } from '../utils'

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

// const ratings = ref(null)

// function calculateRatings(rating) {
//   let temp = rating * 10
//   ratings.value = Math.floor(temp / 2)
// }

// const caregiverRatings = computed((rating) => {
//   let temp = rating * 10;
//   ratings = Math.floor(temp/2);
// })

// console.log(caregiverResource)
// window.sankalp = caregiverResource

// let agencyResource
// agencyResource = createResource({
//   url: 'frappe.client.get_list',
//   params: {
//     doctype: 'Agency',
//     fields: ['agency_name', 'primary_phone', 'complete_address'],
//     name: props.agencyName,
//   },
//   auto: true,
// })

// let caregiverResource
// let agencyResource

// apiCall()

// async function apiCall() {
//   caregiverResource = createResource({
//     url: 'frappe.client.get',
//     params: {
//       doctype: 'Caregiver',
//       // fields: ['name', 'full_name', 'caregiver_type', 'phone_number', 'email', 'agency', 'nursing_specialization', 'passport_size_photo', 'creation', ],
//       filters: {
//         user_id: session.user,
//       },
//     },
//     auto: true,
//   })
//   await caregiverResource.promise
//   console.log(caregiverResource.data)

//   agencyResource = createResource({
//     url: 'frappe.client.get_list',
//     params: {
//       doctype: 'Agency',
//       fields: ['agency_name', 'primary_phone', 'complete_address'],
//       name: caregiverResource.data.agency,
//     },
//     auto: true,
//   })
//   await agencyResource.promise
//   console.log(agencyResource.data)
// }
</script>
