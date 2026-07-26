<template>
  <div class="container-fluid min-vh-100 py-4 py-md-5" style="background: #f5f7fb">
    <div class="row justify-content-center">
      <div class="col-12 col-xl-11">
        <!-- ================= PAGE HEADER ================= -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
          <div>
            <h2 class="fw-bold mb-1">Doctor Profile</h2>
            <div class="text-muted">Comprehensive doctor profile, documents, fees, digital signature, and editable practice details.</div>
          </div>

          <div class="d-flex gap-2">
            <Button variant="solid" class="edit-profile-btn" @click="editProfile"> Edit Profile </Button>

            <Button variant="solid" theme="red" @click="logout"> Logout </Button>
          </div>
        </div>

        <div class="row g-4">
          <!-- ================= LEFT COLUMN ================= -->
          <div class="col-12 col-lg-5">
            <!-- Profile card -->
            <Card class="shadow-sm border-0 mb-4">
              <div class="p-4 text-center">
                <div class="mb-3 d-flex justify-content-center">
                  <img
                    v-if="profileData?.data?.doctor?.photo"
                    :src="profileData.data.doctor.photo"
                    class="rounded-circle"
                    style="width: 96px; height: 96px; object-fit: cover"
                    alt="Doctor photo"
                    @error="imageLoadError = true"
                    v-show="!imageLoadError"
                  />
                  <div
                    v-if="!profileData?.data?.doctor?.photo || imageLoadError"
                    class="rounded-circle bg-warning text-dark fw-bold d-flex align-items-center justify-content-center"
                    style="width: 96px; height: 96px; font-size: 28px"
                  >
                    {{ profileData?.data?.doctor?.first_name?.charAt(0) }}{{ profileData?.data?.doctor?.last_name?.charAt(0) }}
                  </div>
                </div>

                <h4 class="fw-bold mb-1">
                  {{ profileData?.data?.doctor?.full_name }}
                </h4>

                <div class="text-primary fw-semibold">
                  {{ profileData?.data?.doctor?.doctor_type }}
                </div>

                <div class="text-muted small mb-3">
                  {{ profileData?.data?.doctor?.city }}
                </div>

                <div class="progress mb-2" style="height: 6px">
                  <div class="progress-bar bg-success" role="progressbar" :style="{ width: (profileData?.data?.doctor?.profile_completion_percent || 0) + '%' }"></div>
                </div>

                <div class="text-muted small">Profile completion {{ profileData?.data?.doctor?.profile_completion_percent || 92 }}%</div>
              </div>
            </Card>

            <!-- Consultation fees -->
            <Card class="shadow-sm border-0">
              <div class="p-4">
                <h5 class="fw-bold mb-3">Consultation fees</h5>

                <div class="d-flex justify-content-between py-2 border-bottom">
                  <span class="text-muted">Normal Consultation</span>
                  <span class="fw-semibold">₹{{ profileData?.data?.doctor?.normal_charge }}</span>
                </div>
                <div class="d-flex justify-content-between py-2 border-bottom">
                  <span class="text-muted">Emergency Consultation</span>
                  <span class="fw-semibold">₹{{ profileData?.data?.doctor?.emergency_charge }}</span>
                </div>
                <div class="d-flex justify-content-between py-2">
                  <span class="text-muted">Priority Consultation</span>
                  <span class="fw-semibold">₹{{ profileData?.data?.doctor?.priority_charge }}</span>
                </div>
              </div>
            </Card>
          </div>

          <!-- ================= RIGHT COLUMN ================= -->
          <div class="col-12 col-lg-7">
            <!-- Biography -->
            <Card class="shadow-sm border-0 mb-4">
              <div class="p-4">
                <h5 class="fw-bold mb-3">Biography</h5>

                <p class="text-muted mb-4">
                  {{ profileData?.data?.doctor?.professional_summary || 'No biography available.' }}
                </p>

                <div class="row g-3">
                  <div class="col-12 col-sm-6">
                    <div class="bg-light rounded p-3">
                      {{ profileData?.data?.doctor?.qualification || 'Not Available' }}
                    </div>
                  </div>
                  <div class="col-12 col-sm-6">
                    <div class="bg-light rounded p-3">{{ profileData?.data?.doctor?.experience_years }} years experience</div>
                  </div>
                  <div class="col-12 col-sm-6">
                    <div class="bg-light rounded p-3">{{ profileData?.data?.doctor?.council_name }}: {{ profileData?.data?.doctor?.registration_no }}</div>
                  </div>
                  <div class="col-12 col-sm-6">
                    <div class="bg-light rounded p-3">
                      {{ profileData?.data?.doctor?.languages_known?.length ? profileData.data.doctor.languages_known.map(lang => lang.spoken_language_option).join(', ') : 'Not Available' }}
                    </div>
                  </div>
                  <div class="col-12 col-sm-6">
                    <div class="bg-light rounded p-3">
                      {{ profileData?.data?.doctor?.specializations?.length ? profileData.data.doctor.specializations.join(', ') : 'Not Available' }}
                    </div>
                  </div>
                  <div class="col-12 col-sm-6">
                    <div class="bg-light rounded p-3">
                      {{ profileData?.data?.doctor?.hospitals_worked?.length ? profileData.data.doctor.hospitals_worked.join(', ') : 'Not Available' }}
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            <div class="row g-4">
              <!-- Awards and education -->
              <div class="col-12 col-md-6">
                <Card class="shadow-sm border-0 h-100">
                  <div class="p-4">
                    <h5 class="fw-bold mb-3">Awards and education</h5>
                    <ul class="mb-0 ps-3">
                      <li v-for="(item, idx) in profileData?.data?.doctor?.awards_and_education" :key="idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                </Card>
              </div>

              <!-- Documents -->
              <div class="col-12 col-md-6">
                <Card class="shadow-sm border-0 h-100">
                  <div class="p-4">
                    <h5 class="fw-bold mb-3">Documents</h5>
                    <div class="d-flex flex-column gap-2">
                      <Button v-for="doc in profileData?.data?.doctor?.documents" :key="doc.name" variant="outline" theme="orange" class="w-100" @click="openDocument(doc)">
                        {{ doc.label }}
                      </Button>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        </div>

        <div class="text-center text-muted small mt-5">CareYogi Doctor App v1.0 prototype. Designed for doctor feedback, not clinical production use.</div>
      </div>
    </div>
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
import router from '@/router';

const state = reactive({
  index: 0,
  tabs: [{ label: 'General' }, { label: 'Ratings' }],
});

let profileData;
let totalRatings = 0;

// Initial API call
apiCall();

function logout() {
  session.logout.submit();
}

async function apiCall() {
  try {
    // Fetch caregiver data
    profileData = createResource({
      url: '/api/method/wellnest.api.doctor_profile',
      auto: true,
    });
    await profileData.promise;
    console.log(profileData.data);

    // Check if the data structure is valid
    const ratings = profileData?.data?.doctor?.ratings;
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
