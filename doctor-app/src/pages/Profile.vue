<template>
  <!-- Loading state -->
  <div v-if="profileData?.loading" class="w-full min-h-screen flex items-center justify-center bg-[#f5f7fb]">
    <div class="text-center p-8">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-teal-500 border-t-transparent mx-auto mb-4" role="status">
        <span class="sr-only">Loading...</span>
      </div>
      <div class="text-gray-500 font-semibold">Loading doctor profile...</div>
    </div>
  </div>

  <!-- Error state: non-Practitioner user -->
  <div v-else-if="loadError" class="w-full min-h-screen flex items-center justify-center bg-[#f5f7fb]">
    <div class="text-center p-8 max-w-[480px]">
      <div class="mb-4 text-6xl">🚫</div>
      <h3 class="text-2xl font-bold text-gray-900 mb-3">Access Denied</h3>
      <p class="text-gray-500 mb-6">{{ loadError }}</p>
      <Button variant="solid" theme="red" @click="logout">Logout</Button>
    </div>
  </div>

  <!-- Normal profile view -->
  <div v-else class="w-full min-h-screen py-6 md:py-10 px-4 md:px-8 bg-[#f5f7fb]">
    <div class="max-w-7xl mx-auto">
      <!-- ================= PAGE HEADER ================= -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div>
          <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-1">Doctor Profile</h2>
          <div class="text-gray-500 text-sm md:text-base">Comprehensive doctor profile, documents, fees, digital signature, and editable practice details.</div>
        </div>

        <div class="flex items-center gap-3">
          <Button variant="solid" class="edit-profile-btn" @click="editProfile"> Edit Profile </Button>

          <Button variant="solid" theme="red" @click="logout"> Logout </Button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- ================= LEFT COLUMN ================= -->
        <div class="lg:col-span-5 space-y-6">
          <!-- Profile card -->
          <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
            <div class="p-6 text-center">
              <div class="mb-4 flex justify-center">
                <img
                  v-if="profileData?.data?.doctor?.photo"
                  :src="profileData.data.doctor.photo"
                  class="rounded-full w-24 h-24 object-cover border-2 border-gray-100 shadow-sm"
                  alt="Doctor photo"
                  @error="imageLoadError = true"
                  v-show="!imageLoadError"
                />
                <div v-if="!profileData?.data?.doctor?.photo || imageLoadError" class="rounded-full bg-amber-400 text-gray-900 font-bold flex items-center justify-center w-24 h-24 text-2xl shadow-sm">
                  {{ profileData?.data?.doctor?.first_name?.charAt(0) }}{{ profileData?.data?.doctor?.last_name?.charAt(0) }}
                </div>
              </div>

              <h4 class="text-xl font-bold text-gray-900 mb-1">
                {{ profileData?.data?.doctor?.full_name }}
              </h4>

              <div class="text-teal-600 font-semibold text-sm">
                {{ profileData?.data?.doctor?.doctor_type }}
              </div>

              <div class="text-gray-500 text-sm mb-4">
                {{ profileData?.data?.doctor?.city }}
              </div>

              <div class="w-full bg-gray-200 rounded-full h-2 mb-2 overflow-hidden">
                <div class="bg-emerald-500 h-full transition-all duration-300 rounded-full" :style="{ width: (profileData?.data?.doctor?.profile_completion_percent || 0) + '%' }"></div>
              </div>

              <div class="text-gray-500 text-xs">Profile completion {{ profileData?.data?.doctor?.profile_completion_percent || 92 }}%</div>
            </div>
          </Card>

          <!-- Personal & account details -->
          <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
            <div class="p-6">
              <h5 class="text-lg font-bold text-gray-900 mb-4">Personal &amp; account details</h5>

              <div class="divide-y divide-gray-100">
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Gender</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ profileData?.data?.doctor?.gender || 'Not Available' }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Email</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ profileData?.data?.doctor?.email || 'Not Available' }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Mobile</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ profileData?.data?.doctor?.mobile || 'Not Available' }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Account status</span>
                  <span class="font-semibold text-sm capitalize" :class="profileData?.data?.doctor?.account_status === 'active' ? 'text-emerald-600' : 'text-gray-500'">
                    {{ profileData?.data?.doctor?.account_status || 'Not Available' }}
                  </span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Telemedicine certified</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ profileData?.data?.doctor?.telemedicine_certified ? 'Yes' : 'No' }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">HPR verified</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ profileData?.data?.doctor?.hpr_verified ? 'Yes' : 'No' }}</span>
                </div>
              </div>
            </div>
          </Card>

          <!-- Consultation fees -->
          <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
            <div class="p-6">
              <h5 class="text-lg font-bold text-gray-900 mb-4">Consultation fees</h5>

              <div class="divide-y divide-gray-100">
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Normal Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm">₹{{ profileData?.data?.doctor?.normal_charge }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Emergency Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm">₹{{ profileData?.data?.doctor?.emergency_charge }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Priority Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm">₹{{ profileData?.data?.doctor?.priority_charge }}</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <!-- === RIGHT COLUMN === -->
        <div class="lg:col-span-7 space-y-6">
          <!-- Biography -->
          <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
            <div class="p-6">
              <h5 class="text-lg font-bold text-gray-900 mb-3">Biography</h5>

              <p class="text-gray-500 text-sm leading-relaxed mb-6">
                {{ profileData?.data?.doctor?.professional_summary || 'No biography available.' }}
              </p>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Qualification</span>
                  {{ profileData?.data?.doctor?.qualification || 'Not Available' }}
                </div>
                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Experience</span>
                  {{ profileData?.data?.doctor?.experience_years }} years experience
                </div>
                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Council Registration</span>
                  {{ profileData?.data?.doctor?.council_name }}: {{ profileData?.data?.doctor?.registration_no }}
                </div>
                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Languages</span>
                  {{ profileData?.data?.doctor?.languages_known?.length ? profileData.data.doctor.languages_known.map((lang) => lang.spoken_language_option).join(', ') : 'Not Available' }}
                </div>
                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100 sm:col-span-2">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Availability</span>
                  {{ profileData?.data?.doctor?.availability_days?.length ? profileData.data.doctor.availability_days.map((d) => d.day).join(', ') : 'Not Available' }}
                </div>
              </div>
            </div>
          </Card>

          <div class="grid grid-cols-1 gap-6">
            <!-- Awards and education -->
            <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
              <div class="p-6">
                <h5 class="text-lg font-bold text-gray-900 mb-3">Awards and education</h5>
                <ul class="list-disc list-inside space-y-2 text-sm text-gray-700">
                  <li v-for="(item, idx) in profileData?.data?.doctor?.awards_and_education" :key="item || idx">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </Card>

            <!-- Documents -->
            <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
              <div class="p-6">
                <h5 class="text-lg font-bold text-gray-900 mb-4">Documents</h5>

                <div v-if="profileData?.data?.doctor?.registration_letter">
                  <div
                    class="document-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 border border-gray-200 rounded-xl bg-white hover:shadow-md transition-shadow duration-200"
                  >
                    <div class="flex items-center gap-4 min-w-0">
                      <div class="document-icon w-12 h-12 flex items-center justify-center bg-blue-50 text-blue-600 rounded-xl shrink-0">
                        <FeatherIcon name="file-text" class="w-6 h-6 text-blue-600" />
                      </div>

                      <div class="document-info min-w-0">
                        <div class="document-title text-base font-bold text-gray-900 mb-0.5">Registration Letter</div>

                        <div class="document-name text-sm text-gray-500 truncate">
                          {{ profileData.data.doctor.registration_letter.split('/').pop() }}
                        </div>
                      </div>
                    </div>

                    <Button class="view-btn shrink-0" @click="openDocument(profileData.data.doctor.registration_letter)">
                      <FeatherIcon name="eye" class="w-4 h-4 mr-1" />
                      <span>View</span>
                    </Button>
                  </div>
                </div>

                <div v-else class="text-gray-500 text-sm">No documents uploaded yet.</div>
              </div>
            </Card>
          </div>
        </div>
      </div>

      <div class="text-center text-gray-400 text-xs mt-10 pb-6">CareYogi Doctor App v1.0 prototype. Designed for doctor feedback, not clinical production use.</div>
    </div>
  </div>

  <!-- Edit profile modal -->
  <div v-if="showEditProfile" class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="closeEditProfile">
    <div class="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="flex justify-between items-center p-6 border-b border-gray-200">
        <h4 class="text-xl font-bold text-gray-900">Edit profile</h4>
        <button class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors" @click="closeEditProfile" aria-label="Close">
          <FeatherIcon name="x" class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <div class="p-6 overflow-y-auto space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Qualification</label>
            <input
              v-model="editForm.qualification"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              placeholder="e.g. MBBS, MD"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Experience (years)</label>
            <input
              v-model="editForm.experience_years"
              type="number"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              placeholder="e.g. 12"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Council name</label>
            <input
              v-model="editForm.council_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              placeholder="e.g. Delhi Medical Council"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Registration number</label>
            <input
              v-model="editForm.registration_no"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              placeholder="e.g. DMC/R/04821"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
            <select v-model="editForm.gender" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500">
              <option value="">Select gender</option>
              <option value="Female">Female</option>
              <option value="Male">Male</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="editForm.email"
              type="email"
              placeholder="e.g. doctor@example.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mobile</label>
            <input
              v-model="editForm.mobile"
              type="tel"
              placeholder="e.g. 9876543210"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Account status</label>
            <input
              :value="profileData?.data?.doctor?.account_status || 'Not Available'"
              type="text"
              disabled
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-100 text-gray-500 cursor-not-allowed"
            />
            <div class="text-xs text-gray-500 mt-1">Account status can only be changed by an administrator.</div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1"> Languages known </label>
            <input
              v-model="editForm.languages_known"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              placeholder="e.g. English, Hindi, Kumaoni"
            />
            <div class="text-xs text-gray-500 mt-1">Separate multiple languages with commas.</div>
          </div>

          <div class="sm:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Biography</label>
            <textarea
              v-model="editForm.professional_summary"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              rows="4"
              placeholder="Short professional summary"
            ></textarea>
          </div>
        </div>
      </div>

      <div class="flex justify-end p-6 border-t border-gray-200 bg-gray-50">
        <Button variant="solid" class="save-profile-btn" @click="saveProfile"> Save profile </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { FeatherIcon, Badge, Avatar, createResource } from 'frappe-ui';
import { session } from '../data/session';
import router from '@/router';

function formatDateOnly(dateString) {
  if (!dateString) return 'Not Available';
  return dateString.split(' ')[0];
}

const state = reactive({
  index: 0,
  tabs: [{ label: 'General' }, { label: 'Ratings' }],
});

const imageLoadError = ref(false);

// Tracks whether the profile failed to load (e.g. non-practitioner user).
// When set, the template shows an Access Denied screen instead of blank/broken content.
const loadError = ref(null);
const totalRatings = ref(0);

const profileData = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.doctor_profile',
  auto: true,
  onSuccess(data) {
    const ratings = data?.doctor?.ratings;
    if (Array.isArray(ratings) && ratings.length > 0) {
      const sum = ratings.reduce((acc, rating) => acc + (rating.rating / 2) * 10, 0);
      totalRatings.value = sum / ratings.length;
    } else {
      totalRatings.value = 0;
    }
  },
  onError(error) {
    console.error('API call failed:', error);
    const serverMessage = error?.messages?.[0] || error?.message || '';
    if (serverMessage.toLowerCase().includes('practitioner not found')) {
      loadError.value = 'Your account is not linked to a Practitioner record. Please contact the administrator to set up your doctor profile.';
    } else {
      loadError.value = 'Failed to load profile. Please try again or contact support.';
    }
    totalRatings.value = 0;
  },
});

function logout() {
  session.logout.submit();
}

function openDocument(filePath) {
  if (!filePath) return;
  window.open(encodeURI(filePath), '_blank');
}

// Edit profile modal

const showEditProfile = ref(false);

const editForm = reactive({
  professional_summary: '',
  qualification: '',
  experience_years: '',
  registration_no: '',
  council_name: '',
  languages_known: '',
  gender: '',
  email: '',
  mobile: '',
});

const updateProfileResource = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.update_doctor_profile',
});

function editProfile() {
  const doctor = profileData?.data?.doctor;

  editForm.professional_summary = doctor?.professional_summary || '';
  editForm.qualification = doctor?.qualification || '';
  editForm.experience_years = doctor?.experience_years || '';
  editForm.registration_no = doctor?.registration_no || '';
  editForm.council_name = doctor?.council_name || '';
  editForm.languages_known = doctor?.languages_known?.length ? doctor.languages_known.map((l) => l.spoken_language_option).join(', ') : '';
  editForm.gender = doctor?.gender || '';
  editForm.email = doctor?.email || '';
  editForm.mobile = doctor?.mobile || '';

  showEditProfile.value = true;
}

function closeEditProfile() {
  showEditProfile.value = false;
}

async function saveProfile() {
  const languagesArray = editForm.languages_known
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  try {
    await updateProfileResource.submit({
      professional_summary: editForm.professional_summary,
      qualification: editForm.qualification,
      experience_years: editForm.experience_years,
      registration_no: editForm.registration_no,
      council_name: editForm.council_name,
      languages_known: languagesArray,
      gender: editForm.gender,
      email: editForm.email,
      mobile: editForm.mobile,
    });

    // Reflect the change immediately
    if (profileData?.data?.doctor) {
      profileData.data.doctor.professional_summary = editForm.professional_summary;
      profileData.data.doctor.qualification = editForm.qualification;
      profileData.data.doctor.experience_years = editForm.experience_years;
      profileData.data.doctor.registration_no = editForm.registration_no;
      profileData.data.doctor.council_name = editForm.council_name;
      profileData.data.doctor.languages_known = languagesArray.map((lang) => ({ spoken_language_option: lang }));
      profileData.data.doctor.gender = editForm.gender;
      profileData.data.doctor.email = editForm.email;
      profileData.data.doctor.mobile = editForm.mobile;
    }

    showEditProfile.value = false;
  } catch (err) {
    console.error('Failed to save profile:', err);
  }
}
</script>
