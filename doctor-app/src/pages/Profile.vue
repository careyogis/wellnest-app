<template>
  <!-- Loading state -->
  <div v-if="profileData?.loading" class="container-fluid min-vh-100 d-flex align-items-center justify-content-center" style="background: #f5f7fb">
    <div class="text-center p-5">
      <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem">
        <span class="visually-hidden">Loading...</span>
      </div>
      <div class="text-muted fw-semibold">Loading doctor profile...</div>
    </div>
  </div>

  <!-- Error state: non-Practitioner user -->
  <div v-else-if="loadError" class="container-fluid min-vh-100 d-flex align-items-center justify-content-center" style="background: #f5f7fb">
    <div class="text-center p-5" style="max-width: 480px">
      <div class="mb-4" style="font-size: 56px">🚫</div>
      <h3 class="fw-bold mb-3">Access Denied</h3>
      <p class="text-muted mb-4">{{ loadError }}</p>
      <Button variant="solid" theme="red" @click="logout">Logout</Button>
    </div>
  </div>

  <!-- Normal profile view -->
  <div v-else class="container-fluid min-vh-100 py-4 py-md-5" style="background: #f5f7fb">
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

            <!-- Personal & account details -->
            <Card class="shadow-sm border-0 mb-4">
              <div class="p-4">
                <h5 class="fw-bold mb-3">Personal &amp; account details</h5>

                <div class="d-flex justify-content-between py-2 border-bottom">
                  <span class="text-muted">Gender</span>
                  <span class="fw-semibold">{{ profileData?.data?.doctor?.gender || 'Not Available' }}</span>
                </div>
                <div class="d-flex justify-content-between py-2 border-bottom">
                  <span class="text-muted">Email</span>
                  <span class="fw-semibold">{{ profileData?.data?.doctor?.email || 'Not Available' }}</span>
                </div>
                <div class="d-flex justify-content-between py-2 border-bottom">
                  <span class="text-muted">Mobile</span>
                  <span class="fw-semibold">{{ profileData?.data?.doctor?.mobile || 'Not Available' }}</span>
                </div>
                <div class="d-flex justify-content-between py-2 border-bottom">
                  <span class="text-muted">Account status</span>
                  <span class="fw-semibold text-capitalize" :class="profileData?.data?.doctor?.account_status === 'active' ? 'text-success' : 'text-muted'">
                    {{ profileData?.data?.doctor?.account_status || 'Not Available' }}
                  </span>
                </div>
                <div class="d-flex justify-content-between py-2 border-bottom">
                  <span class="text-muted">Telemedicine certified</span>
                  <span class="fw-semibold">{{ profileData?.data?.doctor?.telemedicine_certified ? 'Yes' : 'No' }}</span>
                </div>
                <div class="d-flex justify-content-between py-2">
                  <span class="text-muted">HPR verified</span>
                  <span class="fw-semibold">{{ profileData?.data?.doctor?.hpr_verified ? 'Yes' : 'No' }}</span>
                </div>
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

          <!-- === RIGHT COLUMN === -->
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
                      {{ profileData?.data?.doctor?.languages_known?.length ? profileData.data.doctor.languages_known.map((lang) => lang.spoken_language_option).join(', ') : 'Not Available' }}
                    </div>
                  </div>
                  <div class="col-12 col-sm-6">
                    <div class="bg-light rounded p-3">
                      {{ profileData?.data?.doctor?.availability_days?.length ? profileData.data.doctor.availability_days.map((d) => d.day).join(', ') : 'Not Available' }}
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
              <div class="col-12">
                <Card class="shadow-sm border-0 h-100">
                  <div class="p-4">
                    <h5 class="fw-bold mb-3">Documents</h5>

                    <div v-if="profileData?.data?.doctor?.registration_letter">
                      <div class="document-card">
                        <div class="document-icon">
                          <i class="bi bi-file-earmark-pdf-fill"></i>
                        </div>

                        <div class="document-info">
                          <div class="document-title">Registration Letter</div>

                          <div class="document-name">
                            {{ profileData.data.doctor.registration_letter.split('/').pop() }}
                          </div>
                        </div>

                        <Button class="view-btn" @click="openDocument(profileData.data.doctor.registration_letter)">
                          <i class="bi bi-eye-fill me-1"></i>
                          <span>View</span>
                        </Button>
                      </div>
                    </div>

                    <div v-else class="text-muted small">No documents uploaded yet.</div>
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

  <!-- Edit profile modal -->
  <div v-if="showEditProfile" class="edit-profile-overlay" @click.self="closeEditProfile">
    <div class="edit-profile-modal">
      <div class="d-flex justify-content-between align-items-center p-4 border-bottom">
        <h4 class="fw-bold mb-0">Edit profile</h4>
        <button class="btn-close-custom" @click="closeEditProfile" aria-label="Close">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <div class="p-4">
        <div class="row g-3">
          <div class="col-12 col-sm-6">
            <label class="form-label text-muted">Qualification</label>
            <input v-model="editForm.qualification" type="text" class="form-control" placeholder="e.g. MBBS, MD" />
          </div>

          <div class="col-12 col-sm-6">
            <label class="form-label text-muted">Experience (years)</label>
            <input v-model="editForm.experience_years" type="number" min="0" class="form-control" placeholder="e.g. 12" />
          </div>

          <div class="col-12 col-sm-6">
            <label class="form-label text-muted">Council name</label>
            <input v-model="editForm.council_name" type="text" class="form-control" placeholder="e.g. Delhi Medical Council" />
          </div>

          <div class="col-12 col-sm-6">
            <label class="form-label text-muted">Registration number</label>
            <input v-model="editForm.registration_no" type="text" class="form-control" placeholder="e.g. DMC/R/04821" />
          </div>

          <div class="col-12">
            <label class="form-label text-muted">Languages known</label>
            <input v-model="editForm.languages_known" type="text" class="form-control" placeholder="e.g. English, Hindi, Kumaoni" />
            <div class="form-text">Separate multiple languages with commas.</div>
          </div>

          <div class="col-12">
            <label class="form-label text-muted">Biography</label>
            <textarea v-model="editForm.professional_summary" class="form-control" rows="4" placeholder="Short professional summary"></textarea>
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-end p-4 border-top">
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
  window.open(filePath, '_blank');
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
  editForm.languages_known = doctor?.languages_known?.length
    ? doctor.languages_known.map((l) => l.spoken_language_option).join(', ')
    : '';

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
    });

    if (profileData?.data?.doctor) {
      profileData.data.doctor.professional_summary = editForm.professional_summary;
      profileData.data.doctor.qualification = editForm.qualification;
      profileData.data.doctor.experience_years = editForm.experience_years;
      profileData.data.doctor.registration_no = editForm.registration_no;
      profileData.data.doctor.council_name = editForm.council_name;
      profileData.data.doctor.languages_known = languagesArray.map((lang) => ({ spoken_language_option: lang }));
    }

    showEditProfile.value = false;
  } catch (err) {
    console.error('Failed to save profile:', err);
  }
}




</script>
