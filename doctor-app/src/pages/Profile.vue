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
      <!-- === PAGE HEADER ===-->
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
        <!-- ==== LEFT COLUMN ====-->
        <div class="lg:col-span-5 space-y-6">
          <!-- Profile card -->
          <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
            <div class="p-6 text-center">
              <div class="mb-4 flex justify-center">
                <div class="relative group w-24 h-24">
                  <img
                    v-if="profileData?.data?.doctor?.photo && !imageLoadError"
                    :src="profileData.data.doctor.photo"
                    class="rounded-full w-24 h-24 object-cover border-2 border-gray-100 shadow-sm"
                    alt="Doctor photo"
                    @error="imageLoadError = true"
                  />

                  <div v-else class="rounded-full bg-amber-400 text-gray-900 font-bold flex items-center justify-center w-24 h-24 text-2xl shadow-sm">
                    {{ profileData?.data?.doctor?.first_name?.charAt(0) }}
                    {{ profileData?.data?.doctor?.last_name?.charAt(0) }}
                  </div>

                  <!-- Edit photo button -->
                  <button
                    type="button"
                    class="absolute inset-0 rounded-full bg-black/50 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                    @click="openPhotoPicker"
                    aria-label="Change profile photo"
                  >
                    <FeatherIcon name="edit-2" class="w-5 h-5" />
                  </button>

                  <input ref="photoInput" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="handlePhotoSelected" />
                </div>
              </div>

              <h4 class="text-xl font-bold text-gray-900 mb-1">
                {{ profileData?.data?.doctor?.full_name }}
              </h4>

              <div class="text-gray-500 text-sm mb-4">
                {{ profileData?.data?.doctor?.city?.replace(/,\s*[^,]+$/, '') }}
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
                  <span class="text-gray-500 text-sm">Date of birth</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ formatDateOnly(profileData?.data?.doctor?.dob) }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Nationality</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ profileData?.data?.doctor?.nationality || 'Not Available' }}</span>
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

          <!-- Address -->
          <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
            <div class="p-6">
              <h5 class="text-lg font-bold text-gray-900 mb-4">Address</h5>

              <div class="divide-y divide-gray-100">
                <div class="flex justify-between gap-4 py-3">
                  <span class="text-gray-500 text-sm">Address Line 1</span>
                  <span class="font-semibold text-gray-900 text-sm text-right">
                    {{ profileData?.data?.doctor?.address_line1 || 'Not Available' }}
                  </span>
                </div>

                <div class="flex justify-between gap-4 py-3">
                  <span class="text-gray-500 text-sm">City</span>
                  <span class="font-semibold text-gray-900 text-sm">
                    {{ profileData?.data?.doctor?.city?.replace(/,\s*[^,]+$/, '') || 'Not Available' }}
                  </span>
                </div>

                <div class="flex justify-between gap-4 py-3">
                  <span class="text-gray-500 text-sm">State</span>
                  <span class="font-semibold text-gray-900 text-sm">
                    {{ profileData?.data?.doctor?.state || 'Not Available' }}
                  </span>
                </div>

                <div class="flex justify-between gap-4 py-3">
                  <span class="text-gray-500 text-sm">Pincode</span>
                  <span class="font-semibold text-gray-900 text-sm">
                    {{ profileData?.data?.doctor?.pincode || 'Not Available' }}
                  </span>
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
                  <span class="text-gray-500 text-sm">Online Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm">₹{{ profileData?.data?.doctor?.online_charge }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Emergency Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm">₹{{ profileData?.data?.doctor?.emergency_charge }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Priority Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm">₹{{ profileData?.data?.doctor?.priority_charge }}</span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">In-Clinic Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm"> ₹{{ profileData?.data?.doctor?.clinic_charge }} </span>
                </div>
                <div class="flex justify-between py-3">
                  <span class="text-gray-500 text-sm">Available For Home Visits?</span>
                  <span class="font-semibold text-gray-900 text-sm">{{ profileData?.data?.doctor?.available_for_home_visits ? 'Yes' : 'No' }}</span>
                </div>
                <div class="flex justify-between py-3"">
                  <span class="text-gray-500 text-sm">Home Visit Consultation</span>
                  <span class="font-semibold text-gray-900 text-sm"> ₹{{ profileData?.data?.doctor?.home_visit_charge }} </span>
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
                <div class="sm:col-span-2 bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-2"> Education History </span>

                  <div v-if="profileData?.data?.doctor?.education_history?.length" class="space-y-2">
                    <div v-for="(education, index) in profileData.data.doctor.education_history" :key="index" class="border border-gray-200 rounded-lg bg-white p-3">
                      <div class="font-medium text-gray-900">
                        {{ education.degree || 'Degree not available' }}
                      </div>

                      <div class="text-gray-500 text-sm">
                        {{ education.institution || 'Institution not available' }}
                      </div>

                      <div v-if="education.year_of_completion" class="text-gray-500 text-xs mt-1">Completed: {{ education.year_of_completion }}</div>
                    </div>
                  </div>

                  <div v-else class="text-gray-500">No education history available.</div>
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Designation </span>
                  {{ profileData?.data?.doctor?.designation || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Specialty </span>
                  {{ profileData?.data?.doctor?.specialty_name || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Super Specialty </span>
                  {{ profileData?.data?.doctor?.super_specialty_name || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Practicing From </span>

                  {{ profileData?.data?.doctor?.practicing_from || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Council Registration </span>
                  {{ profileData?.data?.doctor?.council_name || 'Not Available' }}
                  <span v-if="profileData?.data?.doctor?.registration_no"> · {{ profileData.data.doctor.registration_no }} </span>
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Primary Facility </span>
                  {{ profileData?.data?.doctor?.primary_facility_name || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Languages </span>
                  {{ profileData?.data?.doctor?.languages_known?.length ? profileData.data.doctor.languages_known.map((lang) => lang.spoken_language_option).join(', ') : 'Not Available' }}
                </div>
              </div>
            </div>
          </Card>

          <!-- Availability -->
          <Card class="shadow-sm border border-gray-200 rounded-2xl bg-white">
            <div class="p-6">
              <h5 class="text-lg font-bold text-gray-900 mb-4">Availability</h5>

              <div class="mb-5">
                <span class="text-gray-500 text-xs font-medium uppercase tracking-wide block mb-2">Available Days &amp; Hours</span>

                <div v-if="profileData?.data?.doctor?.availability_days?.length" class="space-y-3">
                  <div v-for="item in profileData.data.doctor.availability_days" :key="item.day" class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                    <div class="text-sm font-semibold text-gray-900 mb-3">
                      {{ item.day }}
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <!-- Online -->
                      <div class="bg-white rounded-lg border border-gray-100 p-3">
                        <span class="text-gray-400 block mb-1 text-xs"> Online </span>

                        <span class="font-medium text-sm text-gray-700">
                          <template v-if="formatTimeDisplay(item.online_from) || formatTimeDisplay(item.online_to)">
                            {{ formatTimeDisplay(item.online_from) || '—' }}
                            –
                            {{ formatTimeDisplay(item.online_to) || '—' }}
                          </template>

                          <template v-else> Not Available </template>
                        </span>
                      </div>

                      <!-- Emergency -->
                      <div class="bg-white rounded-lg border border-gray-100 p-3">
                        <span class="text-gray-400 block mb-1 text-xs"> Emergency </span>

                        <span class="font-medium text-sm text-gray-700">
                          <template v-if="formatTimeDisplay(item.emergency_from) || formatTimeDisplay(item.emergency_to)">
                            {{ formatTimeDisplay(item.emergency_from) || '—' }}
                            –
                            {{ formatTimeDisplay(item.emergency_to) || '—' }}
                          </template>

                          <template v-else> Not Available </template>
                        </span>
                      </div>

                      <!-- In-Clinic -->
                      <div class="bg-white rounded-lg border border-gray-100 p-3">
                        <span class="text-gray-400 block mb-1 text-xs"> In-Clinic </span>

                        <span class="font-medium text-sm text-gray-700">
                          <template v-if="formatTimeDisplay(item.clinic_from) || formatTimeDisplay(item.clinic_to)">
                            {{ formatTimeDisplay(item.clinic_from) || '—' }}
                            –
                            {{ formatTimeDisplay(item.clinic_to) || '—' }}
                          </template>

                          <template v-else> Not Available </template>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="text-gray-500 text-sm">Not Available</div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Registration Valid Upto</span>
                  <span class="text-sm font-semibold text-gray-900">
                    {{ formatDateOnly(profileData?.data?.doctor?.registration_valid_upto) }}
                  </span>
                </div>

                <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Published</span>
                  <span class="text-sm font-semibold text-gray-900">
                    {{ profileData?.data?.doctor?.is_published ? 'Yes' : 'No' }}
                  </span>
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
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                  <div>
                    <h5 class="text-lg font-bold text-gray-900">Documents</h5>

                    <p class="text-sm text-gray-500 mt-1">Upload and manage your professional documents.</p>
                  </div>

                  <button
                    type="button"
                    class="inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-teal-600 text-white text-sm font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
                    :disabled="documentUploading"
                    @click="openDocumentPicker"
                  >
                    <FeatherIcon :name="documentUploading ? 'loader' : 'upload'" class="w-4 h-4" />

                    <span>
                      {{ documentUploading ? 'Uploading...' : 'Upload Document' }}
                    </span>
                  </button>

                  <input ref="documentInput" type="file" class="hidden" @change="handleDocumentSelected" />
                </div>

                <div v-if="documents.length" class="space-y-3">
                  <div
                    v-for="document in documents"
                    :key="document.name"
                    class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 border border-gray-200 rounded-xl bg-white hover:shadow-md transition-shadow"
                  >
                    <div class="flex items-center gap-4 min-w-0">
                      <div class="w-12 h-12 flex items-center justify-center bg-blue-50 text-blue-600 rounded-xl shrink-0">
                        <FeatherIcon name="file-text" class="w-6 h-6" />
                      </div>

                      <div class="min-w-0">
                        <div class="text-base font-semibold text-gray-900 truncate">
                          {{ document.file_name }}
                        </div>

                        <div class="text-xs text-gray-500 mt-1">Professional document</div>
                      </div>
                    </div>

                    <div class="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        class="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-teal-600 text-white text-sm font-medium hover:bg-teal-700 transition-colors whitespace-nowrap shrink-0"
                        @click="openDocument(document.file_url)"
                      >
                        <FeatherIcon name="eye" class="w-4 h-4 shrink-0" />
                        <span class="hidden sm:inline">View</span>
                      </button>

                      <button
                        type="button"
                        class="p-2 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 transition-colors shrink-0"
                        :aria-label="`Delete ${document.file_name}`"
                        :title="`Delete ${document.file_name}`"
                        @click="deleteDocument(document)"
                      >
                        <FeatherIcon name="trash-2" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                <div v-else class="border border-dashed border-gray-300 rounded-xl p-8 text-center">
                  <FeatherIcon name="file-text" class="w-8 h-8 mx-auto text-gray-400 mb-2" />

                  <p class="text-sm font-medium text-gray-700">No documents uploaded yet.</p>

                  <p class="text-xs text-gray-500 mt-1">Upload your registration letter, certificates, or other professional documents.</p>
                </div>
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

      <div class="p-6 overflow-y-auto space-y-6">
        <!-- Personal Information -->
        <div>
          <h5 class="text-base font-bold text-gray-900 mb-3">Personal Information</h5>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                v-model="editForm.title"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="e.g. Dr."
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
              <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
              <input
                v-model="editForm.first_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Middle Name</label>
              <input
                v-model="editForm.middle_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
              <input
                v-model="editForm.last_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
              <input v-model="editForm.dob" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nationality</label>
              <input
                v-model="editForm.nationality"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="e.g. Indian"
              />
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

            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1"> Languages Known </label>

              <Autocomplete :model-value="selectedLanguageOptions" :options="languageOptions" multiple placeholder="Select languages" @update:model-value="updateLanguages" />
              <div class="text-xs text-gray-500 mt-1">Select all languages you speak.</div>

              <div v-if="selectedLanguageOptions.length" class="flex flex-wrap gap-2 mt-2">
                <span
                  v-for="option in selectedLanguageOptions"
                  :key="option.value"
                  class="inline-flex items-center gap-1 pl-3 pr-2 py-1 bg-teal-50 text-teal-700 text-xs font-medium rounded-full border border-teal-200"
                >
                  {{ option.label }}
                  <button type="button" @click="removeLanguage(option)" class="hover:text-teal-900" aria-label="Remove">
                    <FeatherIcon name="x" class="w-3 h-3" />
                  </button>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Address -->
        <div class="border-t border-gray-200 pt-5">
          <h5 class="text-base font-bold text-gray-900 mb-3">Address</h5>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
              <input
                v-model="editForm.address_line1"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">City</label>
              <Autocomplete
                :model-value="
                  editForm.city
                    ? {
                        label: editForm.city.replace(/,\s*[^,]+$/, ''),
                        value: editForm.city,
                      }
                    : null
                "
                :options="cityOptions"
                placeholder="Select city"
                @update:model-value="(option) => (editForm.city = option?.value || '')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">State</label>
              <Autocomplete
                :model-value="stateOptions.find((option) => option.value === editForm.state) || null"
                :options="stateOptions"
                placeholder="Select state"
                @update:model-value="(option) => (editForm.state = option?.value || '')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
              <input
                v-model="editForm.pincode"
                type="text"
                inputmode="numeric"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>
          </div>
        </div>

        <!-- Professional Information -->
        <div class="border-t border-gray-200 pt-5">
          <h5 class="text-base font-bold text-gray-900 mb-3">Professional Information</h5>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-gray-700"> Education History </label>

                <button
                  type="button"
                  class="text-sm font-medium text-blue-600 hover:underline"
                  @click="
                    editForm.education_history.push({
                      degree: '',
                      institution: '',
                      year_of_completion: '',
                    })
                  "
                >
                  + Add Education
                </button>
              </div>

              <div v-if="editForm.education_history.length" class="space-y-3">
                <div v-for="(education, index) in editForm.education_history" :key="index" class="border border-gray-200 rounded-lg p-4">
                  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Degree</label>
                      <Autocomplete
                        :model-value="medicalDegreeOptions.find((option) => option.value === education.degree) || null"
                        :options="medicalDegreeOptions"
                        placeholder="Select degree"
                        @update:model-value="(option) => (education.degree = option?.value || '')"
                      />
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Institution</label>
                      <Autocomplete
                        :model-value="educationalInstitutionOptions.find((option) => option.value === education.institution) || null"
                        :options="educationalInstitutionOptions"
                        placeholder="Search institution"
                        @update:query="
                          (query) => {
                            educationalInstitutionSearchQuery = query;
                            educationalInstitutionResource.fetch();
                          }
                        "
                        @update:model-value="
                          (option) => {
                            education.institution = option?.value || '';
                            educationalInstitutionSearchQuery = '';
                          }
                        "
                      >
                        <template #footer>
                          <div
                            v-if="educationalInstitutionSearchQuery.trim() && !educationalInstitutionResource.loading && educationalInstitutionOptions.length === 0"
                            class="border-t border-gray-200 p-2"
                          >
                            <button type="button" class="w-full text-left px-3 py-2 rounded-md text-sm text-teal-600 hover:bg-teal-50" @click="createInstitution(education)">
                              + Add "{{ educationalInstitutionSearchQuery }}"
                            </button>
                          </div>
                        </template>
                      </Autocomplete>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1"> Year of Completion </label>
                      <input
                        v-model="education.year_of_completion"
                        type="number"
                        placeholder="e.g. 2022"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                      />
                    </div>
                  </div>

                  <button type="button" class="mt-3 text-sm text-red-600 hover:underline" @click="editForm.education_history.splice(index, 1)">Remove</button>
                </div>
              </div>

              <div v-else class="text-sm text-gray-500 border border-dashed border-gray-300 rounded-lg p-3">No education history added.</div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Designation</label>
              <input
                v-model="editForm.designation"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Specialty</label>
              <Autocomplete
                :model-value="specialtyOptions.find((option) => option.value === editForm.specialty) || null"
                :options="specialtyOptions"
                placeholder="Select specialty"
                @update:model-value="(option) => (editForm.specialty = option?.value || '')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Super Specialty</label>
              <Autocomplete
                :model-value="superSpecialtyOptions.find((option) => option.value === editForm.super_specialty) || null"
                :options="superSpecialtyOptions"
                placeholder="Select super specialty"
                @update:model-value="(option) => (editForm.super_specialty = option?.value || '')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"> Practicing From </label>
              <input
                v-model="editForm.practicing_from"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Council Name</label>
              <input
                v-model="editForm.council_name"
                type="text"
                placeholder="e.g. Delhi Medical Council"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Registration Number</label>
              <input
                v-model="editForm.registration_no"
                type="text"
                placeholder="e.g. DMC/R/04821"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Registration Valid Upto</label>
              <input
                v-model="editForm.registration_valid_upto"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Digital Signature URL</label>
              <input
                v-model="editForm.digital_signature_url"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="Signature URL"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"> Primary Facility </label>

              <Autocomplete
                :model-value="hospitalOptions.find((option) => option.value === editForm.primary_facility) || null"
                :options="hospitalOptions"
                placeholder="Search primary facility"
                @update:query="
                  (query) => {
                    hospitalSearchQuery = query;
                    hospitalResource.fetch();
                  }
                "
                @update:model-value="
                  (option) => {
                    editForm.primary_facility = option?.value || '';
                    hospitalSearchQuery = '';
                  }
                "
              >
                <template #footer>
                  <div v-if="hospitalSearchQuery.trim() && !hospitalResource.loading && hospitalOptions.length === 0" class="border-t border-gray-200 p-2">
                    <button type="button" class="w-full text-left px-3 py-2 rounded-md text-sm text-teal-600 hover:bg-teal-50" @click="createHospital">+ Add "{{ hospitalSearchQuery }}"</button>
                  </div>
                </template>
              </Autocomplete>

              <p class="text-xs text-gray-500 mt-1">Search for a hospital. If it is not available, you can add it.</p>
            </div>

            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Professional Summary</label>
              <textarea
                v-model="editForm.professional_summary"
                rows="4"
                placeholder="Short professional summary"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Consultation & Account -->
        <div class="border-t border-gray-200 pt-5">
          <h5 class="text-base font-bold text-gray-900 mb-3">Consultation &amp; Account</h5>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Currency</label>
              <input
                v-model="editForm.currency"
                type="text"
                placeholder="e.g. INR"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Online Consultation Charge</label>
              <input
                v-model="editForm.online_charge"
                type="number"
                min="0"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Emergency Consultation Charge</label>
              <input
                v-model="editForm.emergency_charge"
                type="number"
                min="0"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority Consultation Charge</label>
              <input
                v-model="editForm.priority_charge"
                type="number"
                min="0"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"> In-Clinic Consultation </label>
              <input
                v-model="editForm.clinic_charge"
                type="number"
                min="0"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>
            <div class="flex items-center gap-3 pt-6">
              <input id="available-for-home-visits" v-model="editForm.available_for_home_visits" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
              <label for="available-for-home-visits" class="text-sm font-medium text-gray-700"> Available for Home Visits? </label>
            </div>
            <div :hidden="!editForm.available_for_home_visits">
              <label class="block text-sm font-medium text-gray-700 mb-1"> Home Visit Consultation </label>
              <input
                v-model="editForm.home_visit_charge"
                type="number"
                min="0"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div class="flex items-center gap-3 pt-6">
              <input id="telemedicine-certified" v-model="editForm.telemedicine_certified" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
              <label for="telemedicine-certified" class="text-sm font-medium text-gray-700"> Telemedicine Certified </label>
            </div>

            <div class="flex items-center gap-3">
              <input id="hpr-verified" v-model="editForm.hpr_verified" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
              <label for="hpr-verified" class="text-sm font-medium text-gray-700"> HPR Verified </label>
            </div>

            <div class="flex items-center gap-3">
              <input id="is-published" v-model="editForm.is_published" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
              <label for="is-published" class="text-sm font-medium text-gray-700"> Is Published </label>
            </div>
          </div>
        </div>

        <!-- Availability -->
        <div class="border-t border-gray-200 pt-5">
          <h5 class="text-base font-bold text-gray-900 mb-3">Availability</h5>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">Availability Days &amp; Hours</label>
              <p class="text-xs text-gray-500 mb-3">Select the days you're available, then set hours for each day individually.</p>

              <div class="space-y-3">
                <div v-for="day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']" :key="day" class="border border-gray-200 rounded-lg overflow-hidden">
                  <label class="flex items-center gap-2 p-3 cursor-pointer hover:bg-gray-50">
                    <input type="checkbox" :checked="!!getDayItem(day)" @change="toggleDay(day, $event.target.checked)" class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
                    <span class="text-sm font-medium text-gray-700">{{ day }}</span>
                  </label>

                  <div v-if="getDayItem(day)" class="px-3 pb-4 pt-2 border-t border-gray-100 bg-gray-50">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <!-- Online -->
                      <div class="bg-white border border-gray-200 rounded-lg p-3">
                        <label class="block text-xs font-semibold text-gray-600 mb-2"> Online Hours </label>

                        <div class="flex gap-1.5">
                          <select
                            :value="getHour24(getDayItem(day).online_from)"
                            @change="setDayTime(getDayItem(day), 'online_from', $event.target.value)"
                            class="w-1/3 px-1.5 py-1.5 border border-gray-300 rounded-lg text-xs"
                          >
                            <option value="HH">HH</option>
                            <option v-for="h in 24" :key="h" :value="String(h).padStart(2, '0')">
                              {{ String(h).padStart(2, '0') }}
                            </option>
                          </select>
                          <pre class="text-center text-xs text-gray-600 my-1">  to  </pre>
                          <select
                            :value="getHour24(getDayItem(day).online_to)"
                            @change="setDayTime(getDayItem(day), 'online_to', $event.target.value)"
                            class="w-1/3 px-1.5 py-1.5 border border-gray-300 rounded-lg text-xs"
                          >
                            <option value="HH">HH</option>
                            <option v-for="h in 24" :key="h" :value="String(h).padStart(2, '0')">
                              {{ String(h).padStart(2, '0') }}
                            </option>
                          </select>

                        </div>
                      </div>

                      <!-- Emergency -->
                      <div class="bg-white border border-gray-200 rounded-lg p-3">
                        <label class="block text-xs font-semibold text-gray-600 mb-2"> Emergency Hours </label>

                        <div class="flex gap-1.5">
                          <select
                            :value="getHour24(getDayItem(day).emergency_from)"
                            @change="setDayTime(getDayItem(day), 'emergency_from', $event.target.value)"
                            class="w-1/3 px-1.5 py-1.5 border border-gray-300 rounded-lg text-xs"
                          >
                            <option value="HH">HH</option>
                            <option v-for="h in 24" :key="h" :value="String(h).padStart(2, '0')">
                              {{ String(h).padStart(2, '0') }}
                            </option>
                          </select>
                          <pre class="text-center text-xs text-gray-600 my-1">  to  </pre>
                          <select
                            :value="getHour24(getDayItem(day).emergency_to)"
                            @change="setDayTime(getDayItem(day), 'emergency_to', $event.target.value)"
                            class="w-1/3 px-1.5 py-1.5 border border-gray-300 rounded-lg text-xs"
                          >
                            <option value="HH">HH</option>
                            <option v-for="h in 24" :key="h" :value="String(h).padStart(2, '0')">
                              {{ String(h).padStart(2, '0') }}
                            </option>
                          </select>

                        </div>
                      </div>

                      <!-- In-Clinic -->
                      <div class="bg-white border border-gray-200 rounded-lg p-3">
                        <label class="block text-xs font-semibold text-gray-600 mb-2"> In-Clinic Hours </label>

                        <div class="flex gap-1.5">
                          <select
                            :value="getHour24(getDayItem(day).clinic_from)"
                            @change="setDayTime(getDayItem(day), 'clinic_from', $event.target.value)"
                            class="w-1/3 px-1.5 py-1.5 border border-gray-300 rounded-lg text-xs"
                          >
                            <option value="HH">HH</option>
                            <option v-for="h in 24" :key="h" :value="String(h).padStart(2, '0')">
                              {{ String(h).padStart(2, '0') }}
                            </option>
                          </select>
                          <pre class="text-center text-xs text-gray-600 my-1">  to  </pre>
                          <select
                            :value="getHour24(getDayItem(day).clinic_to)"
                            @change="setDayTime(getDayItem(day), 'clinic_to', $event.target.value)"
                            class="w-1/3 px-1.5 py-1.5 border border-gray-300 rounded-lg text-xs"
                          >
                            <option value="HH">HH</option>
                            <option v-for="h in 24" :key="h" :value="String(h).padStart(2, '0')">
                              {{ String(h).padStart(2, '0') }}
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <button type="button" class="mt-3 text-xs font-medium text-teal-600 hover:underline" @click="copyAvailabilityToSelectedDays(day)">Copy these timings to all selected days</button>
                  </div>
                </div>
              </div>
            </div>
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
import { computed, reactive, ref, watch } from 'vue';
import { FeatherIcon, Badge, Avatar, Autocomplete, FileUploader, createResource } from 'frappe-ui';
import { session } from '../data/session';
import { profileData } from '@/data/doctorProfile';

function formatDateOnly(dateString) {
  if (!dateString) return 'Not Available';
  return dateString.split(' ')[0];
}

function formatTimeOnly(timeString) {
  if (!timeString) return NaN;
  const parts = timeString.split(':');
  const paddedParts = parts.map((part) => part.padStart(2, '0'));
  return parts[0];
}

function formatTimeDisplay(timeString) {
  if (!timeString) return '';

  const parts = timeString.split(':');
  const hours = parseInt(parts[0], 10);

  if (Number.isNaN(hours)) return '';

  return `${String(hours).padStart(2, '0')}00 hrs`;
}

function getHour24(timeString) {
  if (!timeString) return '';
  const hour = parseInt(timeString.split(':')[0], 10);

  if (Number.isNaN(hour)) return '';

  return String(hour).padStart(2, '0');
}

function setDayTime(dayItem, fieldName, value) {
  if (value && value != 'HH')
    dayItem[fieldName] = `${value}`;
  else
    dayItem[fieldName] = NaN;
}

function getDayItem(dayName) {
  return editForm.availability_days.find((item) => item.day === dayName);
}

function toggleDay(dayName, checked) {
  if (checked) {
    editForm.availability_days.push({
      day: dayName,
      online_from: '',
      online_to: '',
      emergency_from: '',
      emergency_to: '',
      clinic_from: '',
      clinic_to: '',
    });
  } else {
    editForm.availability_days = editForm.availability_days.filter((item) => item.day !== dayName);
  }
}

function copyAvailabilityToSelectedDays(sourceDay) {
  const source = getDayItem(sourceDay);

  if (!source) return;

  editForm.availability_days.forEach((dayItem) => {
    if (dayItem.day !== sourceDay) {
      dayItem.online_from = source.online_from || '';
      dayItem.online_to = source.online_to || '';
      dayItem.emergency_from = source.emergency_from || '';
      dayItem.emergency_to = source.emergency_to || '';
      dayItem.clinic_from = source.clinic_from || '';
      dayItem.clinic_to = source.clinic_to || '';
    }
  });
}

function updateLanguages(options) {
  const incoming = Array.isArray(options) ? options : [];

  const existing = selectedLanguageOptions.value || [];

  const merged = [...existing];

  for (const option of incoming) {
    const value = typeof option === 'object' ? option.value : option;

    if (
      !merged.some((item) => {
        const itemValue = typeof item === 'object' ? item.value : item;
        return itemValue === value;
      })
    ) {
      merged.push(typeof option === 'object' ? option : { label: option, value: option });
    }
  }

  selectedLanguageOptions.value = merged;

  editForm.languages_known = merged.map((option) => {
    return typeof option === 'object' ? option.value : option;
  });
}

function removeLanguage(option) {
  selectedLanguageOptions.value = selectedLanguageOptions.value.filter((item) => item.value !== option.value);
  editForm.languages_known = selectedLanguageOptions.value.map((item) => item.value);
}

const imageLoadError = ref(false);
const photoInput = ref(null);
const documentInput = ref(null);
const documentUploading = ref(false);

const selectedLanguageOptions = ref([]);
const isEditingProfile = ref(false);

const totalRatings = computed(() => {
  const ratings = profileData.data?.doctor?.ratings;
  if (Array.isArray(ratings) && ratings.length > 0) {
    const sum = ratings.reduce((acc, rating) => acc + (rating.rating / 2) * 10, 0);
    return sum / ratings.length;
  }
  return 0;
});

const loadError = computed(() => {
  const error = profileData.error;
  if (!error) return null;
  const serverMessage = error?.messages?.[0] || error?.message || '';
  if (serverMessage.toLowerCase().includes('practitioner not found')) {
    return 'Your account is not linked to a Practitioner record. Please contact the administrator to set up your doctor profile.';
  }
  return 'Failed to load profile. Please try again or contact support.';
});

const documentsResource = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.doctor_documents',
  makeParams() {
    return { docname: profileData.data?.doctor?.name };
  },
});

watch(
  () => profileData.data?.doctor?.name,
  (docname) => {
    if (docname) {
      documentsResource.fetch();
    }
  },
  { immediate: true }
);

const documents = computed(() => {
  return documentsResource.data?.documents || [];
});

function logout() {
  session.logout.submit();
}

function openDocument(filePath) {
  if (!filePath) return;

  const url = encodeURI(filePath);

  window.open(url, '_blank');
}

function openPhotoPicker() {
  photoInput.value?.click();
}

async function handleDocumentSelected(event) {
  const file = event.target.files?.[0];

  if (!file) return;

  documentUploading.value = true;

  try {
    const formData = new FormData();

    formData.append('file', file);
    formData.append('is_private', '1');
    formData.append('doctype', 'Practitioner');
    formData.append('docname', profileData.data.doctor.name);

    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    const result = await response.json();

    if (!response.ok || result.exc) {
      throw new Error(result.exc || 'Document upload failed');
    }

    await documentsResource.reload();
  } catch (error) {
    alert('Failed to upload document.');
  } finally {
    documentUploading.value = false;
    event.target.value = '';
  }
}

function openDocumentPicker() {
  documentInput.value?.click();
}

async function deleteDocument(document) {
  const confirmed = window.confirm(`Are you sure you want to delete "${document.file_name}"?`);

  if (!confirmed) return;

  try {
    const response = await fetch('/api/method/wellnest.health.doctype.practitioner.practitioner.delete_doctor_document', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        docname: profileData.data.doctor.name,
        file_name: document.name,
      }),
    });

    const result = await response.json();

    if (!response.ok || result.exc) {
      throw new Error(result.exc || 'Failed to delete document');
    }

    await documentsResource.reload();
  } catch (error) {
    alert('Failed to delete document.');
  }
}

async function handlePhotoSelected(event) {
  const file = event.target.files?.[0];

  if (!file) return;

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

  if (!allowedTypes.includes(file.type)) {
    alert('Please select a JPG, PNG, or WEBP image.');
    event.target.value = '';
    return;
  }

  try {
    const formData = new FormData();

    formData.append('file', file);
    formData.append('is_private', '0');
    formData.append('doctype', 'Practitioner');
    formData.append('docname', profileData.data.doctor.name);
    formData.append('fieldname', 'photo');

    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    const result = await response.json();

    if (!response.ok || result.exc) {
      throw new Error(result.exc || 'Photo upload failed');
    }

    console.log('Photo uploaded:', result);

    const uploadedFile = result.message;

    // Persist the photo field on the actual Practitioner record
    await setPhotoResource.submit({
      doctype: 'Practitioner',
      name: profileData.data.doctor.name,
      fieldname: 'photo',
      value: uploadedFile.file_url,
    });

    // Update the UI immediately
    profileData.data.doctor.photo = uploadedFile.file_url;
    editForm.photo = uploadedFile.file_url;

    // Reset image error state
    imageLoadError.value = false;
  } catch (error) {
    alert('Failed to upload profile photo.');
  } finally {
    event.target.value = '';
  }
}

// Edit profile modal

const showEditProfile = ref(false);

const editForm = reactive({
  // Personal information
  title: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  gender: '',
  dob: '',
  email: '',
  mobile: '',
  nationality: '',
  photo: '',
  languages_known: [],
  education_history: [],

  // Address
  address_line1: '',
  city: '',
  state: '',
  pincode: '',

  // Professional information
  designation: '',
  specialty: '',
  super_specialty: '',
  registration_no: '',
  registration_valid_upto: '',
  registration_letter: '',
  council_name: '',
  practicing_from: '',
  digital_signature_url: '',
  professional_summary: '',
  primary_facility: '',
  telemedicine_certified: false,
  hpr_verified: false,

  // Account / charges
  currency: '',
  online_charge: '',
  emergency_charge: '',
  priority_charge: '',
  clinic_charge: '',
  available_for_home_visits: false,
  home_visit_charge: '',
  is_active: false,

  // Availability
  availability_days: [],
  is_published: false,
});

const cityOptions = ref([]);
const stateOptions = ref([]);
const hospitalOptions = ref([]);
const hospitalSearchQuery = ref('');
const specialtyOptions = ref([]);
const superSpecialtyOptions = ref([]);
const languageOptions = ref([]);
const medicalDegreeOptions = ref([]);
const educationalInstitutionOptions = ref([]);
const educationalInstitutionSearchQuery = ref('');

const cityResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'City',
      fields: ['name', 'state'],
      limit_page_length: 0,
      order_by: 'name asc',
    };
  },
  onSuccess(data) {
    cityOptions.value = (data || []).map((item) => ({
      label: item.name.replace(/,\s*[^,]+$/, ''),
      value: item.name,
      state: item.state,
    }));
  },
});
watch(
  [() => editForm.city, cityOptions],
  ([city, options]) => {
    const selectedCity = options.find((option) => option.value === city);

    editForm.state = selectedCity?.state || '';
  },
  { immediate: true }
);

const stateResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'State',
      fields: ['name'],
      limit_page_length: 100,
      order_by: 'name asc',
    };
  },
  onSuccess(data) {
    stateOptions.value = (data || []).map((item) => ({
      label: item.name,
      value: item.name,
    }));
  },
});

const hospitalResource = createResource({
  url: 'frappe.client.get_list',

  makeParams() {
    return {
      doctype: 'Hospital',
      fields: ['name', 'hospital_name'],
      filters: hospitalSearchQuery.value ? [['hospital_name', 'like', `%${hospitalSearchQuery.value}%`]] : [],
      limit_page_length: 100,
      order_by: 'hospital_name asc',
    };
  },

  onSuccess(data) {
    hospitalOptions.value = (data || []).map((item) => ({
      label: item.hospital_name || item.name,
      value: item.name,
    }));
  },
});

const createHospitalResource = createResource({
  url: 'wellnest.health.doctype.hospital.hospital.create_hospital',
});

async function createHospital() {
  console.log('CREATE HOSPITAL CLICKED');
  const hospitalName = hospitalSearchQuery.value.trim();

  if (!hospitalName) {
    return;
  }

  try {
    const response = await createHospitalResource.submit({
      hospital_name: hospitalName,
    });

    console.log('Create hospital response:', response);

    const hospital = response?.message || response;

    if (!hospital?.name) {
      console.error('Hospital creation returned an unexpected response:', response);
      return;
    }

    const option = {
      label: hospital.hospital_name || hospitalName,
      value: hospital.name,
    };

    hospitalOptions.value = [option, ...hospitalOptions.value.filter((item) => item.value !== option.value)];

    editForm.primary_facility = hospital.name;

    hospitalSearchQuery.value = '';

    await hospitalResource.fetch();

    editForm.primary_facility = hospital.name;
  } catch (error) {
    console.error('Failed to create hospital:', error);
  }
}

async function createInstitution(education) {
  const institutionName = educationalInstitutionSearchQuery.value.trim();

  if (!institutionName) {
    return;
  }

  try {
    const response = await createResource({
      url: 'wellnest.health.doctype.educational_institution.educational_institution.create_institution',
    }).submit({
      institution_name: institutionName,
    });

    const institution = response;

    const option = {
      label: institution.institution_name || institution.name,
      value: institution.name,
    };

    const existing = educationalInstitutionOptions.value.find((item) => item.value === option.value);

    if (!existing) {
      educationalInstitutionOptions.value.push(option);
    }

    education.institution = option.value;

    educationalInstitutionSearchQuery.value = '';
  } catch (error) {
    console.error('Failed to create institution:', error);
  }
}

const specialtyResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Medical Specialty',
      fields: ['name', 'specialty_name'],
      limit_page_length: 100,
      order_by: 'specialty_name asc',
    };
  },
  onSuccess(data) {
    specialtyOptions.value = (data || []).map((item) => ({
      label: item.specialty_name,
      value: item.name,
    }));
  },
});

const superSpecialtyResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    const params = {
      doctype: 'Medical Super Specialty',
      fields: ['name', 'super_specialty_name', 'specialty'],
      limit_page_length: 100,
      order_by: 'super_specialty_name asc',
    };

    if (editForm.specialty) {
      params.filters = JSON.stringify({
        specialty: editForm.specialty,
      });
    }

    return params;
  },
  onSuccess(data) {
    superSpecialtyOptions.value = (data || []).map((item) => ({
      label: item.super_specialty_name,
      value: item.name,
    }));

    if (editForm.super_specialty && !superSpecialtyOptions.value.some((option) => option.value === editForm.super_specialty)) {
      editForm.super_specialty = '';
    }
  },
});

watch(
  () => editForm.specialty,
  () => {
    editForm.super_specialty = '';
    superSpecialtyResource.reload();
  }
);

const medicalDegreeResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Medical Degree',
      fields: ['name'],
      limit_page_length: 100,
      order_by: 'name asc',
    };
  },
  onSuccess(data) {
    medicalDegreeOptions.value = (data || []).map((item) => ({
      label: item.name,
      value: item.name,
    }));
  },
});

const educationalInstitutionResource = createResource({
  url: 'frappe.client.get_list',

  makeParams() {
    return {
      doctype: 'Educational Institution',
      fields: ['name', 'institution_name'],
      filters: educationalInstitutionSearchQuery.value ? [['institution_name', 'like', `%${educationalInstitutionSearchQuery.value}%`]] : [],
      limit_page_length: 100,
      order_by: 'institution_name asc',
    };
  },

  onSuccess(data) {
    educationalInstitutionOptions.value = (data || []).map((item) => ({
      label: item.institution_name || item.name,
      value: item.name,
    }));
  },
});

const languageResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Spoken Language',
      fields: ['name'],
      limit_page_length: 100,
      order_by: 'name asc',
    };
  },
  onSuccess(data) {
    languageOptions.value = (data || []).map((item) => ({
      label: item.name,
      value: item.name,
    }));

    if (isEditingProfile.value) {
      selectedLanguageOptions.value = languageOptions.value.filter((option) => editForm.languages_known.includes(option.value));
    }
  },
});

const updateProfileResource = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.update_doctor_profile',
});

const setPhotoResource = createResource({
  url: 'frappe.client.set_value',
});

function editProfile() {
  const doctor = profileData?.data?.doctor;

  isEditingProfile.value = true;

  cityResource.fetch();
  stateResource.fetch();
  hospitalResource.fetch();
  specialtyResource.fetch();
  superSpecialtyResource.fetch();
  languageResource.fetch();
  medicalDegreeResource.fetch();
  educationalInstitutionResource.fetch();

  // Personal information
  editForm.title = doctor?.title || '';
  editForm.first_name = doctor?.first_name || '';
  editForm.middle_name = doctor?.middle_name || '';
  editForm.last_name = doctor?.last_name || '';
  editForm.gender = doctor?.gender || '';
  editForm.dob = doctor?.dob ? doctor.dob.split(' ')[0] : '';
  editForm.email = doctor?.email || '';
  editForm.mobile = doctor?.mobile || '';
  editForm.nationality = doctor?.nationality || '';
  editForm.photo = doctor?.photo || '';
  editForm.languages_known = doctor?.languages_known?.length ? doctor.languages_known.map((l) => l.spoken_language_option) : [];
  editForm.education_history = (doctor?.education_history || []).map((item) => ({
    degree: item.degree || '',
    institution: item.institution || '',
    year_of_completion: item.year_of_completion || '',
  }));

  // Sync immediately if options are already cached from a previous open
  if (languageOptions.value.length) {
    selectedLanguageOptions.value = languageOptions.value.filter((option) => editForm.languages_known.includes(option.value));
  } else {
    selectedLanguageOptions.value = [];
  }

  // Address
  editForm.address_line1 = doctor?.address_line1 || '';
  editForm.city = doctor?.city || '';
  editForm.state = doctor?.state || '';
  editForm.pincode = doctor?.pincode || '';

  // Professional information
  editForm.designation = doctor?.designation || '';
  editForm.specialty = doctor?.specialty || '';
  editForm.super_specialty = doctor?.super_specialty || '';
  editForm.registration_no = doctor?.registration_no || '';
  editForm.registration_valid_upto = doctor?.registration_valid_upto || '';
  editForm.registration_letter = doctor?.registration_letter || '';
  editForm.council_name = doctor?.council_name || '';
  editForm.practicing_from = doctor?.practicing_from || '';
  editForm.digital_signature_url = doctor?.digital_signature_url || '';
  editForm.professional_summary = doctor?.professional_summary || '';
  editForm.primary_facility = doctor?.primary_facility || '';
  editForm.telemedicine_certified = Boolean(doctor?.telemedicine_certified);
  editForm.hpr_verified = Boolean(doctor?.hpr_verified);

  // Account / charges
  editForm.currency = doctor?.currency || '';
  editForm.online_charge = doctor?.online_charge ?? '';
  editForm.emergency_charge = doctor?.emergency_charge ?? '';
  editForm.priority_charge = doctor?.priority_charge ?? '';
  editForm.clinic_charge = doctor?.clinic_charge ?? '';
  editForm.available_for_home_visits = Boolean(doctor?.available_for_home_visits);
  editForm.home_visit_charge = doctor?.home_visit_charge ?? '';
  editForm.is_active = Boolean(doctor?.is_active);

  // Availability
  editForm.availability_days = (doctor?.availability_days || []).map((item) => ({
    day: item.day,
    online_from: formatTimeOnly(item.online_from),
    online_to: formatTimeOnly(item.online_to),
    emergency_from: formatTimeOnly(item.emergency_from),
    emergency_to: formatTimeOnly(item.emergency_to),
    clinic_from: formatTimeOnly(item.clinic_from),
    clinic_to: formatTimeOnly(item.clinic_to),
  }));
  editForm.is_published = Boolean(doctor?.is_published);

  showEditProfile.value = true;
}

function closeEditProfile() {
  isEditingProfile.value = false;
  showEditProfile.value = false;
}

async function saveProfile() {
  const languagesArray = editForm.languages_known || [];

  try {
    await updateProfileResource.submit({
      docname: profileData.data.doctor.name,
      updates: {
        // Personal information
        title: editForm.title,
        first_name: editForm.first_name,
        middle_name: editForm.middle_name,
        last_name: editForm.last_name,
        gender: editForm.gender,
        dob: editForm.dob,
        email: editForm.email,
        mobile: editForm.mobile,
        nationality: editForm.nationality,

        // Address
        address_line1: editForm.address_line1,
        city: editForm.city,
        state: editForm.state,
        pincode: editForm.pincode,

        // Professional information
        education_history: editForm.education_history.map((item) => ({
          degree: item.degree,
          institution: item.institution,
          year_of_completion: item.year_of_completion,
        })),
        designation: editForm.designation,
        specialty: editForm.specialty,
        super_specialty: editForm.super_specialty,
        registration_no: editForm.registration_no,
        registration_valid_upto: editForm.registration_valid_upto,
        registration_letter: editForm.registration_letter,
        council_name: editForm.council_name,
        practicing_from: editForm.practicing_from,
        digital_signature_url: editForm.digital_signature_url,
        professional_summary: editForm.professional_summary,
        primary_facility: editForm.primary_facility,
        telemedicine_certified: editForm.telemedicine_certified,
        hpr_verified: editForm.hpr_verified,

        // Account / charges
        currency: editForm.currency,
        online_charge: editForm.online_charge,
        emergency_charge: editForm.emergency_charge,
        priority_charge: editForm.priority_charge,
        clinic_charge: editForm.clinic_charge,
        available_for_home_visits: editForm.available_for_home_visits,
        home_visit_charge: editForm.home_visit_charge,
        is_active: editForm.is_active,

        // Availability
        is_published: editForm.is_published,

        // Existing child table
        languages_known: languagesArray,

        // Availability child table
        availability_days: editForm.availability_days,

        // Existing attachment values
        photo: editForm.photo,
      },
    });

    // Reflect the changes immediately
    if (profileData?.data?.doctor) {
      const doctor = profileData.data.doctor;

      doctor.title = editForm.title;
      doctor.first_name = editForm.first_name;
      doctor.middle_name = editForm.middle_name;
      doctor.last_name = editForm.last_name;
      doctor.full_name = [editForm.title, editForm.first_name, editForm.middle_name, editForm.last_name].filter(Boolean).join(' ');
      doctor.gender = editForm.gender;
      doctor.dob = editForm.dob;
      doctor.email = editForm.email;
      doctor.mobile = editForm.mobile;
      doctor.nationality = editForm.nationality;
      doctor.photo = editForm.photo;

      doctor.address_line1 = editForm.address_line1;
      doctor.city = editForm.city;
      doctor.state = editForm.state;
      doctor.pincode = editForm.pincode;

      doctor.education_history = editForm.education_history.map((item) => ({
        degree: item.degree,
        institution: item.institution,
        year_of_completion: item.year_of_completion,
      }));
      doctor.designation = editForm.designation;
      doctor.specialty = editForm.specialty;
      doctor.super_specialty = editForm.super_specialty;

      doctor.specialty_name = specialtyOptions.value.find((option) => option.value === editForm.specialty)?.label || '';

      doctor.super_specialty_name = superSpecialtyOptions.value.find((option) => option.value === editForm.super_specialty)?.label || '';
      doctor.registration_no = editForm.registration_no;
      doctor.registration_valid_upto = editForm.registration_valid_upto;
      doctor.registration_letter = editForm.registration_letter;
      doctor.council_name = editForm.council_name;
      doctor.practicing_from = editForm.practicing_from;
      doctor.digital_signature_url = editForm.digital_signature_url;
      doctor.professional_summary = editForm.professional_summary;
      doctor.primary_facility = editForm.primary_facility;
      doctor.primary_facility_name = hospitalOptions.value.find((option) => option.value === editForm.primary_facility)?.label || editForm.primary_facility;
      doctor.telemedicine_certified = editForm.telemedicine_certified;
      doctor.hpr_verified = editForm.hpr_verified;

      doctor.currency = editForm.currency;
      doctor.online_charge = editForm.online_charge;
      doctor.emergency_charge = editForm.emergency_charge;
      doctor.priority_charge = editForm.priority_charge;
      doctor.clinic_charge = editForm.clinic_charge;
      doctor.available_for_home_visits = editForm.available_for_home_visits;
      doctor.home_visit_charge = editForm.home_visit_charge;

      doctor.is_published = editForm.is_published;

      doctor.languages_known = languagesArray.map((lang) => ({
        spoken_language_option: lang,
      }));

      doctor.availability_days = editForm.availability_days.map((item) => ({
        day: item.day,
        online_from: item.online_from,
        online_to: item.online_to,
        emergency_from: item.emergency_from,
        emergency_to: item.emergency_to,
        clinic_from: item.clinic_from,
        clinic_to: item.clinic_to,
      }));
    }

    isEditingProfile.value = false;
    showEditProfile.value = false;
  } catch (err) {
    alert('Failed to save profile.');
  }
}
</script>
