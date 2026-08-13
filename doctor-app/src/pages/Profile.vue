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
                    {{ profileData?.data?.doctor?.city || 'Not Available' }}
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
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Qualification </span>
                  {{ profileData?.data?.doctor?.qualification || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Additional Qualification </span>
                  {{ profileData?.data?.doctor?.additional_qualification || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Designation </span>
                  {{ profileData?.data?.doctor?.designation || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Super Specialty </span>
                  {{ profileData?.data?.doctor?.super_specialty || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Experience </span>
                  {{ profileData?.data?.doctor?.experience_years ?? 'Not Available' }}
                  <span v-if="profileData?.data?.doctor?.experience_years != null"> years </span>
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Council Registration </span>
                  {{ profileData?.data?.doctor?.council_name || 'Not Available' }}
                  <span v-if="profileData?.data?.doctor?.registration_no"> · {{ profileData.data.doctor.registration_no }} </span>
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Registration Valid Upto </span>
                  {{ profileData?.data?.doctor?.registration_valid_upto || 'Not Available' }}
                </div>

                <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-800 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1"> Primary Facility </span>
                  {{ profileData?.data?.doctor?.primary_facility || 'Not Available' }}
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
                <span class="text-gray-500 text-xs font-medium uppercase tracking-wide block mb-2">Available Days</span>

                <div v-if="profileData?.data?.doctor?.availability_days?.length" class="flex flex-wrap gap-2">
                  <span
                    v-for="item in profileData.data.doctor.availability_days"
                    :key="item.day"
                    class="px-2.5 py-1 bg-teal-50 text-teal-700 text-xs font-semibold rounded-full border border-teal-200"
                  >
                    {{ item.day }}
                  </span>
                </div>
                <div v-else class="text-gray-500 text-sm">Not Available</div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Consultation Hours</span>
                  <span class="text-sm font-semibold text-gray-900">
                    <template v-if="formatTimeDisplay(profileData?.data?.doctor?.available_from) || formatTimeDisplay(profileData?.data?.doctor?.available_till)">
                      {{ formatTimeDisplay(profileData?.data?.doctor?.available_from) || '—' }} – {{ formatTimeDisplay(profileData?.data?.doctor?.available_till) || '—' }}
                    </template>
                    <template v-else>Not Available</template>
                  </span>
                </div>

                <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <span class="font-medium text-gray-500 block text-xs mb-1">Emergency Hours</span>
                  <span class="text-sm font-semibold text-gray-900">
                    <template v-if="formatTimeDisplay(profileData?.data?.doctor?.available_in_emergency_from) || formatTimeDisplay(profileData?.data?.doctor?.available_in_emergency_till)">
                      {{ formatTimeDisplay(profileData?.data?.doctor?.available_in_emergency_from) || '—' }} – {{ formatTimeDisplay(profileData?.data?.doctor?.available_in_emergency_till) || '—' }}
                    </template>
                    <template v-else>Not Available</template>
                  </span>
                </div>

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
                :model-value="cityOptions.find((option) => option.value === editForm.city) || null"
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
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Qualification</label>
              <input
                v-model="editForm.qualification"
                type="text"
                placeholder="e.g. MBBS, MD"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Additional Qualification</label>
              <input
                v-model="editForm.additional_qualification"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Super Specialty</label>
              <input
                v-model="editForm.super_specialty"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Experience (years)</label>
              <input
                v-model="editForm.experience_years"
                type="number"
                min="0"
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Primary Facility</label>
              <Autocomplete
                :model-value="hospitalOptions.find((option) => option.value === editForm.primary_facility) || null"
                :options="hospitalOptions"
                placeholder="Select hospital"
                @update:model-value="(option) => (editForm.primary_facility = option?.value || '')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Doctor Type</label>
              <select v-model="editForm.doctor_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500">
                <option value="">Select doctor type</option>
                <option value="Doctor">Doctor</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">ABDM Council Code</label>
              <input
                v-model="editForm.abdm_council_code"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">ABDM Specialty Code</label>
              <input
                v-model="editForm.abdm_specialty_code"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Normal Consultation Charge</label>
              <input
                v-model="editForm.normal_charge"
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Account Status</label>
              <input
                :value="editForm.account_status || 'Not Available'"
                type="text"
                disabled
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-100 text-gray-500 cursor-not-allowed"
              />
              <div class="text-xs text-gray-500 mt-1">Account status can only be changed by an administrator.</div>
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
              <input id="is-active" v-model="editForm.is_active" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
              <label for="is-active" class="text-sm font-medium text-gray-700"> Is Active </label>
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
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Available From</label>
              <div class="flex gap-2">
                <select
                  v-model="availableFromTime.hour.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="h in 12" :key="h" :value="String(h).padStart(2, '0')">{{ String(h).padStart(2, '0') }}</option>
                </select>
                <select
                  v-model="availableFromTime.minute.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="m in ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']" :key="m" :value="m">{{ m }}</option>
                </select>
                <select
                  v-model="availableFromTime.period.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Available Till</label>
              <div class="flex gap-2">
                <select
                  v-model="availableTillTime.hour.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="h in 12" :key="h" :value="String(h).padStart(2, '0')">{{ String(h).padStart(2, '0') }}</option>
                </select>
                <select
                  v-model="availableTillTime.minute.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="m in ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']" :key="m" :value="m">{{ m }}</option>
                </select>
                <select
                  v-model="availableTillTime.period.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Emergency Available From</label>
              <div class="flex gap-2">
                <select
                  v-model="emergencyFromTime.hour.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="h in 12" :key="h" :value="String(h).padStart(2, '0')">{{ String(h).padStart(2, '0') }}</option>
                </select>
                <select
                  v-model="emergencyFromTime.minute.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="m in ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']" :key="m" :value="m">{{ m }}</option>
                </select>
                <select
                  v-model="emergencyFromTime.period.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Emergency Available Till</label>
              <div class="flex gap-2">
                <select
                  v-model="emergencyTillTime.hour.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="h in 12" :key="h" :value="String(h).padStart(2, '0')">{{ String(h).padStart(2, '0') }}</option>
                </select>
                <select
                  v-model="emergencyTillTime.minute.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option v-for="m in ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']" :key="m" :value="m">{{ m }}</option>
                </select>
                <select
                  v-model="emergencyTillTime.period.value"
                  class="w-1/3 px-2 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                >
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
            </div>

            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">Availability Days</label>

              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <label
                  v-for="day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']"
                  :key="day"
                  class="flex items-center gap-2 p-2 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    :value="day"
                    :checked="editForm.availability_days.some((item) => item.day === day)"
                    @change="$event.target.checked ? editForm.availability_days.push({ day }) : (editForm.availability_days = editForm.availability_days.filter((item) => item.day !== day))"
                    class="h-4 w-4 rounded border-gray-300 text-teal-600 focus:ring-teal-500"
                  />
                  <span class="text-sm text-gray-700">{{ day }}</span>
                </label>
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
import { computed, reactive, ref } from 'vue';
import { FeatherIcon, Badge, Avatar, Autocomplete, FileUploader, createResource } from 'frappe-ui';
import { session } from '../data/session';
import router from '@/router';

function formatDateOnly(dateString) {
  if (!dateString) return 'Not Available';
  return dateString.split(' ')[0];
}

function formatTimeOnly(timeString) {
  if (!timeString) return '';
  const parts = timeString.split(':');
  const paddedParts = parts.map((part) => part.padStart(2, '0'));
  return paddedParts.join(':');
}

function formatTimeDisplay(timeString) {
  if (!timeString) return null;

  const parts = timeString.split(':');
  let hours = parseInt(parts[0], 10);
  const minutes = (parts[1] || '00').padStart(2, '0');

  if (Number.isNaN(hours)) return null;

  const period = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  if (hours === 0) hours = 12;

  return `${hours}:${minutes} ${period}`;
}

function combineTime(hour12Str, minuteStr, period) {
  let hour12 = parseInt(hour12Str, 10);
  if (Number.isNaN(hour12)) hour12 = 12;
  let hour24 = hour12 % 12;
  if (period === 'PM') hour24 += 12;
  return `${String(hour24).padStart(2, '0')}:${minuteStr}:00`;
}

function useTimeField(fieldName) {
  const hour = computed({
    get() {
      const val = editForm[fieldName];
      if (!val) return '';
      let h = parseInt(val.split(':')[0], 10);
      if (Number.isNaN(h)) return '';
      let h12 = h % 12;
      if (h12 === 0) h12 = 12;
      return String(h12).padStart(2, '0');
    },
    set(newHour12) {
      const current = editForm[fieldName] || '00:00';
      const currentMinute = (current.split(':')[1] || '00').padStart(2, '0');
      const currentHour = parseInt(current.split(':')[0], 10) || 0;
      const currentPeriod = currentHour >= 12 ? 'PM' : 'AM';
      editForm[fieldName] = combineTime(newHour12, currentMinute, currentPeriod);
    },
  });

  const minute = computed({
    get() {
      const val = editForm[fieldName];
      if (!val) return '';
      return (val.split(':')[1] || '00').padStart(2, '0');
    },
    set(newMinute) {
      const current = editForm[fieldName] || '00:00';
      const currentHour = parseInt(current.split(':')[0], 10) || 0;
      let h12 = currentHour % 12;
      if (h12 === 0) h12 = 12;
      const currentPeriod = currentHour >= 12 ? 'PM' : 'AM';
      editForm[fieldName] = combineTime(String(h12).padStart(2, '0'), newMinute, currentPeriod);
    },
  });

  const period = computed({
    get() {
      const val = editForm[fieldName];
      if (!val) return 'AM';
      const h = parseInt(val.split(':')[0], 10);
      return h >= 12 ? 'PM' : 'AM';
    },
    set(newPeriod) {
      const current = editForm[fieldName] || '12:00';
      const currentMinute = (current.split(':')[1] || '00').padStart(2, '0');
      const currentHour = parseInt(current.split(':')[0], 10) || 0;
      let h12 = currentHour % 12;
      if (h12 === 0) h12 = 12;
      editForm[fieldName] = combineTime(String(h12).padStart(2, '0'), currentMinute, newPeriod);
    },
  });

  return { hour, minute, period };
}

function updateLanguages(options) {
  selectedLanguageOptions.value = options || [];

  editForm.languages_known = (options || []).map((option) => {
    return typeof option === 'object' ? option.value : option;
  });
}

function removeLanguage(option) {
  selectedLanguageOptions.value = selectedLanguageOptions.value.filter((item) => item.value !== option.value);
  editForm.languages_known = selectedLanguageOptions.value.map((item) => item.value);
}

const state = reactive({
  index: 0,
  tabs: [{ label: 'General' }, { label: 'Ratings' }],
});

const imageLoadError = ref(false);
const photoInput = ref(null);
const photoUploading = ref(false);
const documentInput = ref(null);
const documentUploading = ref(false);

const loadError = ref(null);
const totalRatings = ref(0);
const selectedLanguageOptions = ref([]);

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

const documentsResource = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.doctor_documents',
  auto: true,
});

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
    console.error('Failed to upload document:', error);
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
        file_name: document.name,
      }),
    });

    const result = await response.json();

    if (!response.ok || result.exc) {
      throw new Error(result.exc || 'Failed to delete document');
    }

    await documentsResource.reload();
  } catch (error) {
    console.error('Failed to delete document:', error);
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
    formData.append('is_private', '1');
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
    console.error('Failed to upload profile photo:', error);
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

  // Address
  address_line1: '',
  city: '',
  state: '',
  pincode: '',

  // Professional information
  qualification: '',
  additional_qualification: '',
  designation: '',
  super_specialty: '',
  registration_no: '',
  registration_valid_upto: '',
  registration_letter: '',
  council_name: '',
  experience_years: '',
  digital_signature_url: '',
  professional_summary: '',
  primary_facility: '',
  telemedicine_certified: false,
  hpr_verified: false,
  doctor_type: '',
  abdm_council_code: '',
  abdm_specialty_code: '',

  // Account / charges
  account_status: '',
  currency: '',
  normal_charge: '',
  emergency_charge: '',
  priority_charge: '',
  is_active: false,

  // Availability
  available_from: '',
  available_till: '',
  availability_days: [],
  available_in_emergency_from: '',
  available_in_emergency_till: '',
  is_published: false,
});

const availableFromTime = useTimeField('available_from');
const availableTillTime = useTimeField('available_till');
const emergencyFromTime = useTimeField('available_in_emergency_from');
const emergencyTillTime = useTimeField('available_in_emergency_till');

const cityOptions = ref([]);
const stateOptions = ref([]);
const hospitalOptions = ref([]);
const languageOptions = ref([]);

const cityResource = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'City',
      fields: ['name'],
      limit_page_length: 100,
      order_by: 'name asc',
    };
  },
  onSuccess(data) {
    cityOptions.value = (data || []).map((item) => ({
      label: item.name,
      value: item.name,
    }));
  },
});

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
      fields: ['name'],
      limit_page_length: 100,
      order_by: 'name asc',
    };
  },
  onSuccess(data) {
    hospitalOptions.value = (data || []).map((item) => ({
      label: item.name,
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

    // Re-sync selected chips
    selectedLanguageOptions.value = languageOptions.value.filter((option) => editForm.languages_known.includes(option.value));
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

  cityResource.fetch();
  stateResource.fetch();
  hospitalResource.fetch();
  languageResource.fetch();

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
  editForm.qualification = doctor?.qualification || '';
  editForm.additional_qualification = doctor?.additional_qualification || '';
  editForm.designation = doctor?.designation || '';
  editForm.super_specialty = doctor?.super_specialty || '';
  editForm.registration_no = doctor?.registration_no || '';
  editForm.registration_valid_upto = doctor?.registration_valid_upto || '';
  editForm.registration_letter = doctor?.registration_letter || '';
  editForm.council_name = doctor?.council_name || '';
  editForm.experience_years = doctor?.experience_years ?? '';
  editForm.digital_signature_url = doctor?.digital_signature_url || '';
  editForm.professional_summary = doctor?.professional_summary || '';
  editForm.primary_facility = doctor?.primary_facility || '';
  editForm.telemedicine_certified = Boolean(doctor?.telemedicine_certified);
  editForm.hpr_verified = Boolean(doctor?.hpr_verified);
  editForm.doctor_type = doctor?.doctor_type || '';
  editForm.abdm_council_code = doctor?.abdm_council_code || '';
  editForm.abdm_specialty_code = doctor?.abdm_specialty_code || '';

  // Account / charges
  editForm.account_status = doctor?.account_status || '';
  editForm.currency = doctor?.currency || '';
  editForm.normal_charge = doctor?.normal_charge ?? '';
  editForm.emergency_charge = doctor?.emergency_charge ?? '';
  editForm.priority_charge = doctor?.priority_charge ?? '';
  editForm.is_active = Boolean(doctor?.is_active);

  // Availability
  // Availability
  editForm.available_from = formatTimeOnly(doctor?.available_from);
  editForm.available_till = formatTimeOnly(doctor?.available_till);
  editForm.availability_days = doctor?.availability_days || [];
  editForm.available_in_emergency_from = formatTimeOnly(doctor?.available_in_emergency_from);
  editForm.available_in_emergency_till = formatTimeOnly(doctor?.available_in_emergency_till);
  editForm.is_published = Boolean(doctor?.is_published);

  showEditProfile.value = true;
}

function closeEditProfile() {
  showEditProfile.value = false;
}

async function saveProfile() {
  const languagesArray = editForm.languages_known || [];

  try {
    await updateProfileResource.submit({
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
      qualification: editForm.qualification,
      additional_qualification: editForm.additional_qualification,
      designation: editForm.designation,
      super_specialty: editForm.super_specialty,
      registration_no: editForm.registration_no,
      registration_valid_upto: editForm.registration_valid_upto,
      registration_letter: editForm.registration_letter,
      council_name: editForm.council_name,
      experience_years: editForm.experience_years,
      digital_signature_url: editForm.digital_signature_url,
      professional_summary: editForm.professional_summary,
      primary_facility: editForm.primary_facility,
      telemedicine_certified: editForm.telemedicine_certified,
      hpr_verified: editForm.hpr_verified,
      doctor_type: editForm.doctor_type,
      abdm_council_code: editForm.abdm_council_code,
      abdm_specialty_code: editForm.abdm_specialty_code,

      // Account / charges
      account_status: editForm.account_status,
      currency: editForm.currency,
      normal_charge: editForm.normal_charge,
      emergency_charge: editForm.emergency_charge,
      priority_charge: editForm.priority_charge,
      is_active: editForm.is_active,

      // Availability
      available_from: editForm.available_from,
      available_till: editForm.available_till,
      available_in_emergency_from: editForm.available_in_emergency_from,
      available_in_emergency_till: editForm.available_in_emergency_till,
      is_published: editForm.is_published,

      // Existing child table
      languages_known: languagesArray,

      // Availability child table
      availability_days: editForm.availability_days,

      // Existing attachment values
      photo: editForm.photo,
      registration_letter: editForm.registration_letter,
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

      doctor.qualification = editForm.qualification;
      doctor.additional_qualification = editForm.additional_qualification;
      doctor.designation = editForm.designation;
      doctor.super_specialty = editForm.super_specialty;
      doctor.registration_no = editForm.registration_no;
      doctor.registration_valid_upto = editForm.registration_valid_upto;
      doctor.registration_letter = editForm.registration_letter;
      doctor.council_name = editForm.council_name;
      doctor.experience_years = editForm.experience_years;
      doctor.digital_signature_url = editForm.digital_signature_url;
      doctor.professional_summary = editForm.professional_summary;
      doctor.primary_facility = editForm.primary_facility;
      doctor.telemedicine_certified = editForm.telemedicine_certified;
      doctor.hpr_verified = editForm.hpr_verified;
      doctor.doctor_type = editForm.doctor_type;
      doctor.abdm_council_code = editForm.abdm_council_code;
      doctor.abdm_specialty_code = editForm.abdm_specialty_code;

      doctor.account_status = editForm.account_status;
      doctor.currency = editForm.currency;
      doctor.normal_charge = editForm.normal_charge;
      doctor.emergency_charge = editForm.emergency_charge;
      doctor.priority_charge = editForm.priority_charge;
      doctor.is_active = editForm.is_active;

      doctor.available_from = editForm.available_from;
      doctor.available_till = editForm.available_till;
      doctor.available_in_emergency_from = editForm.available_in_emergency_from;
      doctor.available_in_emergency_till = editForm.available_in_emergency_till;
      doctor.is_published = editForm.is_published;

      doctor.languages_known = languagesArray.map((lang) => ({
        spoken_language_option: lang,
      }));

      doctor.availability_days = editForm.availability_days;
    }

    showEditProfile.value = false;
  } catch (err) {
    console.error('Failed to save profile:', err);
  }
}
</script>
