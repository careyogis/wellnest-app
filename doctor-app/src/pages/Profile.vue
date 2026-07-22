<template>
  <div class="container-fluid min-vh-100 py-5" style="background: #f5f7fb">
    <div class="row justify-content-center">
      <div class="col-lg-9">
        <Card class="shadow-lg border-0" style="border-radius: 20px">
          <div class="p-5">
            <div class="d-flex justify-content-between align-items-center mb-5">
              <div class="d-flex align-items-center">
                <img src="@/assets/images/logo-01.png" style="height: 55px" class="me-3" />

                <div>
                  <div class="fw-bold fs-5">CareYogi Doctor</div>

                  <div class="text-muted small">Doctor Portal</div>
                </div>
              </div>

              <div class="d-flex gap-2">
                <Button variant="outline"> Edit Profile </Button>

                <Button variant="solid" theme="red" @click="logout"> Logout </Button>
              </div>
            </div>

            <hr class="mb-5" />

            <!-- ================= HEADER ================= -->

            <div class="text-center">
              <div class="rounded-circle bg-warning text-dark fw-bold d-inline-flex align-items-center justify-content-center" style="width: 110px; height: 110px; font-size: 38px">
                {{ profileData?.data?.doctor?.first_name?.charAt(0) }}{{ profileData?.data?.doctor?.last_name?.charAt(0) }}
              </div>

              <h2 class="fw-bold mt-4 mb-2">
                {{ profileData?.data?.doctor?.full_name }}
              </h2>

              <div class="text-muted fs-5">Orthopaedic Surgeon</div>

              <div class="mt-3 text-warning fs-5">
                <i class="bi bi-star-fill"></i>
                <i class="bi bi-star-fill"></i>
                <i class="bi bi-star-fill"></i>
                <i class="bi bi-star-fill"></i>
                <i class="bi bi-star-fill"></i>
              </div>
            </div>

            <hr class="my-5" />

            <!-- ================= ABOUT ================= -->

            <h3 class="mb-3">About</h3>

            <p class="text-muted">
              Experienced Orthopaedic Surgeon with more than 20 years of clinical practice in trauma care, joint replacement and rehabilitation. Dedicated to providing compassionate post-discharge
              patient care.
            </p>

            <hr class="my-5" />

            <!-- ================= CONTACT ================= -->

            <h3 class="mb-4">Contact Information</h3>

            <div class="row">
              <div class="col-md-6 mb-4">
                <div class="text-muted small">Phone</div>
                <div class="fw-semibold fs-5">
                  {{ profileData?.data?.doctor?.mobile }}
                </div>
              </div>

              <div class="col-md-6 mb-4">
                <div class="text-muted small">Email</div>
                <div class="fw-semibold fs-5">
                  {{ profileData?.data?.doctor?.email }}
                </div>
              </div>

              <div class="col-md-6 mb-4">
                <div class="text-muted small">Hospital</div>
                <div class="fw-semibold fs-5">CareYogi Medical Centre</div>
              </div>

              <div class="col-md-6 mb-4">
                <div class="text-muted small">Location</div>
                <div class="fw-semibold fs-5">New Delhi, India</div>
              </div>
            </div>

            <hr class="my-5" />

            <!-- ================= PROFESSIONAL DETAILS ================= -->

            <h3 class="mb-4">Professional Details</h3>

            <div class="row">
              <div class="col-md-6 mb-4">
                <div class="text-muted small">Account Status</div>
                <div class="fw-semibold fs-5">
                  {{ profileData?.data?.doctor?.account_status }}
                </div>
              </div>

              <div class="col-md-6 mb-4">
                <div class="text-muted small">Experience</div>
                <div class="fw-semibold fs-5">{{ profileData?.data?.doctor?.experience_years }} Years</div>
              </div>

              <div class="col-md-6 mb-4">
                <div class="text-muted small">Qualification</div>
                <div class="fw-semibold fs-5">MBBS, MS (Orthopaedics)</div>
              </div>

              <div class="col-md-6 mb-4">
                <div class="text-muted small">Specialization</div>
                <div class="fw-semibold fs-5">Orthopaedics & Trauma</div>
              </div>

              <div class="col-md-6 mb-4">
                <div class="text-muted small">Languages</div>
                <div class="fw-semibold fs-5">
                  {{ profileData?.data?.doctor?.languages_known?.length ? profileData.data.doctor.languages_known.join(', ') : 'Not Available' }}
                </div>
              </div>
            </div>

            <hr class="my-5" />

            <!-- ================= AVAILABILITY ================= -->

            <h3 class="mb-4">Availability</h3>

            <div class="row">
              <div class="col-md-6 mb-3">
                <Card class="shadow-sm border-0 h-100">
                  <div class="p-4">
                    <div class="text-muted small">Consultation Days</div>

                    <div class="fw-bold fs-5 mt-2">
                      {{ profileData?.data?.doctor?.availability_days?.length ? profileData.data.doctor.availability_days.join(', ') : 'Not Available' }}
                    </div>
                  </div>
                </Card>
              </div>

              <div class="col-md-6 mb-3">
                <Card class="shadow-sm border-0 h-100">
                  <div class="p-4">
                    <div class="text-muted small">Timings</div>

                    <div class="fw-bold fs-5 mt-2">9:00 AM – 5:00 PM</div>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        </Card>
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
