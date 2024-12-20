<template>
  <div v-if="!profileData.loading && profileData.data">
    <CaregiverNavbar title="Profile" />
    <div class="my-3 flex flex-col items-center">
      <Avatar class="flex-auto w-20 h-20 mb-2.5" :shape="'circle'" :image="profileData.data.caregiver.passport_size_photo" label="EY" size="3xl" />
      <div class="text-xl text-[#070707] font-semibold">
        {{ profileData.data.caregiver.full_name }}
      </div>
      <div>
        {{ profileData.data.caregiver.caregiver_type }}
      </div>
      <div>
        Member Since:
        {{ shortDateFormatter(profileData.data.caregiver.creation) }}
      </div>
    </div>

    <Tabs class="bro" v-model="state.index" :tabs="state.tabs">
      <template #default="{ tab }">
        <div class="p-5">
          <div>
            <div v-if="state.index === 0">
              <div class="mb-7">
                <div class="text-xl text-[#070707] font-semibold mb-3">Contact Information</div>
                <div class="mb-3 flex gap-2">
                  <FeatherIcon class="w-4" name="phone" />
                  <div>
                    {{ profileData.data.caregiver.phone_number }}
                  </div>
                </div>
                <div class="flex gap-2">
                  <FeatherIcon class="w-4 mt-0.5" name="mail" />
                  <div>
                    {{ profileData.data.caregiver.email }}
                  </div>
                </div>
              </div>
              <!-- AGENCY SECTION -->
              <div v-if="profileData.data.agency_data" class="agencyDetails mb-7">
                <div class="text-xl text-[#070707] font-semibold mb-3">Agency Details</div>
                <div class="mb-3 flex gap-2">
                  <FeatherIcon class="w-5" name="user" />
                  <div>
                    {{ profileData.data.agency_data.supplier_name }}
                  </div>
                </div>
                <div class="mb-3 flex gap-2">
                  <FeatherIcon class="w-4" name="phone" />
                  <div>
                    {{ profileData.data.agency_contact.phone }}
                  </div>
                </div>
                <div class="flex gap-2">
                  <FeatherIcon class="w-4 self-start mt-1" name="map-pin" />
                  <p>
                    {{ profileData.data.agency_contact.address_line1 }} <br />
                    {{ profileData.data.agency_contact.address_line2 }} <br />
                    {{ profileData.data.agency_contact.city }} <br />
                    {{ profileData.data.agency_contact.state }} <br />
                    {{ profileData.data.agency_contact.country }} <br />
                    {{ profileData.data.agency_contact.pincode }}
                  </p>
                </div>
              </div>
              <!-- SPECIALITIES SECTION -->
              <div class="mySpecialities mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">My Specialities</div>
                <div class="whitespace-nowrap overflow-x-auto">
                  <span v-for="specialization in profileData.data.caregiver.proficient_activities" class="mx-1">
                    <Badge :variant="'solid'" size="lg" label="Badge" theme="orange">
                      {{ specialization.activity }}
                    </Badge>
                  </span>
                </div>
              </div>
              <!-- IMPORTANT DOCUMENTS SECTION -->
              <div class="mb-5">
                <div class="text-xl text-[#070707] font-semibold mb-2">Important Documents</div>
              </div>
              <div class="mb-3 flex gap-2" v-if="profileData.data.caregiver.aadhar_photo">
                <FeatherIcon class="w-4" name="paperclip" />
                <a :href="profileData.data.caregiver.aadhar_photo">Aadhar Card</a>
              </div>
              <div class="mb-3 flex gap-2" v-if="profileData.data.caregiver.pan_photo">
                <FeatherIcon class="w-4 -rotate-45" name="paperclip" />
                <a :href="profileData.data.caregiver.pan_photo">Pan Card</a>
              </div>
              <div class="mb-3 flex gap-2" v-if="profileData.data.caregiver.police_verification_certificate">
                <FeatherIcon class="w-4 -rotate-45" name="paperclip" />
                <a :href="profileData.data.caregiver.police_verification_certificate">Police Verification Certificate</a>
              </div>
              <div class="mb-3 flex gap-2" v-if="profileData.data.caregiver.vaccination_certificate">
                <FeatherIcon class="w-4 -rotate-45" name="paperclip" />
                <a :href="profileData.data.caregiver.vaccination_certificate">Vaccination Certificate</a>
              </div>
            </div>

            <!-- RATINGS SECTION -->
            <div v-else-if="state.index === 1">
              <div class="flex justify-between">
                <div class="text-3xl font-semibold">Overall Rating</div>
                <div>
                  <star-rating :read-only="true" :increment="0.01" :rating="totalRatings" :star-size="25" active-color="#DB7706" :show-rating="false"></star-rating>
                </div>
                <!-- <div>
                  {{ totalRatings.toFixed(1) }}
                </div> -->
              </div>
              <div v-for="rating in profileData.data.caregiver.ratings">
                <div class="mt-8 grid grid-cols-8">
                  <Avatar class="" :shape="'circle'" :image="findCustomerImage(rating.rater)" :label="rating.rater" size="xl" />
                  <div class="col-span-7 flex-col">
                    <div class="flex mb-2 items-end gap-2">
                      <div class="text-sm text-[#78abaf] font-semibold">
                        {{ rating.rater }}
                      </div>
                      <div class="text-sm">
                        {{ shortDateFormatter(rating.rating_date) }}
                      </div>
                    </div>
                    <p class="col-span-2 text-sm mb-2">
                      {{ rating.comment }}
                    </p>
                    <star-rating :read-only="true" :increment="0.5" :rating="(rating.rating / 2) * 10" :star-size="15" active-color="#DB7706" :show-rating="false"></star-rating>
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
import { computed, reactive, ref } from 'vue';
import { Tabs, FeatherIcon, Badge, Avatar, createResource } from 'frappe-ui';
import { session } from '../data/session';
import CaregiverNavbar from '../components/CaregiverNavbar.vue';
import Earnings from '../components/Earnings.vue';
import { formatCurrency, shortDateFormatter } from '../utils';
import StarRating from '../components/star-rating.vue';

const state = reactive({
  index: 0,
  tabs: [{ label: 'General' }, { label: 'Ratings' }],
});

let profileData;
let totalRatings = 0;

// Initial API call
apiCall();

async function apiCall() {
  try {
    // Fetch caregiver data
    profileData = createResource({
      url: '/api/method/wellnest.api.profile',
      auto: true,
    });
    await profileData.promise;

    // Check if the data structure is valid
    const ratings = profileData?.data?.caregiver?.ratings;
    if (Array.isArray(ratings) && ratings.length > 0) {
      // Calculate average rating
      totalRatings = ratings.reduce((sum, rating) => sum + (rating.rating / 2) * 10, 0);
      totalRatings = totalRatings / ratings.length;
    } else {
      console.warn('No ratings data available.');
      totalRatings = 0;
    }
  } catch (error) {
    console.error('API call failed:', error);
    profileData = null;
    totalRatings = 0;
  }
}

function findCustomerImage(name) {
  try {
    const customerData = profileData?.data?.customers;
    if (!Array.isArray(customerData)) {
      console.warn('Customer data is not available or invalid.');
      return null;
    }

    const customer = customerData.find((obj) => obj.name === name);
    return customer?.image || null;
  } catch (error) {
    console.error('Error finding customer image:', error);
    return null;
  }
}
</script>
