<template>
  <div v-if="!caregiver.loading && caregiver.data">
    <CaregiverNavbar title="Profile" />
    <div class="my-3 flex flex-col items-center">
      <Avatar
        class="flex-auto w-20 h-20 mb-2.5"
        :shape="'circle'"
        :image="caregiver.data.caregiver_name.passport_size_photo"
        label="EY"
        size="3xl"
      />
      <div class="text-xl text-[#070707] font-semibold">
        {{ caregiver.data.caregiver_name.full_name }}
      </div>
      <div>
        {{ caregiver.data.caregiver_name.caregiver_type }}
      </div>
      <div>
        Member Since:
        {{ shortDateFormatter(caregiver.data.caregiver_name.creation) }}
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
                    {{ caregiver.data.caregiver_name.phone_number }}
                  </div>
                </div>
                <div class="flex gap-2">
                  <FeatherIcon class="w-4 mt-0.5" name="mail" />
                  <div>
                    {{ caregiver.data.caregiver_name.email }}
                  </div>
                </div>
              </div>
              <!-- AGENCY SECTION -->
              <div class="agencyDetails mb-7">
                <div class="text-xl text-[#070707] font-semibold mb-3">
                  Agency Details
                </div>
                <div class="mb-3 flex gap-2">
                  <FeatherIcon class="w-5" name="user" />
                  <div>
                    {{ caregiver.data.agency_data.supplier_name }}
                  </div>
                </div>
                <div class="mb-3 flex gap-2">
                  <FeatherIcon class="w-4" name="phone" />
                  <div>
                    {{ caregiver.data.agency_contact.phone }}
                  </div>
                </div>
                <div class="flex gap-2">
                  <FeatherIcon class="w-4 self-start mt-1" name="map-pin" />
                  <p>
                    {{ caregiver.data.agency_contact.address_line1 }} <br />
                    {{ caregiver.data.agency_contact.address_line2 }} <br />
                    {{ caregiver.data.agency_contact.city }} <br />
                    {{ caregiver.data.agency_contact.state }} <br />
                    {{ caregiver.data.agency_contact.country }} <br />
                    {{ caregiver.data.agency_contact.pincode }}
                  </p>
                </div>
              </div>
              <!-- SPECIALITIES SECTION -->
              <div class="mySpecialities mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">
                  My Specialities
                </div>
                <div
                  v-if="
                    caregiver.data.caregiver_data.caregiver_type === 'Attendant'
                  "
                >
                  <span
                    v-for="specialization in caregiver.data.caregiver_data
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
                <div
                  v-if="
                    caregiver.data.caregiver_data.caregiver_type === 'Nurse'
                  "
                >
                  <span
                    v-for="specialization in caregiver.data.caregiver_data
                      .proficient_activities"
                    class=""
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
              </div>
              <!-- IMPORTANT DOCUMENTS SECTION -->
              <div class="mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">
                  Important Documents
                </div>
              </div>
              <div
                class="mb-3 flex gap-2"
                v-if="caregiver.data.caregiver_name.aadhar_photo"
              >
                <FeatherIcon class="w-4" name="paperclip" />
                <a :href="caregiver.data.caregiver_name.aadhar_photo"
                  >Aadhar Card</a
                >
              </div>
              <div
                class="mb-3 flex gap-2"
                v-if="caregiver.data.caregiver_name.pan_photo"
              >
                <FeatherIcon class="w-4 -rotate-45" name="paperclip" />
                <a :href="caregiver.data.caregiver_name.pan_photo">Pan Card</a>
              </div>
              <div
                class="mb-3 flex gap-2"
                v-if="
                  caregiver.data.caregiver_name.police_verification_certificate
                "
              >
                <FeatherIcon class="w-4 -rotate-45" name="paperclip" />
                <a
                  :href="
                    caregiver.data.caregiver_name
                      .police_verification_certificate
                  "
                  >Police Verification Certificate</a
                >
              </div>
              <div
                class="mb-3 flex gap-2"
                v-if="caregiver.data.caregiver_name.vaccination_certificate"
              >
                <FeatherIcon class="w-4 -rotate-45" name="paperclip" />
                <a :href="caregiver.data.caregiver_name.vaccination_certificate"
                  >Vaccination Certificate</a
                >
              </div>
            </div>

            <!-- RATINGS SECTION -->
            <div v-else-if="state.index === 1">
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
              <div v-for="rater in caregiver.data.caregiver_data.rating">
                <div class="mt-8 grid grid-cols-8">
                  <Avatar
                    class=""
                    :shape="'circle'"
                    :image="caregiver.data.caregiver_name.passport_size_photo"
                    :label="rater.rater"
                    size="xl"
                  />
                  <div class="col-span-7 flex-col">
                    <div class="flex mb-2 items-end gap-2">
                      <div class="text-sm text-[#78abaf] font-semibold">
                        {{ rater.rater }}
                      </div>
                      <div class="text-sm">
                        {{ shortDateFormatter(rater.rating_date) }}
                      </div>
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
import Earnings from '../components/Earnings.vue'
import { formatCurrency, shortDateFormatter } from '../utils'

const state = reactive({
  index: 0,
  tabs: [
    {
      label: 'General',
    },
    {
      label: 'Ratings',
    },
  ],
})

let caregiver = createResource({
  url: '/api/method/wellnest.api.profile',
  auto: true,
})

// let caregiverResource = createResource({
//   url: 'frappe.client.get',
//   params: {
//     doctype: 'Caregiver',
//     // fields: ['name', 'full_name', 'caregiver_type', 'phone_number', 'email', 'agency', 'nursing_specialization', 'passport_size_photo', 'creation', ],
//     filters: {
//       user_id: session.user,
//     },
//   },
//   auto: true,
// })

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
