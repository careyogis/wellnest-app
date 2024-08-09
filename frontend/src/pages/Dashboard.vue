<template>
  <nav class="flex mx-5 my-2 items-center justify-between mb-10">
    <div class="w-15 h-15 flex items-center justify-center">
      <button
        class="w-[42px] h-[42px] bg-white border divide-y divide-slate-200 border-slate-200 rounded-full drop-shadow-lg"
      >
        <FeatherIcon class="pl-2.5 w-8 h-8 stroke-gray-700" name="align-left" />
      </button>
    </div>
    <img class="w-15" src="/public/favicon.png" alt="" />
    <Avatar
      :shape="'circle'"
      :image="'https://lh5.googleusercontent.com/proxy/gXCFTaGwqD6OXUkJWgLLGw5vAFyJUTnFQjRGF9N_n9dH7alWLedGpd_6mPfAMrJWyVw5fmx_4zMNhUnP-CFnDVe7HLbbWrAQgpgrf7aR32eoZ3euxAX48BrCXtGajHMd'"
      label="EY"
      size="2xl"
    />
  </nav>
  <div class="m-[28px]">
    <div class="flex justify-start gap-3">
      <button
        class="w-[42px] h-[42px] rounded-full bg-gradient-to-b from-[#0FD3C2] from-90% to-[#10BAAB] to-10% mb-10"
      >
        <FeatherIcon class="pl-2.5 w-8 h-8 stroke-white" name="calendar" />
      </button>
      <div class="flex flex-col">
        <div class="font-semibold">20 June 2024</div>
        <div class="text-sm">Thursday</div>
      </div>
    </div>
    <div class="flex justify-between w-full">
      <div class="font-semibold">Beneficiary</div>
      <div class="flex items-center">
        <div class="text-sm text-[#10BAAB]">See All</div>
        <FeatherIcon
          class="pl-2.5 w-6 h-6 stroke-[#10BAAB]"
          name="chevron-right"
        />
      </div>
    </div>
  </div>
  <div class="w-90%">
    <div class="m-[10px] p-4 bg-white border rounded border-slate-600">
      <div class="flex justify-between">
        <div class="flex items-center gap-1">
          <Avatar
            :shape="'circle'"
            :image="'https://lh5.googleusercontent.com/proxy/gXCFTaGwqD6OXUkJWgLLGw5vAFyJUTnFQjRGF9N_n9dH7alWLedGpd_6mPfAMrJWyVw5fmx_4zMNhUnP-CFnDVe7HLbbWrAQgpgrf7aR32eoZ3euxAX48BrCXtGajHMd'"
            label="EY"
            size="2xl"
          />
          <div>
            <div class="font-semibold">
              {{ caregiverResource.data.full_name }}
            </div>
            <!-- calculate age and replace it with the static data -->
            <div class="">{{ caregiverResource.data.gender }} 23</div>
          </div>
        </div>
        <div class="flex">
          <FeatherIcon
            class="w-6 mt-0.5 stroke-[#10BAAB] stroke-2 self-start"
            name="calendar"
          />
          <div class="flex flex-col items-center">
            <div class="font-semibold">15 June 2024 - 25 June 2024</div>
            <div>5 more days to go</div>
            <div class="flex gap-1">
              <FeatherIcon
                class="w-5 mt-0.5 stroke-[#10BAAB] stroke-2"
                name="clock"
              />
              <div>10 AM - 5 PM</div>
            </div>
          </div>
        </div>
      </div>

      <hr class="m-4" />
      <div class="mb-7">
        <div class="text-[#070707] font-semibold mb-3">Contact Details</div>
        <div class="mb-3 flex gap-2">
          <FeatherIcon class="w-4" name="phone" />
          <div class="text-[14px]">
            {{ caregiverResource.data.phone_number.slice(0, 3) }}
            {{ caregiverResource.data.phone_number.slice(4) }}
          </div>
        </div>
        <div class="flex gap-2">
          <FeatherIcon class="w-4 mt-0.5" name="mail" />
          <div class="text-[14px]">
            {{ caregiverResource.data.email }}
          </div>
        </div>
      </div>
      <Customer />
      <NursingManager />
      <div class="mySpecialities mb-5">
        <div class="text-[#070707] font-semibold mb-2">Services Needed</div>
        <div v-if="caregiverResource.data.caregiver_type === 'Attendant'">
          <span
            v-for="specialization in caregiverResource.data.attendant_care"
            class="mx-1"
          >
            <Badge :variant="'solid'" size="lg" label="Badge" theme="orange">
              {{ specialization.link_ebyl }}
            </Badge>
          </span>
        </div>
        <div v-if="caregiverResource.data.caregiver_type === 'Nurse'">
          <span
            v-for="specialization in caregiverResource.data
              .nursing_specialization"
            class="mx-1"
          >
            <Badge :variant="'solid'" size="lg" label="Badge" theme="orange">
              {{ specialization.link_liob }}
            </Badge>
          </span>
        </div>
      </div>
      <button
        class="text-xl font-medium border border-gray-300 rounded w-1/2 py-2 mb-4"
      >
        <div class="flex justify-evenly">
          <FeatherIcon
            class="w-4 mt-0.5 stroke-[#10BAAB] stroke-2"
            name="check-square"
          />
          <div class="text-[#10BAAB]">Tasks</div>
          <FeatherIcon
            class="w-4 mt-0.5 stroke-[#10BAAB] stroke-2"
            name="chevron-right"
          />
        </div>
      </button>
      <div class="flex gap-6">
        <button
          class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1"
        >
          <div class="flex justify-center gap-1">
            <FeatherIcon
              class="w-4 mt-0.5 stroke-gray-500 stroke-2"
              name="eye"
            />
            <div>Checkin</div>
          </div>
        </button>
        <button
          class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1"
        >
          <div class="flex justify-center gap-1">
            <FeatherIcon
              class="w-4 mt-0.5 stroke-gray-500 stroke-2"
              name="eye"
            />
            <div>Checkout</div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { FeatherIcon, Badge, Avatar, createResource } from 'frappe-ui'
import { session } from '../data/session'
import Agency from '../components/Agency.vue'
import Customer from '../components/Customer.vue'
import NursingManager from '../components/NursingManager.vue'

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
