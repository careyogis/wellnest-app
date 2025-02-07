<template>
  <div v-if="dashboard.data && notCaregiver == false">
    <nav class="flex mx-5 my-2 items-center justify-between mb-10">
      <div class="w-15 h-15 flex items-center justify-center">
        <Avatar :shape="'circle'" :image="dashboard.data.caregiver.passport_size_photo" label="EY" size="2xl" />
      </div>
      <img class="w-15" src="/favicon.png" alt="" />
      <div class="w-15 h-15 flex items-center justify-center">
        <button @click="toggleMobileNav"
          class="w-[42px] h-[42px] bg-white border divide-y divide-slate-200 border-slate-200 rounded-full drop-shadow-lg"
          :class="{ 'icon-active': mobileNav }">
          <FeatherIcon class="pl-2.5 w-8 h-8 stroke-gray-700" name="align-left" />
        </button>
      </div>
      <div v-if="mobileNav" class="dropdown-nav">
        <ul class="navigation">
          <li>
            <router-link class="link" :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li>
            <router-link class="link" :to="{ name: 'Profile' }">Profile</router-link>
          </li>
          <li>
            <button class="link" @click="session.logout.submit()">Logout</button>
          </li>
        </ul>
      </div>
    </nav>
    <div class="m-[28px]">
      <div class="flex justify-start gap-3">
        <button
          class="w-[42px] h-[42px] rounded-full bg-gradient-to-b from-[#0FD3C2] from-90% to-[#10BAAB] to-10% mb-10">
          <FeatherIcon class="pl-2.5 w-8 h-8 stroke-white" name="calendar" />
        </button>
        <div class="flex flex-col">
          <div class="font-semibold">{{ longDateFormatter(new Date()) }}</div>
          <div class="text-sm">{{ dayFormatter(new Date()) }}</div>
        </div>
      </div>
      <div class="flex justify-between w-full">
        <div class="font-semibold">Beneficiary</div>
      </div>
    </div>
    <!-- card -->
    <div v-for="engagement in dashboard.data.engagements" class="w-90%">
      <div class="m-[10px] p-4 bg-white border rounded border-slate-600">
        <div class="flex justify-between gap-4">
          <div class="flex items-center gap-1">
            <Avatar v-if="!mobileNav" :shape="'circle'" :image="engagement.customer.image" label="EY" size="2xl" />
            <div>
              <div class="font-semibold">
                {{ engagement.customer.customer_name }}
              </div>
              <div>
                {{ engagement.customer.gender }}
              </div>
              <div v-if="engagement.customer.custom_age">{{ engagement.customer.custom_age }} Years</div>
            </div>
          </div>
          <div class="flex gap-1">
            <FeatherIcon class="w-6 mt-0.5 stroke-[#10BAAB] stroke-2 self-start" name="calendar" />
            <div class="flex flex-col items-center">
              <div class="font-semibold">
                {{ engagement.caregiverStartDate ? longDateFormatter(engagement.caregiverStartDate) : 'Present' }}
                -
                {{ engagement.caregiverEndDate ? longDateFormatter(engagement.caregiverEndDate) : 'Present' }}
              </div>
              <div v-show="engagement.engagement.service_hours" class="flex gap-1">
                <FeatherIcon class="w-5 mt-0.5 stroke-[#10BAAB] stroke-2" name="clock" />
                <div>{{ engagement.engagement.service_hours }} Hours</div>
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
          <div class="whitespace-nowrap overflow-x-auto">
            <span v-for="services in engagement.engagement.required_activity" class="mx-1">
              <Badge :variant="'solid'" size="lg" label="Badge" theme="orange">
                {{ services.activity }}
              </Badge>
            </span>
          </div>
        </div>
        <button v-if="checkins[engagement.engagement.name]"
          class="text-xl font-medium border border-gray-300 rounded w-1/2 py-2 mb-4" @click="
            $router.push({
              name: 'Activity',
              params: {
                dailyRecordId: checkins[engagement.engagement.name].name,
              },
            })
            ">
          <div class="flex justify-evenly">
            <FeatherIcon class="w-4 mt-0.5 stroke-[#10BAAB] stroke-2" name="check-square" />
            <div class="text-[#10BAAB]">Tasks</div>
            <FeatherIcon class="w-4 mt-0.5 stroke-[#10BAAB] stroke-2" name="chevron-right" />
          </div>
        </button>
        <div class="flex gap-6">
          <button v-if="!checkins[engagement.engagement.name]"
            :disabled="!isDateInRange(engagement.reporting_start_time, engagement.reporting_end_time)"
            class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1 disabled:border-gray-200 disabled:text-zinc-400"
            @click="openCheckinDialog(engagement.engagement.name)">
            <div class="flex justify-center gap-1">
              <FeatherIcon class="w-4 mt-0.5 stroke-gray-500 stroke-2" name="eye" />
              <div>Check-In</div>
            </div>
          </button>
          <button v-else :disabled="isDisabled[checkins[engagement.engagement.name].name]"
            class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1 disabled:border-gray-200 disabled:text-zinc-400"
            @click="openCheckoutDialog(engagement.engagement.name)">
            <div class="flex justify-center gap-1">
              <FeatherIcon class="w-4 mt-0.5 stroke-gray-500 stroke-2" name="eye" />
              <div v-if="isDisabled[checkins[engagement.engagement.name].name]">Checked-Out</div>
              <div v-else>Check-Out</div>
            </div>
          </button>
          <Dialog :options="{
            title: 'Confirm',
            message: 'Are you sure you want to Check-In?',
            size: 'xl',
            actions: [
              {
                label: 'Confirm',
                variant: 'solid',
                onClick: () => {
                  checkin(selectedEngagement);
                },
              },
              {
                label: 'Cancel',
                variant: 'subtle',
                onClick: () => {
                  confirmCheckin = false;
                },
              },
            ],
          }" v-model="confirmCheckin" />
          <Dialog :options="{
            title: 'Confirm',
            message: 'Are you sure you want to Check-Out?',
            size: 'xl',
            actions: [
              {
                label: 'Confirm',
                variant: 'solid',
                onClick: () => {
                  checkout(selectedEngagement);
                },
              },
              {
                label: 'Cancel',
                variant: 'subtle',
                onClick: () => {
                  confirmCheckout = false;
                },
              },
            ],
          }" v-model="confirmCheckout" />
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="dashboard.data && notCaregiver" class="flex items-center justify-center min-h-screen">
    <div class="bg-gray-200 p-8 rounded-md text-center">
      No data to display for you. <br />
      Contact support
    </div>
  </div>
  <div v-else class="flex items-center justify-center min-h-screen">
    <div class="bg-gray-200 p-8 rounded-md">Loading...</div>
  </div>
  <div v-if="noActiveEngagements" class="flex items-center justify-center">
    <div class="bg-gray-200 p-8 rounded-md text-center">No Active Patients Found</div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { FeatherIcon, Badge, Avatar, createResource, Dialog } from 'frappe-ui';
import { session } from '../data/session';
import { dayFormatter, longDateFormatter, isDateInRange } from '../utils';


const dashboard = reactive({
  data: null,
});

// Hamburger parts
let scrollPosition;
let mobile;
let mobileNav = ref(false);
let windowWidth;

let confirmCheckin = ref(false);
let confirmCheckout = ref(false);

let selectedEngagement;
let isDisabled = reactive({});
let checkins = {};
let notCaregiver = ref(false);
let noActiveEngagements = ref(false);

function toggleMobileNav() {
  mobileNav.value = !mobileNav.value;
}

let dashboardResponse;

// API call to fetch dashboard data
async function apiCall() {
  try {
    dashboardResponse = createResource({
      url: '/api/method/wellnest.api.dashboard',
      auto: true,
    });
    await dashboardResponse.promise;
    dashboard.data = dashboardResponse.data;


    // if engagements is a blank array
    if (Array.isArray(dashboard.data.engagements) && dashboard.data.engagements.length === 0) {
      noActiveEngagements.value = true;
      return;
    }

    // Couldn't find caregiver data for logged in user
    if (!dashboard.data.engagements && dashboard.data.message) {
      notCaregiver.value = true;
      return;
    }

    // For all other edge cases
    if (!dashboard.data || !Array.isArray(dashboard.data.engagements)) {
      console.warn('No valid engagements data found.');
      checkins = {};
      return;
    }

    checkins = Object.fromEntries(dashboard.data.engagements.map(({ engagement, todaysCheckin }) => [engagement.name, todaysCheckin]));

    for (let obj of dashboard.data.engagements) {
      if (obj.todaysCheckin) {
        isDisabled[obj.todaysCheckin.name] = !!obj.todaysCheckin.check_out_date_and_time;
      }
    }
  } catch (error) {
    console.error('API call failed:', error);
    dashboard = null;
  }
}

// Open the check-in dialog
function openCheckinDialog(engagement) {
  confirmCheckin.value = true;
  selectedEngagement = engagement;
}

// Open the check-out dialog
function openCheckoutDialog(engagement) {
  confirmCheckout.value = true;
  selectedEngagement = engagement;
}

// Check-in function
async function checkin(engagementId) {
  try {
    if (!checkins || !checkins[engagementId]) {
      const caregiverName = dashboard?.data?.caregiver?.name || '';
      const response = createResource({
        url: `/api/method/wellnest.api.createDailyRecord?engagement=${engagementId}&caregiver=${caregiverName}`,
        auto: true,
      });
      await response.promise;

      checkins = checkins || {};
      checkins[engagementId] = response.data;
    } else {
      alert('Already Checked in today');
    }

    dashboard.data = await dashboardResponse?.reload();

    confirmCheckin.value = false;
  } catch (error) {
    console.error('Check-in failed:', error);
  }
}

// Check-out function
async function checkout(engagementId) {
  try {
    if (!checkins || !checkins[engagementId]) {
      alert('You have not checked in');
      return;
    }

    const checkin = checkins[engagementId];
    const update = createResource({
      url: `/api/method/wellnest.api.checkout?record=${checkin.name}`,
      auto: true,
    });
    await update.promise;

    apiCall();
    confirmCheckout.value = false;
  } catch (error) {
    console.error('Check-out failed:', error);
  }
}

// Initial API call to fetch data
apiCall();
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
