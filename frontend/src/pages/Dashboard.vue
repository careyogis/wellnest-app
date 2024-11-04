<template>
  <div v-if="dashboard.data">
    <nav class="flex mx-5 my-2 items-center justify-between mb-10">
      <Avatar
        :shape="'circle'"
        :image="dashboard.data.caregiver.passport_size_photo"
        label="EY"
        size="2xl"
      />
      <img class="w-15" src="/public/favicon.png" alt="" />
      <div class="w-15 h-15 flex items-center justify-center">
        <button
          @click="toggleMobileNav"
          class="w-[42px] h-[42px] bg-white border divide-y divide-slate-200 border-slate-200 rounded-full drop-shadow-lg"
          :class="{ 'icon-active': mobileNav }"
        >
          <FeatherIcon
            class="pl-2.5 w-8 h-8 stroke-gray-700"
            name="align-left"
          />
        </button>
      </div>
      <div v-if="mobileNav" class="dropdown-nav">
        <ul class="navigation">
          <li>
            <router-link class="link" :to="{ name: 'Home' }">Home</router-link>
          </li>
          <li>
            <router-link class="link" :to="{ name: '' }">Profile</router-link>
          </li>
          <li>
            <router-link class="link" :to="{ name: '' }">Dashboard</router-link>
          </li>
        </ul>
      </div>
    </nav>
    <div class="m-[28px]">
      <div class="flex justify-start gap-3">
        <button
          class="w-[42px] h-[42px] rounded-full bg-gradient-to-b from-[#0FD3C2] from-90% to-[#10BAAB] to-10% mb-10"
        >
          <FeatherIcon class="pl-2.5 w-8 h-8 stroke-white" name="calendar" />
        </button>
        <div class="flex flex-col">
          <!-- <div class="font-semibold">20 June 2024</div> -->
          <div class="font-semibold">{{ longDateFormatter(new Date()) }}</div>
          <div class="text-sm">{{ dayFormatter(new Date()) }}</div>
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
    <!-- card -->
    <div v-for="engagement in dashboard.data.engagements" class="w-90%">
      <div class="m-[10px] p-4 bg-white border rounded border-slate-600">
        <div class="flex justify-between">
          <div class="flex items-center gap-1">
            <Avatar
              v-if="!mobileNav"
              :shape="'circle'"
              :image="engagement.customer.image"
              label="EY"
              size="2xl"
            />
            <div>
              <div class="font-semibold">
                {{ engagement.customer.customer_name }}
              </div>
              <div>
                {{ engagement.customer.gender }}
                {{ engagement.customer.custom_age }} Years
              </div>
            </div>
          </div>
          <div class="flex">
            <FeatherIcon
              class="w-6 mt-0.5 stroke-[#10BAAB] stroke-2 self-start"
              name="calendar"
            />
            <div class="flex flex-col items-center">
              <!-- <div class="font-semibold">15 June 2024 - 25 June 2024</div> -->
              <div class="font-semibold">
                <!-- TODO: ADD VALIDATION FOR IF THERE IS NO END DATE -->
                {{ longDateFormatter(engagement.engagement.start_date) }} -
                {{ longDateFormatter(engagement.engagement.end_date) }}
              </div>
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
              {{ engagement.customer.mobile_no }}
            </div>
          </div>
          <div class="flex gap-2">
            <FeatherIcon class="w-4 mt-0.5" name="mail" />
            <div class="text-[14px]">
              {{ engagement.customer.email_id }}
            </div>
          </div>
        </div>
        <!-- <Customer /> -->
        <!-- Nursing Manager -->
        <div class="nursingManager mb-7">
          <div class="text-[#070707] font-semibold mb-3">Nursing Manager</div>
          <div class="mb-3 flex gap-2">
            <FeatherIcon class="w-5" name="user" />
            <div class="text-[14px]">
              {{ engagement.engagement.nursing_manager }}
            </div>
          </div>
          <div class="mb-3 flex gap-2">
            <FeatherIcon class="w-4" name="phone" />
            <div class="text-[14px]">
              {{ engagement.engagement.nursing_manager_contact }}
            </div>
          </div>
        </div>
        <div class="mySpecialities mb-5">
          <div class="text-[#070707] font-semibold mb-2">Services Needed</div>
          <span
            v-for="services in engagement.engagement.required_activity"
            class="mx-1"
          >
            <Badge :variant="'solid'" size="lg" label="Badge" theme="orange">
              {{ services.activity }}
            </Badge>
          </span>
        </div>
        <button
          class="text-xl font-medium border border-gray-300 rounded w-1/2 py-2 mb-4"
        >
          <div class="flex justify-evenly">
            <FeatherIcon
              class="w-4 mt-0.5 stroke-[#10BAAB] stroke-2"
              name="check-square"
            />
            <!-- <div class="text-[#10BAAB]">Tasks</div> -->
            <router-link class="text-[#10BAAB]" :to="{ name: 'Activity', params: { dailyRecordId: checkins[engagement.engagement.name].name }}"
              >Tasks</router-link
            >
            <FeatherIcon
              class="w-4 mt-0.5 stroke-[#10BAAB] stroke-2"
              name="chevron-right"
            />
          </div>
        </button>
        <div class="flex gap-6">
          <button
            class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1"
            @click="checkin(engagement.engagement.name)"
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
            @click="checkout(engagement.engagement.name)"
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
  </div>
  <div v-else>Loading...</div>
</template>
<script setup>
import { reactive, ref } from 'vue'
import {
  FeatherIcon,
  Badge,
  Avatar,
  createResource,
  createDocumentResource,
  createListResource,
} from 'frappe-ui'
import { session } from '../data/session'
import Agency from '../components/Agency.vue'
import Customer from '../components/Customer.vue'
import NursingManager from '../components/NursingManager.vue'
import {
  getAge,
  dayFormatter,
  longDateFormatter,
  shortDateFormatter,
  formatCurrentDateTime,
} from '../utils'

let dashboard
let engagementActivity
let engagementRecord

// Hamburger parts
let scrollPosition
let mobile
let mobileNav = ref(false)
let windowWidth

function toggleMobileNav() {
  mobileNav.value = !mobileNav.value
}

apiCall()

async function apiCall() {
  dashboard = createResource({
    url: '/api/method/wellnest.api.dashboard',
    auto: true,
  })
  await dashboard.promise
  checkins = Object.fromEntries(
    dashboard.data.engagements.map(({ engagement, todaysCheckin }) => [
      engagement.name,
      todaysCheckin,
    ]),
  )
}

let checkins = {};
async function checkin(engagementId) {

  if (!checkins[engagementId]) {
    const response = createResource({
      url: `/api/method/wellnest.api.createDailyRecord?engagement=${engagementId}&caregiver=${dashboard.data.caregiver.name}&time=${formatCurrentDateTime()}`,
      auto: true,
    });
    await response.promise;
    checkins[engagementId] = response.data;
  } else {
    alert('Already Checked in today');
  }
};

async function checkout(engagementId) {
  const checkin = checkins[engagementId]
  if (!checkin) {
    alert('You have not checked in')
    return;
  }
  let update = createResource({
    url: `/api/method/wellnest.api.checkout?record=${checkin.name}&time=${formatCurrentDateTime()}`,
    auto: true,
  })
  await update.promise;
}

</script>

<style scoped>
nav {
  /* ul,
  .link {
    font-weight: 500;
    color: #fff;
    list-style: none;
    text-decoration: none;
  } */

  li {
    text-transform: uppercase;
    padding: 16px;
    margin-left: 16px;
  }

  .link {
    font-size: 14px;
    transition: 0.5s ease all;
    padding-bottom: 4px;
    border-bottom: 1px solid transparent;
  }

  /* .navigation {
    display: flex;
    align-items: center;
    flex: 1;
    justify-content: flex-end
  } */

  .icon-active {
    transform: rotate(180deg);
  }

  .dropdown-nav {
    display: flex;
    flex-direction: column;
    position: fixed;
    width: 100%;
    max-width: 250px;
    height: 100%;
    background-color: #fff;
    top: 0;
    left: 0;

    li {
      margin-left: 0;
      .link {
        color: #000;
      }
    }
  }
}
</style>
