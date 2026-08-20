consultations. page
<template>
  <div class="p-6 md:p-8">
    <!-- Page Header -->
    <div class="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Consultations</h1>
        <p class="text-gray-500 mt-1">
          Each booked row opens its own patient-specific prescription workspace,
          whether the doctor writes digitally or validates an uploaded paper prescription.
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          class="px-4 py-2 rounded-lg border border-amber-400 bg-white
                 text-amber-700 font-semibold hover:bg-amber-50 transition"
                   @click="showTemplatePreview = true"
        >
          Preview selected template
        </button>

        <button
  type="button"
  class="px-5 py-3
         rounded-xl
         border border-amber-400
         text-amber-700
         font-semibold
         hover:bg-amber-50"
  @click="router.push({ name: 'Schedule' })"
>
  Update availability
</button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
      <div
        v-for="card in summaryCards"
        :key="card.title"
        class="bg-white border border-gray-200 rounded-2xl p-5"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500">{{ card.title }}</p>

            <p
              class="text-3xl font-bold text-gray-900 mt-4"
              :class="{ 'text-2xl': card.value.length > 8 }"
            >
              {{ card.value }}
            </p>

            <p class="text-sm text-gray-500 mt-2">
              {{ card.description }}
            </p>
          </div>

          <div
            class="w-10 h-10 rounded-xl bg-amber-50
                   text-amber-600 flex items-center justify-center"
          >
            <FeatherIcon :name="card.icon" class="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,2fr)_minmax(360px,1fr)] gap-6 items-start">

      <!-- Waiting Room / Upcoming -->
     <section
  class="bg-white border border-gray-200
         rounded-2xl overflow-y-auto
         max-h-[620px]"
      >

        <div class="flex items-center justify-between px-6 py-5 border-b border-gray-200">
          <div>
            <h2 class="text-xl font-bold text-gray-900">
              Waiting room and upcoming
            </h2>
          </div>

     <button
  type="button"
  class="text-sm font-semibold text-amber-600 hover:underline"
  @click="router.push({ name: 'Schedule' })"
>
  Manage slots
</button>
        </div>

        <!-- Desktop table header -->
        <div
          class="hidden lg:grid
                 grid-cols-[90px_1.2fr_90px_1.5fr_150px_165px]
                 gap-3
                 px-6 py-3
                 bg-gray-50
                 text-xs font-semibold text-gray-500
                 uppercase tracking-wide"
        >
          <div>Time</div>
          <div>Patient</div>
          <div>Mode</div>
          <div>Reason</div>
          <div>Workflow</div>
          <div>Actions</div>
        </div>

        <!-- Consultation rows -->
       <div
          v-for="consultation in consultations"
           :key="consultation.id"
           class="border-t border-gray-100 transition-colors"
           :class="{
        'bg-amber-50/60':
          selectedConsultation.id === consultation.id
         }"
        >
          <div
            class="grid grid-cols-1 lg:grid-cols-[90px_1.2fr_90px_1.5fr_150px_165px]
                   gap-4
                   px-6 py-5
                   items-center"
          >
            <!-- Time -->
            <div class="text-sm font-semibold text-gray-900">
              {{ consultation.time }}
            </div>

            <!-- Patient -->
            <div>
              <p class="font-bold text-gray-900">
                {{ consultation.patient }}
              </p>

              <p class="text-sm text-gray-500">
                {{ consultation.bookingStatus }}
              </p>
            </div>

            <!-- Mode -->
            <div class="text-sm text-gray-700">
              {{ consultation.mode }}
            </div>

            <!-- Reason -->
            <div class="text-sm text-gray-700">
              {{ consultation.reason }}
            </div>

            <!-- Workflow -->
            <div>
              <span
                class="inline-flex px-3 py-1 rounded-full
                       text-xs font-semibold"
                :class="workflowClass(consultation.workflow)"
              >
                {{ consultation.workflow }}
              </span>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2">
              <button
                type="button"
                 class="px-3 py-2 rounded-lg
                   border border-amber-400
         text-amber-700
         text-sm font-semibold
         bg-white
         hover:bg-amber-500
         hover:text-white
         transition-colors"
            
                  @click="openPrescription(consultation)"
                   >
                 Open prescription
                </button>

              <button
                type="button"
                class="px-4 py-2 rounded-lg
                       bg-amber-500 text-white
                       text-sm font-semibold
                       hover:bg-amber-600 transition"
                @click="joinConsultation(consultation)"
              >
                Join
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Template Preview -->
     <aside
       class="bg-white border border-gray-200
         rounded-2xl overflow-y-auto
         max-h-[600px]"
        >

        <div class="flex items-center justify-between px-5 py-5 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-900">
            Template preview
          </h2>

          <button
            type="button"
            class="px-3 py-2 rounded-lg
                   border border-amber-400
                   text-amber-700
                   text-sm font-semibold
                   hover:bg-amber-50"
                   @click="showTemplatePreview = true"
          >
            Open full preview
          </button>
        </div>

        <div class="p-5">

          <!-- Doctor details -->
          <div class="grid grid-cols-3 gap-3">

            <div class="border border-gray-200 rounded-xl p-4">
              <p class="text-xs text-gray-500">
                Consulting Doctor
              </p>

              <p class="font-bold text-gray-900 mt-2">
                Brigadier (Retd.) Dr. Yashwant Singh Bisht
              </p>

              <p class="text-xs text-gray-500 mt-2">
                Senior Consultant
              </p>

              <p class="text-xs text-gray-500">
                Internal Medicine
              </p>
            </div>

            <div class="border border-gray-200 rounded-xl p-4">
              <p class="text-xs text-gray-500">
                Qualification
              </p>

              <p class="font-bold text-gray-900 mt-2">
                MBBS, MD
              </p>

              <p class="text-xs text-gray-500 mt-2">
                Internal Medicine
              </p>

              <p class="text-xs text-gray-500">
                34 Years Experience
              </p>
            </div>

            <div class="border border-gray-200 rounded-xl p-4">
              <p class="text-xs text-gray-500">
                Registration
              </p>

              <p class="font-bold text-gray-900 mt-2">
                DMC/R/04821
              </p>

              <p class="text-xs text-gray-500 mt-2">
                Digitally signed draft
              </p>
            </div>
          </div>

          <!-- Selected patient -->
          <div class="mt-6">
            <p class="text-xs text-gray-500">
              Selected patient
            </p>

            <p class="text-3xl font-bold text-gray-900 mt-1">
              {{ selectedConsultation.patient }}
            </p>

            <p class="text-sm text-gray-500">
              {{ selectedConsultation.mode }} consult /
              {{ selectedConsultation.time }}
            </p>
          </div>

          <!-- Chief Complaints -->
          <div class="mt-6">
            <h3 class="text-lg font-bold text-gray-900">
              Chief Complaints (with duration)
            </h3>

            <ul class="list-disc pl-5 mt-2 space-y-1 text-sm text-gray-700">
              <li>
                Elevated fasting glucose readings (7 days)
              </li>

              <li>
                Evening blood pressure spikes (5 days)
              </li>
            </ul>
          </div>

          <!-- History -->
          <div class="mt-6">
            <h3 class="text-lg font-bold text-gray-900">
              History (brief)
            </h3>

            <p class="text-sm text-gray-700 mt-2 leading-6">
              Known type 2 diabetes and hypertension.
              Dietary adherence has been variable during recent travel.
            </p>
          </div>

          <!-- Vitals -->
          <div class="mt-6">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900">
                Vitals
              </h3>

              <span class="text-xs text-gray-500">
                Optional
              </span>
            </div>

            <div class="grid grid-cols-2 gap-3 mt-3">
              <div
                v-for="vital in vitals"
                :key="vital.label"
                class="border border-gray-200 rounded-xl p-3"
              >
                <p class="text-xs text-gray-500">
                  {{ vital.label }}
                </p>

                <p class="font-bold text-gray-900 mt-1">
                  {{ vital.value }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
    <!-- Full consultation workspace -->
<section class="mt-6">
  <Consultation
    :selected-consultation="selectedConsultation"
  />
</section>
    

<!-- Join consultation modal -->
<div
  v-if="showJoinModal"
  class="fixed inset-0 z-50 bg-black/50
         flex items-center justify-center p-4"
  @click.self="closeJoinModal"
>
  <div
  class="w-full
         max-w-3xl
         h-[88vh]
         bg-white
         rounded-xl
         shadow-xl
         overflow-hidden
         flex flex-col"
>
    <!-- Modal header -->
    <div
      class="flex items-center justify-between
             px-6 py-4 border-b border-gray-200"
    >
      <h2 class="text-2xl font-bold text-gray-900">
        Join consultation
      </h2>

      <button
        type="button"
        class="text-gray-500 hover:text-gray-900 text-2xl"
        @click="closeJoinModal"
      >
        ×
      </button>
    </div>

    <!-- Waiting room -->
    <div class="p-5">
      <div
        class="rounded-2xl min-h-[420px]
               bg-gradient-to-br from-teal-500 to-teal-700
               text-white
               p-7
               flex flex-col"
      >
        <!-- Patient details -->
        <div>
          <span
            class="inline-flex px-3 py-1 rounded-lg
                   bg-white/90 text-gray-800
                   text-xs font-semibold"
          >
            Waiting room
          </span>

          <h2 class="text-4xl font-bold mt-4">
            {{ selectedConsultation.patient }}
          </h2>

          <p class="text-lg mt-2">
            {{ selectedConsultation.reason }}
          </p>

          <p class="mt-4 text-base">
            {{ selectedConsultation.mode }} consult /
            {{ selectedConsultation.time }}
          </p>
        </div>

        <!-- Controls -->
        <div class="flex-1 flex items-end justify-center gap-3">

          <button
            type="button"
            class="w-12 h-12 rounded-xl
                   border border-white/40
                   bg-white/10
                   flex items-center justify-center"
          >
            <FeatherIcon name="mic" class="w-5 h-5" />
          </button>

          <button
            type="button"
            class="w-12 h-12 rounded-xl
                   border border-white/40
                   bg-white/10
                   flex items-center justify-center"
          >
            <FeatherIcon name="video" class="w-5 h-5" />
          </button>

          <button
            type="button"
            class="w-12 h-12 rounded-xl
                   border border-white/40
                   bg-white/10
                   flex items-center justify-center"
          >
            <FeatherIcon name="monitor" class="w-5 h-5" />
          </button>

          <button
            type="button"
            class="ml-3 px-5 py-3 rounded-xl
                   bg-red-500 text-white font-semibold
                   hover:bg-red-600"
            @click="closeJoinModal"
          >
            End consultation
          </button>

        </div>
      </div>
    </div>
  </div>
</div>

</div>
<!-- Selected prescription template preview -->
<div
  v-if="showTemplatePreview"
  class="fixed inset-0 z-50
         bg-black/50
         flex items-center justify-center
         p-4"
  @click.self="showTemplatePreview = false"
>
  <div
    class="w-full
           max-w-5xl
           h-[90vh]
           bg-white
           rounded-2xl
           shadow-xl
           overflow-hidden
           flex flex-col"
  >

    <!-- Modal header -->
    <div
      class="flex items-center
             justify-between
             px-6 py-4
             border-b border-gray-200
             shrink-0"
    >
      <h2 class="text-2xl font-semibold text-gray-900">
        {{ selectedConsultation.patient }} prescription preview
      </h2>

      <button
        type="button"
        class="text-gray-500
               hover:text-gray-900
               text-3xl
               leading-none"
        @click="showTemplatePreview = false"
      >
        ×
      </button>
    </div>

    <!-- Scrollable prescription -->
    <div class="flex-1 overflow-y-auto px-4 py-4">

      <div
        class="border border-amber-200
               bg-[#fffdf7]
               rounded-xl
               p-5"
      >

        <!-- Prescription header -->
        <div
          class="flex items-start
                 justify-between
                 gap-4
                 pb-4
                 border-b border-amber-200"
        >
          <div class="flex items-start gap-3">

            <img
  :src="logoUrl"
  alt="CareYogi"
  class="w-24
         h-auto
         object-contain
         shrink-0"
/>

            <div>
              <h3
                class="text-lg
                       font-bold
                       text-gray-900"
              >
                CAREYOGI DIGITAL CONSULTATION PRESCRIPTION
              </h3>

              <p class="text-sm text-gray-600 mt-1">
                5th Floor, Adilakshmi Square, Plot No.137,
                Old Mumbai Highway, Gachibowli, Hyderabad,
                Telangana - 500032
              </p>

              <p class="text-sm text-gray-600 mt-1">
                +91-9810918237 / info@careyogis.com
              </p>
            </div>
          </div>

          <span
            class="shrink-0
                   px-3 py-1
                   rounded-lg
                   bg-emerald-100
                   text-emerald-700
                   text-xs
                   font-semibold"
          >
            Digital draft
          </span>
        </div>

        <!-- Patient details -->
        <div
          class="grid grid-cols-2
                 md:grid-cols-4
                 gap-2
                 mt-4"
        >
          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Patient
            </p>
            <p class="font-bold text-gray-900 mt-1">
              {{ selectedConsultation.patient }}
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Age/Gender
            </p>
            <p class="font-bold text-gray-900 mt-1">
              54 Years / Female
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Prescription ID
            </p>
            <p class="font-bold text-gray-900 mt-1">
              CY-2026-000137
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Consultation Type
            </p>
            <p class="font-bold text-gray-900 mt-1">
              {{ selectedConsultation.mode }}
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Date
            </p>
            <p class="font-bold text-gray-900 mt-1">
              10 Jul 2026
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Time
            </p>
            <p class="font-bold text-gray-900 mt-1">
              {{ selectedConsultation.time }}
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              UHID
            </p>
            <p class="font-bold text-gray-900 mt-1">
              CY-004614
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Appointment ID
            </p>
            <p class="font-bold text-gray-900 mt-1">
              APT-009814
            </p>
          </div>
        </div>

        <!-- Doctor details -->
        <div
          class="grid grid-cols-1
                 md:grid-cols-3
                 gap-2
                 mt-3"
        >
          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Consulting Doctor
            </p>

            <p class="font-bold text-gray-900 mt-1">
              Brigadier (Retd.) Dr. Yashwant Singh Bisht
            </p>

            <p class="text-xs text-gray-500 mt-1">
              Senior Consultant, Internal Medicine
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Qualification
            </p>

            <p class="font-bold text-gray-900 mt-1">
              MBBS, MD (Internal Medicine)
            </p>

            <p class="text-xs text-gray-500 mt-1">
              34 Years Experience
            </p>
          </div>

          <div class="border border-gray-200 bg-white rounded-xl p-3">
            <p class="text-xs text-gray-500">
              Registration
            </p>

            <p class="font-bold text-gray-900 mt-1">
              DMC/R/04821
            </p>

            <p class="text-xs text-gray-500 mt-1">
              Digitally signed draft
            </p>
          </div>
        </div>

        <!-- Chief complaints -->
        <div class="mt-6">
          <h3 class="font-bold text-gray-900">
            Chief Complaints (with duration)
          </h3>

          <ul
            class="list-disc
                   pl-5
                   mt-2
                   space-y-1
                   text-sm
                   text-gray-700"
          >
            <li>
              Elevated fasting glucose readings (7 days)
            </li>

            <li>
              Evening blood pressure spikes (5 days)
            </li>
          </ul>
        </div>

        <!-- History -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            History (brief)
          </h3>

          <p class="text-sm text-gray-700 mt-2">
            Known type 2 diabetes and hypertension.
            Dietary adherence has been variable during recent travel.
          </p>
        </div>

        <!-- Vitals -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Vitals
          </h3>

          <div
            class="grid grid-cols-2
                   md:grid-cols-3
                   gap-2
                   mt-3"
          >
            <div
              class="border border-gray-200
                     bg-white
                     rounded-xl
                     p-3"
            >
              <p class="text-xs text-gray-500 uppercase">
                Weight
              </p>

              <p class="font-bold text-gray-900 mt-1">
                74 kg
              </p>
            </div>

            <div
              class="border border-gray-200
                     bg-white
                     rounded-xl
                     p-3"
            >
              <p class="text-xs text-gray-500 uppercase">
                Height
              </p>

              <p class="font-bold text-gray-900 mt-1">
                162 cm
              </p>
            </div>

            <div
              class="border border-gray-200
                     bg-white
                     rounded-xl
                     p-3"
            >
              <p class="text-xs text-gray-500 uppercase">
                Pulse
              </p>

              <p class="font-bold text-gray-900 mt-1">
                76 /min
              </p>
            </div>

            <div
              class="border border-gray-200
                     bg-white
                     rounded-xl
                     p-3"
            >
              <p class="text-xs text-gray-500 uppercase">
                BP
              </p>

              <p class="font-bold text-gray-900 mt-1">
                128/78 mmHg
              </p>
            </div>

            <div
              class="border border-gray-200
                     bg-white
                     rounded-xl
                     p-3"
            >
              <p class="text-xs text-gray-500 uppercase">
                SpO2
              </p>

              <p class="font-bold text-gray-900 mt-1">
                98%
              </p>
            </div>

            <div
              class="border border-gray-200
                     bg-white
                     rounded-xl
                     p-3"
            >
              <p class="text-xs text-gray-500 uppercase">
                Temperature
              </p>

              <p class="font-bold text-gray-900 mt-1">
                98.4 F
              </p>
            </div>
          </div>
        </div>

        <!-- Examination -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Examination
          </h3>

          <p class="text-sm text-gray-700 mt-2">
            Alert, oriented, no pedal edema, no hypoglycaemic symptoms at present.
            Home glucose log reviewed.
          </p>
        </div>

        <!-- Provisional diagnosis -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Provisional Diagnosis
          </h3>

          <p class="text-sm text-gray-700 mt-2">
            Type 2 diabetes with suboptimal fasting control;
            hypertension presently controlled.
          </p>
        </div>

        <!-- Investigations -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Investigations Advised
          </h3>

          <ul
            class="list-disc
                   pl-5
                   mt-2
                   space-y-1
                   text-sm
                   text-gray-700"
          >
            <li>HbA1c</li>
            <li>Lipid profile</li>
            <li>Urine microalbumin</li>
          </ul>
        </div>

        <!-- Treatment -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Treatment / Medication
          </h3>

          <div class="mt-3 overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead>
                <tr class="bg-amber-100 border-b border-amber-200">
                  <th class="px-3 py-2 font-bold">
                    Medicine (Brand / Generic)
                  </th>
                  <th class="px-3 py-2 font-bold">
                    Dose
                  </th>
                  <th class="px-3 py-2 font-bold">
                    Frequency
                  </th>
                  <th class="px-3 py-2 font-bold">
                    Instructions
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr class="border-b border-gray-200">
                  <td class="px-3 py-2">
                    Metformin XR 500 mg
                  </td>
                  <td class="px-3 py-2">
                    1 tablet
                  </td>
                  <td class="px-3 py-2">
                    Twice daily
                  </td>
                  <td class="px-3 py-2">
                    After breakfast and dinner
                  </td>
                </tr>

                <tr class="border-b border-gray-200">
                  <td class="px-3 py-2">
                    Telmisartan 40 mg
                  </td>
                  <td class="px-3 py-2">
                    1 tablet
                  </td>
                  <td class="px-3 py-2">
                    Once daily
                  </td>
                  <td class="px-3 py-2">
                    Morning
                  </td>
                </tr>

                <tr>
                  <td class="px-3 py-2">
                    Rosuvastatin 10 mg
                  </td>
                  <td class="px-3 py-2">
                    1 tablet
                  </td>
                  <td class="px-3 py-2">
                    Once daily
                  </td>
                  <td class="px-3 py-2">
                    At bedtime
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Follow-up -->
        <div class="mt-6">
          <h3 class="font-bold text-gray-900">
            Follow-up Advise
          </h3>

          <p class="text-sm text-gray-700 mt-2">
            Upload fasting glucose for 7 days and review over video in 2 weeks.
          </p>
        </div>

        <!-- Diet -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Diet Advice
          </h3>

          <p class="text-sm text-gray-700 mt-2">
            Low GI meals, avoid sweetened beverages, and keep dinner light.
          </p>
        </div>

        <!-- Exercise -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Exercise Advice
          </h3>

          <p class="text-sm text-gray-700 mt-2">
            30-minute brisk walk on at least 5 days each week.
          </p>
        </div>

        <!-- Digitally signed -->
        <div
          class="mt-6
                 pt-5
                 border-t border-amber-200"
        >
          <h3 class="font-bold text-gray-900">
            Digitally Signed
          </h3>

          <p class="text-sm text-gray-600 mt-2">
            This is a digitally generated CareYogi prescription
            and does not require a physical signature.
          </p>

          <p class="text-sm text-gray-700 mt-2">
            © CareYogi 2026
          </p>
        </div>

      </div>
    </div>

    <!-- Footer -->
    <div
      class="flex items-center
             justify-end
             gap-3
             px-6 py-4
             border-t border-gray-200
             bg-white
             shrink-0"
    >
      <button
        type="button"
        class="px-5 py-3
               rounded-xl
               bg-gray-100
               text-gray-800
               font-semibold
               hover:bg-gray-200"
        @click="showTemplatePreview = false"
      >
        Close
      </button>

      <button
        type="button"
        class="px-5 py-3
               rounded-xl
               bg-amber-500
               text-white
               font-semibold
               hover:bg-amber-600"
        @click="showTemplatePreview = false"
      >
        Finalize draft
      </button>
    </div>

  </div>
</div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'
import Consultation from './Consultation.vue'
import logoUrl from '@/assets/images/logo-01.png'

const router = useRouter()

const consultations = ref([
  {
    id: 'asha-mehta-1',
    time: '10:30 AM',
    patient: 'Asha Mehta',
    bookingStatus: 'Waiting',
    mode: 'Video',
    reason: 'Review glucose logs and BP readings',
    workflow: 'Digital draft',
  },
  {
    id: 'nirmala-devi-1',
    time: '11:15 AM',
    patient: 'Nirmala Devi',
    bookingStatus: 'Upcoming',
    mode: 'Video',
    reason: 'Breathlessness after discharge',
    workflow: 'In review',
  },
  {
    id: 'rohan-gupta-1',
    time: '12:20 PM',
    patient: 'Rohan Gupta',
    bookingStatus: 'Upcoming',
    mode: 'Clinic',
    reason: 'Post angioplasty medication review',
    workflow: 'Ready for validation',
  },
  {
    id: 'meera-iyer-1',
    time: '03:00 PM',
    patient: 'Meera Iyer',
    bookingStatus: 'Upcoming',
    mode: 'Video',
    reason: 'Joint pain flare-up',
    workflow: 'Digital draft',
  },
  {
    id: 'leela-rao-1',
    time: '05:20 PM',
    patient: 'Leela Rao',
    bookingStatus: 'Assistant assigned',
    mode: 'Home',
    reason: 'Fluid retention check',
    workflow: 'Digital draft',
  },
])

const selectedConsultation = ref(consultations.value[0])
const showJoinModal = ref(false)
const showTemplatePreview = ref(false)

const summaryCards = computed(() => [
  {
    title: 'Digital drafts',
    value: '18',
    description: 'Written during or after consultation',
    icon: 'edit-3',
  },
  {
    title: 'In review',
    value: '1',
    description: 'Paper uploads being processed asynchronously',
    icon: 'loader',
  },
  {
    title: 'Ready for validation',
    value: '1',
    description: 'OCR output awaiting doctor confirmation',
    icon: 'check-square',
  },
  {
    title: 'Selected patient',
    value: selectedConsultation.value.patient,
    description: `${selectedConsultation.value.mode} consult at ${selectedConsultation.value.time}`,
    icon: 'user',
  },
])

const vitals = [
  { label: 'Weight', value: '74 kg' },
  { label: 'Height', value: '162 cm' },
  { label: 'Pulse', value: '76 /min' },
  { label: 'BP', value: '128/78 mmHg' },
  { label: 'SpO2', value: '98%' },
  { label: 'Temperature', value: '98.4 F' },
]

function workflowClass(workflow) {
  if (workflow === 'Ready for validation') {
    return 'bg-cyan-100 text-cyan-700'
  }

  if (workflow === 'In review') {
    return 'bg-amber-100 text-amber-700'
  }

  return 'bg-emerald-100 text-emerald-700'
}

function openPrescription(consultation) {
  selectedConsultation.value = consultation
}

function joinConsultation(consultation) {
  router.push({
    name: 'WaitingRoom',
    params: {
      id: consultation.id,
    },
  })
}

function closeJoinModal() {
  showJoinModal.value = false
}
</script>