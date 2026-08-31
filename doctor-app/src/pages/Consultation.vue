<template>
 <div class="w-full">
    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,2fr)_380px] gap-6">

      <!-- Main consultation workspace -->
      <main class="space-y-6">

        <!-- Clinical findings -->
        <section class="bg-white border border-gray-200 rounded-2xl p-6">
          <div class="flex items-start justify-between gap-4 mb-6">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">
                Clinical findings
              </h1>

              <p class="text-gray-500 mt-1">
                Final CareYogi digital prescription fields,
                scoped to {{ patient.name }}.
              </p>
            </div class="flex items-center gap-3">

            <button
              type="button"
              class="px-4 py-2 rounded-lg
                     border border-amber-400
                     text-amber-700
                     font-semibold
                     hover:bg-amber-50"
              @click="previewTemplate"
            >
              Preview template
            </button>
            <button
             type="button"
             class="px-4 py-2 rounded-lg
           bg-amber-500
           text-white
           font-semibold
           hover:bg-amber-600"
    @click="saveClinicalRecord"
  >
    Save Clinical Record
  </button>

          </div>

          <!-- Chief complaints -->
          <div class="mb-7">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-bold text-gray-900">
                Chief Complaints
              </h2>

              <button
                type="button"
                class="px-4 py-2 rounded-lg
                       bg-gray-50
                       text-gray-900
                       font-semibold
                       hover:bg-gray-100"
                @click="addComplaint"
              >
                Add complaint
              </button>
            </div>

            <div class="space-y-3">
              <div
                v-for="(complaint, index) in complaints"
                :key="complaint.id"
                class="grid grid-cols-1 md:grid-cols-[1fr_240px_auto] gap-3"
              >
                <input
                  v-model="complaint.text"
                  type="text"
                  placeholder="Chief complaint"
                  class="w-full rounded-xl
                         border border-gray-200
                         px-4 py-3
                         text-gray-900
                         focus:outline-none
                         focus:ring-2 focus:ring-amber-200"
                />

                <input
                  v-model="complaint.duration"
                  type="text"
                  placeholder="Duration"
                  class="w-full rounded-xl
                         border border-gray-200
                         px-4 py-3
                         text-gray-900
                         focus:outline-none
                         focus:ring-2 focus:ring-amber-200"
                />

                <button
                  v-if="complaints.length > 1"
                  type="button"
                  class="px-3 py-2 rounded-lg
                         text-red-600
                         hover:bg-red-50"
                  @click="removeComplaint(index)"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>

          <!-- History -->
          <div class="mb-7">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-lg font-semibold text-gray-900">
                History (brief)
                <span class="font-normal text-gray-400">
                  Optional
                </span>
              </h2>
            </div>

            <textarea
              v-model="history"
              rows="3"
              placeholder="Enter brief history"
              class="w-full rounded-xl
                     border border-gray-200
                     px-4 py-3
                     text-gray-900
                     resize-y
                     focus:outline-none
                     focus:ring-2 focus:ring-amber-200"
            ></textarea>
          </div>

          <!-- Vitals -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-bold text-gray-900">
                Vitals
              </h2>

              <span class="text-sm text-gray-500">
                Optional
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                v-for="vital in vitals"
                :key="vital.key"
              >
                <label class="block text-sm text-gray-700 mb-2">
                  {{ vital.label }}
                  <span class="text-gray-400">
                    ({{ vital.unit }})
                  </span>
                </label>

                <input
                  v-model="vital.value"
                  type="text"
                  :placeholder="vital.placeholder"
                  class="w-full rounded-xl
                         border border-gray-200
                         px-4 py-3
                         text-gray-900
                         focus:outline-none
                         focus:ring-2 focus:ring-amber-200"
                />
              </div>
            </div>
          </div>
        
       <div class="h-6"></div>
        <!-- Examination -->
    
          <div class="mb-3">
            <h2 class="text-xl font-bold text-gray-900">
              Examination
            </h2>
          </div>

          <textarea
            v-model="examination"
            rows="3"
            placeholder="Enter examination findings"
            class="w-full rounded-xl
                   border border-gray-200
                   px-4 py-3
                   text-gray-900
                   resize-y
                   focus:outline-none
                   focus:ring-2 focus:ring-amber-200"
          ></textarea>
          
           <!-- Provisional Diagnosis -->
<div class="mt-6">
  <h2 class="text-xl font-bold text-gray-900">
    Provisional Diagnosis
  </h2>

  <textarea
  v-model="provisionalDiagnosis"
  rows="3"
  placeholder="Enter provisional diagnosis"
  class="w-full
         mt-3
         rounded-xl
         border border-gray-200
         px-4 py-3
         text-gray-900
         resize-y
         focus:outline-none
         focus:ring-2
         focus:ring-amber-200"
></textarea>
</div>
<!-- Investigations advised -->
<section
  class="mt-6
         bg-white
         border border-gray-200
         rounded-2xl
         p-6"
>
  <div
    class="flex items-start
           justify-between
           gap-4
           mb-4"
  >
    <div>
      <h2 class="text-xl font-bold text-gray-900">
        Investigations advised
      </h2>

      <p class="text-gray-500 mt-1">
        Optional field, with autosuggest support for common advisories.
      </p>
    </div>

    <button
      type="button"
      class="px-4 py-2
             rounded-xl
             bg-gray-50
             text-gray-900
             font-semibold
             hover:bg-gray-100"
             @click="addInvestigation"
    >
      Add investigation
    </button>
  </div>

  <div class="space-y-3">
  <div
    v-for="(investigation, index) in investigations"
    :key="index"
    class="flex items-center gap-3"
  >
    <input
      v-model="investigations[index]"
      type="text"
      placeholder="Investigation"
      class="flex-1
             rounded-xl
             border border-gray-200
             px-4 py-3
             text-gray-900
             focus:outline-none
             focus:ring-2
             focus:ring-amber-200"
    />

    <button
      type="button"
      class="shrink-0
             px-3 py-2
             rounded-lg
             text-red-600
             bg-red-50
             hover:bg-red-100
             font-semibold
             text-sm"
      @click="removeInvestigation(index)"
    >
      Remove
    </button>
  </div>
</div>
</section>
        </section>
       <!-- Treatment / Medication -->
<section
  class="mt-6
         bg-white
         border border-gray-200
         rounded-2xl
         p-6"
>
  <!-- Header -->
  <div
    class="flex items-start
           justify-between
           gap-4
           mb-5"
  >
    <div>
      <h2 class="text-xl font-bold text-gray-900">
        Treatment / Medication
      </h2>

      <p class="text-gray-500 mt-1">
        Brand or generic, dose, frequency, and instructions.
      </p>
    </div>

    <button
      type="button"
      class="px-4 py-2
             rounded-xl
             bg-gray-50
             text-gray-900
             font-semibold
             hover:bg-gray-100"
      @click="addMedicine"
    >
      Add medicine
    </button>
  </div>

  <!-- Table header -->
  <div
    class="hidden md:grid
           grid-cols-[1.2fr_1fr_1fr_1.2fr_auto]
           gap-4
           px-2 pb-3
           border-b border-gray-200
           text-sm
           font-semibold
           text-gray-900"
  >
    <div>Medicine</div>
    <div>Dose</div>
    <div>Frequency</div>
    <div>Instruction</div>
    <div></div>
  </div>

  <!-- Medicine rows -->
  <div class="space-y-0">
    <div
      v-for="(medicine, index) in medicines"
      :key="index"
      class="grid grid-cols-1
             md:grid-cols-[1.2fr_1fr_1fr_1.2fr_auto]
             gap-4
             py-3
             border-b border-gray-200"
    >
      <!-- Medicine -->
      <input
        v-model="medicine.medicine"
        type="text"
        placeholder="Brand / generic"
        class="w-full
               rounded-xl
               border border-gray-200
               px-3 py-2
               text-gray-900
               focus:outline-none
               focus:ring-2
               focus:ring-amber-200"
      />

      <!-- Dose -->
      <input
        v-model="medicine.dose"
        type="text"
        placeholder="Dose"
        class="w-full
               rounded-xl
               border border-gray-200
               px-3 py-2
               text-gray-900
               focus:outline-none
               focus:ring-2
               focus:ring-amber-200"
      />

      <!-- Frequency -->
      <input
        v-model="medicine.frequency"
        type="text"
        placeholder="Frequency"
        class="w-full
               rounded-xl
               border border-gray-200
               px-3 py-2
               text-gray-900
               focus:outline-none
               focus:ring-2
               focus:ring-amber-200"
      />

      <!-- Instruction -->
      <input
        v-model="medicine.instruction"
        type="text"
        placeholder="Instruction"
        class="w-full
               rounded-xl
               border border-gray-200
               px-3 py-2
               text-gray-900
               focus:outline-none
               focus:ring-2
               focus:ring-amber-200"
      />

      <!-- Remove -->
      <button
        type="button"
        class="self-center
               shrink-0
               px-3 py-2
               rounded-lg
               bg-red-50
               text-red-600
               text-sm
               font-semibold
               hover:bg-red-100"
        @click="removeMedicine(index)"
      >
        Remove
      </button>
    </div>
  </div>
</section>
<!-- Follow-up and lifestyle advice -->
<section
  class="mt-6
         bg-white
         border border-gray-200
         rounded-2xl
         p-6"
>
  <!-- Header -->
  <div
    class="flex items-start
           justify-between
           gap-4
           mb-6"
  >
    <div>
      <h2 class="text-xl font-bold text-gray-900">
        Follow-up and lifestyle advice
      </h2>

      <p class="text-gray-500 mt-1">
        Optional lifestyle sections remain visible in the final prescription only when filled.
      </p>
    </div>
<div class="flex justify-end gap-3">
  <template
  v-if="
    prescriptionWorkflowState !== 'Confirmed' &&
    prescriptionWorkflowState !== 'Complete'
  "
>
    <button
      type="button"
      class="px-5 py-3
             rounded-xl
             border border-amber-400
             text-amber-700
             font-semibold
             hover:bg-amber-50"
      @click="savePrescriptionDraft"
    >
      Save As Draft
    </button>

    <button
      type="button"
      class="px-5 py-3
             rounded-xl
             bg-amber-500
             text-white
             font-semibold
             hover:bg-amber-600"
      @click="finalizePrescription"
    >
      Submit prescription
    </button>
  </template>

  <div
    v-else
    class="rounded-xl border border-green-200
           bg-green-50
           px-5 py-3
           text-sm font-semibold
           text-green-700"
  >
    Prescription already submitted for this patient.
  </div>
</div>
  </div>

  <!-- Follow-up -->
  <div class="mb-5">
    <label class="block text-sm font-medium text-gray-900 mb-2">
      Follow-up Advise
    </label>

    <textarea
      v-model="followUpAdvice"
      rows="3"
      placeholder="Enter follow-up advice"
      class="w-full
             rounded-xl
             border border-gray-200
             px-4 py-3
             text-gray-900
             resize-y
             focus:outline-none
             focus:ring-2
             focus:ring-amber-200"
    ></textarea>
  </div>

  <!-- Diet + Exercise -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-5">

    <!-- Diet -->
    <div>
      <label class="block text-sm font-medium text-gray-900 mb-2">
        Diet Advice
        <span class="text-gray-400 font-normal">
          Optional
        </span>
      </label>

      <textarea
        v-model="dietAdvice"
        rows="3"
        placeholder="Enter diet advice"
        class="w-full
               rounded-xl
               border border-gray-200
               px-4 py-3
               text-gray-900
               resize-y
               focus:outline-none
               focus:ring-2
               focus:ring-amber-200"
      ></textarea>
    </div>

    <!-- Exercise -->
    <div>
      <label class="block text-sm font-medium text-gray-900 mb-2">
        Exercise Advice
        <span class="text-gray-400 font-normal">
          Optional
        </span>
      </label>

      <textarea
        v-model="exerciseAdvice"
        rows="3"
        placeholder="Enter exercise advice"
        class="w-full
               rounded-xl
               border border-gray-200
               px-4 py-3
               text-gray-900
               resize-y
               focus:outline-none
               focus:ring-2
               focus:ring-amber-200"
      ></textarea>
    </div>

  </div>
</section>

      </main>

      <!-- CareYogi Assist -->
      <aside class="space-y-6">

        <section
          class="bg-amber-50
                 border border-amber-200
                 rounded-2xl
                 p-5"
        >
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-xl font-bold text-gray-900">
              CareYogi Assist
            </h2>

            <span
              class="px-2 py-1 rounded-lg
                     bg-white
                     text-xs font-semibold
                     text-gray-700"
            >
              Autosuggest
            </span>
          </div>

          <p class="text-sm text-gray-500 mb-5">
            Prototype capability for AI or trusted medical source
            suggestions. Click to insert or append into the selected
            patient record.
          </p>

          <!-- Suggestions -->
          <div class="space-y-5">

            <div>
              <h3 class="text-sm font-semibold text-gray-900">
                Chief complaints
              </h3>

              <button
                type="button"
                class="mt-2 px-3 py-2 rounded-full
                       border border-amber-300
                       text-amber-700
                       text-sm
                       hover:bg-amber-100"
                @click="insertComplaintSuggestion"
              >
                Elevated fasting glucose / BP spikes
              </button>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-gray-900">
                History
              </h3>

              <button
                type="button"
                class="mt-2 px-3 py-2 rounded-full
                       border border-amber-300
                       text-amber-700
                       text-sm
                       hover:bg-amber-100"
                @click="insertHistorySuggestion"
              >
                Known diabetes and hypertension.
              </button>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-gray-900">
                Examination
              </h3>

              <button
                type="button"
                class="mt-2 px-3 py-2 rounded-full
                       border border-amber-300
                       text-amber-700
                       text-sm
                       hover:bg-amber-100"
                @click="insertExaminationSuggestion"
              >
                General condition reviewed and relevant systems examined.
              </button>
            </div>
            

            <div>
              <h3 class="text-sm font-semibold text-gray-900">
                Diagnosis
              </h3>

              <button
                type="button"
                class="mt-2 px-3 py-2 rounded-full
                       border border-amber-300
                       text-amber-700
                       text-sm
                       hover:bg-amber-100"
                @click="insertDiagnosisSuggestion"
              >
                Diabetes / hypertension follow-up
              </button>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-gray-900">
                Investigations
              </h3>

              <div class="flex flex-wrap gap-2 mt-2">
                <button
                  type="button"
                  class="px-3 py-2 rounded-full
                         border border-amber-300
                         text-amber-700
                         text-sm
                         hover:bg-amber-100"
                >
                  CBC
                </button>

                <button
                  type="button"
                  class="px-3 py-2 rounded-full
                         border border-amber-300
                         text-amber-700
                         text-sm
                         hover:bg-amber-100"
                >
                  RFT
                </button>

                <button
                  type="button"
                  class="px-3 py-2 rounded-full
                         border border-amber-300
                         text-amber-700
                         text-sm
                         hover:bg-amber-100"
                >
                  Doctor to confirm
                </button>
              </div>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-gray-900">
                Follow-up
              </h3>

              <button
                type="button"
                class="mt-2 px-3 py-2 rounded-full
                       border border-amber-300
                       text-amber-700
                       text-sm
                       hover:bg-amber-100"
              >
                Review again with reports and symptom update.
              </button>
            </div>

          </div>
        </section>

        <!-- Selected consultation -->
     <section class="bg-white border border-gray-200 rounded-2xl p-5">
          <span
            class="inline-flex px-3 py-1 rounded-lg
                   bg-gray-100
                   text-gray-700
                   text-xs font-semibold"
          >
            Selected consultation
          </span>

        <div
  class="mt-4 rounded-2xl
         bg-gradient-to-br from-teal-500 to-teal-700
         text-white
         p-5
         cursor-pointer
         hover:shadow-lg
         transition-shadow"
  @click="showJoinModal = true"
>
            <h2 class="text-3xl font-bold">
              {{ patient.name }}
            </h2>

            <p class="mt-2">
              {{ consultation.reason }}
            </p>

            <p class="text-sm mt-2 text-white/80">
              {{ consultation.mode }} consult /
              {{ consultation.time }}
            </p>

            <div class="flex items-center gap-2 mt-6">

              <button
                type="button"
                class="w-11 h-11 rounded-xl
                       border border-white/40
                       bg-white/10
                       flex items-center justify-center"
              >
                <FeatherIcon name="mic" class="w-5 h-5" />
              </button>

              <button
                type="button"
                class="w-11 h-11 rounded-xl
                       border border-white/40
                       bg-white/10
                       flex items-center justify-center"
              >
                <FeatherIcon name="video" class="w-5 h-5" />
              </button>

              <button
                type="button"
                class="w-11 h-11 rounded-xl
                       border border-white/40
                       bg-white/10
                       flex items-center justify-center"
              >
                <FeatherIcon name="monitor" class="w-5 h-5" />
              </button>

              <button
                type="button"
                class="ml-auto px-4 py-2 rounded-lg
                       bg-red-500
                       text-white
                       font-semibold"
              >
                End consultation
              </button>
            </div>
          </div>
        </section>
        <!-- Handwritten prescription workflow -->
<section
  class="mt-6
         bg-white
         border border-gray-200
         rounded-2xl
         p-5"
>
  <!-- Header -->
  <div
    class="flex items-start
           justify-between
           gap-4"
  >
    <div>
      <h2 class="text-xl font-bold text-gray-900 leading-tight">
        Handwritten prescription
        <br />
        workflow
      </h2>
    </div>

    <button
      type="button"
      class="shrink-0
             px-4 py-3
             rounded-xl
             border border-amber-400
             text-amber-700
             font-semibold
             hover:bg-amber-50"
             @click="showOcrModal = true"
    >
      Open OCR
      <br />
      screen
    </button>
  </div>

  <!-- Status -->
  <div
    class="flex items-center
           justify-between
           gap-3
           mt-4"
  >
    <span
      class="inline-flex
             px-3 py-1
             rounded-lg
             bg-emerald-100
             text-emerald-700
             text-xs
             font-semibold"
    >
      Digital draft
    </span>

    <span class="text-sm text-gray-500">
      Not used for this visit
    </span>
  </div>

  <!-- Workflow content -->
  <div
    class="grid grid-cols-1
           md:grid-cols-2
           gap-4
           mt-5"
  >
    <!-- Uploaded source -->
    <div
      class="border border-gray-200
             rounded-xl
             p-4"
    >
      <h3 class="font-semibold text-gray-900">
        Uploaded source
      </h3>

      <div
        class="mt-4
               min-h-[260px]
               rounded-xl
               border border-dashed
               border-gray-300
               bg-amber-50/30
               flex flex-col
               items-center
               justify-center
               text-center
               px-4"
      >
        <div
          class="text-5xl
                 font-serif
                 text-gray-800
                 italic"
        >
          Rx
        </div>

        <p
          class="mt-4
                 text-sm
                 text-gray-700
                 leading-relaxed"
        >
          asha-follow-up-<br />
          note.jpg
        </p>

        <p
          class="mt-2
                 text-sm
                 text-gray-500"
        >
          Digital entry in progress
        </p>
      </div>
    </div>

    <!-- Extracted text -->
    <div>
      <h3 class="font-medium text-gray-900">
        Current extracted text
      </h3>

      <div
        class="mt-3
               min-h-[190px]
               rounded-xl
               border border-dashed
               border-gray-300
               p-4
               text-gray-700
               leading-relaxed
               bg-amber-50/20"
      >
        <p>
          Digital form started during consultation.
        </p>

        <p class="mt-4">
          No paper upload queued for OCR.
        </p>
      </div>

      <button
        type="button"
        class="w-full
               mt-4
               px-4 py-3
               rounded-xl
               bg-amber-500
               text-white
               font-semibold
               hover:bg-amber-600"
      >
        Review structured
        <br />
        prescription
      </button>
    </div>
  </div>
</section>

      </aside>
    </div>

    <!-- Template preview modal -->
<div
  v-if="showPreview"
  class="fixed inset-0 z-50
         bg-black/50
         flex items-center justify-center
         p-4"
  @click.self="showPreview = false"
>
  <div
    class="w-full
           max-w-4xl
           h-[90vh]
           bg-white
           rounded-2xl
           shadow-xl
           overflow-hidden
           flex flex-col"
  >

    <!-- Preview modal header -->
    <div
      class="flex items-center
             justify-between
             px-6 py-4
             border-b border-gray-200
             shrink-0"
    >
      <h2 class="text-2xl font-semibold text-gray-900">
        {{ patient.name }} prescription preview
      </h2>

      <button
        type="button"
        class="text-gray-500
               hover:text-gray-900
               text-3xl
               leading-none"
        @click="showPreview = false"
      >
        ×
      </button>
    </div>

    <!-- Scrollable prescription -->
    <div class="flex-1 overflow-y-auto px-5 py-5">
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
         gap-5
         pb-5
         border-b border-amber-200"
>
  <!-- CareYogi logo + details -->
  <div class="flex items-start gap-4">
    <img
      :src="careyogiLogo"
      alt="CareYogi"
      class="w-32
             h-auto
             object-contain
             shrink-0"
    />

    <div>
      <h3
        class="text-xl
               font-bold
               text-gray-900"
      >
                CAREYOGI DIGITAL CONSULTATION PRESCRIPTION
              </h3>

              <p class="text-sm text-gray-600 mt-2">
                5th Floor, Adilakshmi Square, Plot No.137,
                Old Mumbai Highway, Gachibowli, Hyderabad,
                Telangana - 500032
              </p>

              <p class="text-sm text-gray-600 mt-1">
                +91-9810918237 / info@careyogis.com
              </p>
            </div>
          </div>

          <!-- Status -->
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

        <!-- Patient / consultation details -->
        <div
          class="grid grid-cols-2
                 md:grid-cols-4
                 gap-3
                 mt-5"
        >
          <div
            v-for="item in previewDetails"
            :key="item.label"
            class="border border-gray-200
                   bg-white
                   rounded-xl
                   p-4"
          >
            <p class="text-xs text-gray-500">
              {{ item.label }}
            </p>

            <p
              class="font-bold
                     text-gray-900
                     mt-2"
            >
              {{ item.value }}
            </p>
          </div>
        </div>

        <!-- Doctor details -->
        <div
          class="grid grid-cols-1
                 md:grid-cols-3
                 gap-3
                 mt-4"
        >
          <div
            v-for="item in doctorDetails"
            :key="item.label"
            class="border border-gray-200
                   bg-white
                   rounded-xl
                   p-4"
          >
            <p class="text-xs text-gray-500">
              {{ item.label }}
            </p>

            <p
              class="font-bold
                     text-gray-900
                     mt-2"
            >
              {{ item.value }}
            </p>

            <p
              v-if="item.description"
              class="text-xs
                     text-gray-500
                     mt-1"
            >
              {{ item.description }}
            </p>
          </div>
        </div>

        <!-- Chief Complaints -->
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
            <li
              v-for="complaint in complaints"
              :key="complaint.id"
            >
              {{ complaint.text }}

              <span v-if="complaint.duration">
                ({{ complaint.duration }})
              </span>
            </li>
          </ul>
        </div>

        <!-- History -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            History (brief)
          </h3>

          <p
            class="text-sm
                   text-gray-700
                   mt-2"
          >
            {{ history || 'No history entered.' }}
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
                   gap-3
                   mt-3"
          >
            <div
              v-for="vital in vitals"
              :key="vital.label"
              class="border border-gray-200
                     bg-white
                     rounded-xl
                     p-4"
            >
              <p
                class="text-xs
                       uppercase
                       text-gray-500"
              >
                {{ vital.label }}
              </p>

              <p
                class="font-bold
                       text-gray-900
                       mt-2"
              >
                {{ vital.value }}
              </p>
            </div>
          </div>
        </div>

        <!-- Examination -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Examination
          </h3>

          <p
            class="text-sm
                   text-gray-700
                   mt-2"
          >
            {{ examination || 'No examination findings entered.' }}
          </p>
        </div>

        <!-- Provisional Diagnosis -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Provisional Diagnosis
          </h3>

          <p
            class="text-sm
                   text-gray-700
                   mt-2"
          >
            {{ provisionalDiagnosis || 'No provisional diagnosis entered.' }}
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
            <li
              v-for="investigation in investigations.filter(item => item)"
              :key="investigation"
            >
              {{ investigation }}
            </li>
          </ul>
        </div>

        <!-- Treatment / Medication -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Treatment / Medication
          </h3>

          <div class="mt-3 overflow-x-auto">
            <table
              class="w-full
                     text-left
                     text-sm"
            >
              <thead>
                <tr
                  class="bg-amber-100
                         border-b border-amber-200"
                >
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
                <tr
                  v-for="(medicine, index) in medicines"
                  :key="index"
                  class="border-b border-gray-200"
                >
                  <td class="px-3 py-2 text-gray-800">
                    {{ medicine.medicine }}
                  </td>

                  <td class="px-3 py-2 text-gray-800">
                    {{ medicine.dose }}
                  </td>

                  <td class="px-3 py-2 text-gray-800">
                    {{ medicine.frequency }}
                  </td>

                  <td class="px-3 py-2 text-gray-800">
                    {{ medicine.instruction }}
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

          <p
            class="text-sm
                   text-gray-700
                   mt-2"
          >
            {{ followUpAdvice || 'No follow-up advice entered.' }}
          </p>
        </div>

        <!-- Diet -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Diet Advice
          </h3>

          <p
            class="text-sm
                   text-gray-700
                   mt-2"
          >
            {{ dietAdvice || 'No diet advice entered.' }}
          </p>
        </div>

        <!-- Exercise -->
        <div class="mt-5">
          <h3 class="font-bold text-gray-900">
            Exercise Advice
          </h3>

          <p
            class="text-sm
                   text-gray-700
                   mt-2"
          >
            {{ exerciseAdvice || 'No exercise advice entered.' }}
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

          <p
            class="text-sm
                   text-gray-600
                   mt-2"
          >
            This is a digitally generated CareYogi prescription
            and does not require a physical signature.
          </p>
          <p
    class="text-sm
           text-gray-700
           mt-2"
  >
    © CareYogi 2026
  </p>
        </div>

      </div>
    </div>

    <!-- Preview footer -->
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
        @click="showPreview = false"
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
        @click="finalizeDraft"
      >
        Finalize draft
      </button>
    </div>

  </div>
</div>
</div>
<!-- OCR handwritten prescription modal -->
<div
  v-if="showOcrModal"
  class="fixed inset-0 z-50
         bg-black/50
         flex items-center justify-center
         p-4"
  @click.self="showOcrModal = false"
>
  <div
    class="w-full
           max-w-3xl
           max-h-[90vh]
           bg-white
           rounded-xl
           shadow-xl
           overflow-hidden"
  >

    <!-- Modal header -->
    <div
      class="flex items-center
             justify-between
             px-5 py-4
             border-b border-gray-200"
    >
      <h2 class="text-2xl font-semibold text-gray-900">
        OCR handwritten prescription
      </h2>

      <button
        type="button"
        class="text-gray-500
               hover:text-gray-900
               text-3xl
               leading-none"
        @click="showOcrModal = false"
      >
        ×
      </button>
    </div>

    <!-- Modal body -->
    <div
      class="max-h-[72vh]
             overflow-y-auto
             px-5 py-5"
    >

      <!-- Information banner -->
      <div
        class="rounded-lg
               border border-sky-300
               bg-sky-100
               px-5 py-4
               text-sky-900"
      >
        Doctor can complete the digital prescription during or after the consultation.
      </div>

      <!-- Two-column content -->
      <div
        class="grid grid-cols-1
               md:grid-cols-2
               gap-5
               mt-5"
      >

        <!-- Uploaded image -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            Uploaded image
          </h3>

          <div
            class="mt-2
                   h-[280px]
                   rounded-xl
                   border border-dashed
                   border-gray-300
                   bg-[#fffdf8]
                   flex flex-col
                   items-center
                   justify-center
                   text-center
                   px-5"
          >

            <div
              class="text-[72px]
                     leading-none
                     font-normal
                     italic
                     text-gray-800"
              style="font-family: 'Comic Sans MS', 'Segoe Print', cursive;"
            >
              Rx
            </div>

            <p
              class="mt-5
                     text-lg
                     font-medium
                     italic
                     text-gray-700"
            >
              asha-follow-up-note.jpg
            </p>

            <p
              class="mt-1
                     text-lg
                     italic
                     text-gray-700"
            >
              Digital entry in progress
            </p>

          </div>
        </div>

        <!-- Current system extraction -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            Current system extraction
          </h3>

          <div
            class="mt-2
                   min-h-[150px]
                   rounded-xl
                   border border-dashed
                   border-gray-300
                   p-4
                   text-gray-800"
          >
            <p class="text-base leading-7">
              Digital form started during consultation.
            </p>

            <p class="mt-6 text-base leading-7">
              No paper upload queued for OCR.
            </p>
          </div>
        </div>

      </div>
    </div>

    <!-- Modal footer -->
    <div
      class="flex items-center
             justify-end
             gap-3
             px-5 py-4
             border-t border-gray-200"
    >
      <button
        type="button"
        class="px-5 py-3
               rounded-xl
               bg-gray-100
               text-gray-800
               font-semibold
               hover:bg-gray-200"
        @click="showOcrModal = false"
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
      >
        Review structured draft
      </button>
    </div>

  </div>
</div>

</template>
<script setup>
import { computed, ref, watch } from 'vue'
import { FeatherIcon, createResource } from 'frappe-ui'
import careyogiLogo from '@/assets/images/logo-01.png'

const props = defineProps({
  selectedConsultation: {
    type: Object,
    default: null,
  },
})

const clinicalRecordResource = createResource({
  url: 'wellnest.wellnest.doctype.teleconsultation_clinical_record.teleconsultation_clinical_record.get_clinical_record',
})

const saveClinicalRecordResource = createResource({
  url: 'wellnest.wellnest.doctype.teleconsultation_clinical_record.teleconsultation_clinical_record.save_clinical_record',
})

const vitalsResource = createResource({
  url: 'wellnest.wellnest.doctype.vitals.vitals.get_consultation_vitals',
})

const saveVitalsResource = createResource({
  url: 'wellnest.wellnest.doctype.vitals.vitals.save_consultation_vitals',
})

const createPrescriptionResource = createResource({
  url: 'wellnest.api.prescription.create_consultation_prescription',
})
const updatePrescriptionResource = createResource({
  url: 'wellnest.api.prescription.update_consultation_prescription',
})

const savePrescriptionDraftResource = createResource({
  url: 'wellnest.api.prescription.save_consultation_prescription_draft',
})

const getPrescriptionResource = createResource({
  url: 'wellnest.api.prescription.get_consultation_prescription',
})

const confirmPrescriptionResource = createResource({
  url: 'wellnest.api.prescription.confirm_prescription',
})

const completePrescriptionResource = createResource({
  url: 'wellnest.api.prescription.complete_consultation_prescription',
})

const startDoctorReviewResource = createResource({
  url: 'wellnest.api.prescription.start_doctor_review',
})

const patient = computed(() => ({
 name: props.selectedConsultation?.patient || 'Not Available',
}))

const consultation = computed(() => ({
  reason:
    props.selectedConsultation?.reason ||
    'Survivorship care plan',

  mode:
    props.selectedConsultation?.mode ||
    'Clinic',

 time:
  props.selectedConsultation?.time ||
  'Not Available',
}))

// Clinical Record data
const complaints = ref([])
const investigations = ref([])

const history = ref('')
const examination = ref('')
const provisionalDiagnosis = ref('')

const followUpAdvice = ref('')
const dietAdvice = ref('')
const exerciseAdvice = ref('')

// Existing prescription data - KEEP FOR NOW
const medicines = ref([])
const prescriptionName = ref(null)
const prescriptionWorkflowState = ref(null)

// Existing vitals data - KEEP FOR NOW
const vitals = ref([
  {
    key: 'weight',
    label: 'Weight',
    placeholder: 'Weight',
    value: '',
    vitalType: 'Weight',
    unit: 'kg',
  },
  {
    key: 'height',
    label: 'Height',
    placeholder: 'Height',
    value: '',
    vitalType: 'Height',
    unit: 'cm',
  },
  {
    key: 'pulse',
    label: 'Pulse',
    placeholder: 'Pulse',
    value: '',
    vitalType: 'Heart Rate',
    unit: 'bpm',
  },
  {
    key: 'bp',
    label: 'BP',
    placeholder: 'Blood pressure',
    value: '',
    vitalType: 'BP',
    unit: 'mmHg',
  },
  {
    key: 'spo2',
    label: 'SpO2',
    placeholder: 'SpO2',
    value: '',
    vitalType: 'SPO2',
    unit: '%',
  },
  {
    key: 'temperature',
    label: 'Temperature',
    placeholder: 'Temperature',
    value: '',
    vitalType: 'Temperature',
    unit: '°C',
  },
  {
    key: 'sugar',
    label: 'Blood Sugar',
    placeholder: 'Blood sugar',
    value: '',
    vitalType: 'Sugar',
    unit: 'mg/dL',
  },
  {
    key: 'respiratory_rate',
    label: 'Respiratory Rate',
    placeholder: 'Respiratory rate',
    value: '',
    vitalType: 'Respiratory Rate',
    unit: 'breaths/min',
  },
])

const showPreview = ref(false)
const showJoinModal = ref(false)
const showOcrModal = ref(false)

async function loadClinicalRecord() {
  const appointment = props.selectedConsultation?.appointment

  if (!appointment) {
    return
  }

  try {
    // Load clinical record
    const response = await clinicalRecordResource.submit({
      appointment,
    })

    if (!response) {
      complaints.value = []
      investigations.value = []
      history.value = ''
      examination.value = ''
      provisionalDiagnosis.value = ''
      followUpAdvice.value = ''
      dietAdvice.value = ''
      exerciseAdvice.value = ''
    } else {
      complaints.value = (response.chief_complaints || []).map(
        (complaint, index) => ({
          id: index + 1,
          text: complaint.complaint || '',
          duration: complaint.duration || '',
        }),
      )

      investigations.value = (
        response.investigations || []
      ).map((item) => item.investigation || '')

      history.value = response.history || ''
      examination.value = response.examination || ''
      provisionalDiagnosis.value =
        response.provisional_diagnosis || ''

      followUpAdvice.value =
        response.follow_up_advice || ''

      dietAdvice.value =
        response.diet_advice || ''

      exerciseAdvice.value =
        response.exercise_advice || ''
    }

    // Load vitals
    const vitalsResponse = await vitalsResource.submit({
      appointment,
    })

    // Clear current UI values first
    vitals.value.forEach((vital) => {
      vital.value = ''
    })

    // Populate saved vital values
    if (vitalsResponse?.vital_reading) {
      vitalsResponse.vital_reading.forEach((reading) => {
        const matchingVital = vitals.value.find(
          (vital) => vital.vitalType === reading.vital_type,
        )

        if (matchingVital) {
          matchingVital.value = reading.value || ''
        }
      })
    }
  } catch (error) {
    console.error(
      'Failed to load consultation data:',
      error,
    )
  }
}

async function loadPrescription() {
  const appointment = props.selectedConsultation?.appointment

  if (!appointment) {
    return
  }

  try {
    const response = await getPrescriptionResource.submit({
      appointment,
    })

    if (!response) {
      return
    }
    prescriptionName.value = response.name
    prescriptionWorkflowState.value = response.workflow_state

    medicines.value = (response.medicines || []).map((medicine) => ({
      medicine: medicine.medicine_name || '',
      dose: medicine.dosage || '',
      frequency: medicine.timing || '',
      instruction: medicine.instructions || '',
    }))

    followUpAdvice.value = response.follow_up_advice || ''
    dietAdvice.value = response.diet_advice || ''
    exerciseAdvice.value = response.exercise_advice || ''
  } catch (error) {
    console.error('Failed to load prescription:', error)
  }
}

watch(
  () => props.selectedConsultation?.appointment,
  () => {
    loadClinicalRecord()
    loadPrescription()
  },
  { immediate: true },
)

const previewDetails = computed(() => [
  {
    label: 'Patient',
    value: patient.value.name || 'Not Available',
  },
  {
    label: 'Consultation Type',
    value: consultation.value.mode || 'Not Available',
  },
  {
    label: 'Date',
    value: consultation.value.time
      ? consultation.value.time.split(',')[0]
      : 'Not Available',
  },
  {
    label: 'Time',
    value: consultation.value.time
      ? consultation.value.time.split(',').slice(1).join(',').trim()
      : 'Not Available',
  },
  {
    label: 'Appointment ID',
    value: props.selectedConsultation?.appointment || 'Not Available',
  },
])
const doctorDetails = computed(() => [
  {
    label: 'Consulting Doctor',
    value: props.selectedConsultation?.practitioner || 'Not Available',
    description: '',
  },
  {
    label: 'Qualification',
    value: 'MBBS, MD (Internal Medicine)',
    description: '34 Years Experience',
  },
  {
    label: 'Registration',
   value: props.selectedConsultation?.registration_no || 'Not Available',
    description: 'Digitally signed draft',
  },
])
function addComplaint() {
  complaints.value.push({
    id: Date.now(),
    text: '',
    duration: '',
  })
}

function addInvestigation() {
  investigations.value.push('')
}

function removeInvestigation(index) {
  investigations.value.splice(index, 1)
}

function addMedicine() {
  medicines.value.push({
    medicine: '',
    dose: '',
    frequency: '',
    instruction: '',
  })
}

async function finalizePrescription() {
  if (
  prescriptionWorkflowState.value === 'Confirmed' ||
  prescriptionWorkflowState.value === 'Complete'
) {
  alert('This prescription has already been submitted for this patient.')
  return
}

  const appointment = props.selectedConsultation?.appointment

  if (!appointment) {
    alert('No consultation selected.')
    return
  }

    // Validate mandatory clinical findings before submitting prescription.
  const hasChiefComplaint = complaints.value.some(
    (complaint) => complaint.text?.trim(),
  )

  if (!hasChiefComplaint) {
    alert('Chief Complaint is required before submitting the prescription.')
    return
  }

  if (!history.value?.trim()) {
    alert('History is required before submitting the prescription.')
    return
  }

  if (!examination.value?.trim()) {
    alert('Examination is required before submitting the prescription.')
    return
  }

  if (!provisionalDiagnosis.value?.trim()) {
    alert(
      'Provisional Diagnosis is required before submitting the prescription.',
    )
    return
  }

  if (prescriptionWorkflowState.value === 'Confirmed') {
    alert('This prescription has already been submitted.')
    return
  }

  try {
    const medicinesPayload = medicines.value
      .filter((medicine) => medicine.medicine?.trim())
      .map((medicine) => ({
        medicine_name: medicine.medicine.trim(),
        dosage: medicine.dose?.trim() || '',
        timing: medicine.frequency?.trim() || '',
        duration: 'Not specified',
        instructions: medicine.instruction?.trim() || '',
      }))

    let response

    // If no prescription exists yet, create it as Draft first.
    if (!prescriptionName.value) {
      response = await createPrescriptionResource.submit({
        appointment,
        prescription_date: new Date().toISOString().split('T')[0],
        medicines: JSON.stringify(medicinesPayload),
        follow_up_advice: followUpAdvice.value || '',
        diet_advice: dietAdvice.value || '',
        exercise_advice: exerciseAdvice.value || '',
      })

      prescriptionName.value = response.name
      prescriptionWorkflowState.value = response.workflow_state
    } else {
      // Existing Draft: save the latest changes before submitting.
      if (prescriptionWorkflowState.value === 'Draft') {
        response = await savePrescriptionDraftResource.submit({
          name: prescriptionName.value,
          prescription_date: new Date().toISOString().split('T')[0],
          medicines: JSON.stringify(medicinesPayload),
          follow_up_advice: followUpAdvice.value || '',
          diet_advice: dietAdvice.value || '',
          exercise_advice: exerciseAdvice.value || '',
        })

        prescriptionWorkflowState.value = response.workflow_state
      }
    }

    response = await completePrescriptionResource.submit({
      name: prescriptionName.value,
    })

    prescriptionWorkflowState.value = response.workflow_state

    console.log('Prescription submitted:', response)
    alert('Prescription submitted successfully.')
  } catch (error) {
    console.error('Failed to submit prescription:', error)
    alert('Failed to submit prescription.')
  }
}

async function savePrescriptionDraft() {
    console.log(
    'Current prescription workflow state:',
    prescriptionWorkflowState.value
  )
if (
  prescriptionWorkflowState.value === 'Confirmed' ||
  prescriptionWorkflowState.value === 'Complete'
) {
  alert('This prescription has already been submitted for this patient.')
  return
}

  const appointment = props.selectedConsultation?.appointment

  if (!appointment) {
    alert('No consultation selected.')
    return
  }

  try {
    const medicinesPayload = medicines.value
      .filter((medicine) => medicine.medicine?.trim())
      .map((medicine) => ({
        medicine_name: medicine.medicine.trim(),
        dosage: medicine.dose?.trim() || '',
        timing: medicine.frequency?.trim() || '',
        duration: 'Not specified',
        instructions: medicine.instruction?.trim() || '',
      }))

    let response

   if (prescriptionName.value) {
  response = await savePrescriptionDraftResource.submit({
  name: prescriptionName.value,
  prescription_date: new Date().toISOString().split('T')[0],
  medicines: JSON.stringify(medicinesPayload),
  follow_up_advice: followUpAdvice.value || '',
  diet_advice: dietAdvice.value || '',
  exercise_advice: exerciseAdvice.value || '',
})

    } else {
      response = await createPrescriptionResource.submit({
  appointment,
  medicines: JSON.stringify(medicinesPayload),
  follow_up_advice: followUpAdvice.value || '',
  diet_advice: dietAdvice.value || '',
  exercise_advice: exerciseAdvice.value || '',
})
    }

    if (response?.name) {
      prescriptionName.value = response.name
    }

    if (response?.workflow_state) {
      prescriptionWorkflowState.value = response.workflow_state
    } else {
      prescriptionWorkflowState.value = 'Draft'
    }

    console.log('Prescription draft saved:', response)
    alert('Prescription saved as draft.')
  } catch (error) {
    console.error('Failed to save prescription draft:', error)
    alert('Failed to save prescription draft.')
  }
}

async function saveClinicalRecord() {
  const appointment = props.selectedConsultation?.appointment

  if (!appointment) {
    console.error('No consultation appointment selected.')
    return
  }

  const data = {
    chief_complaints: complaints.value
      .filter((complaint) => complaint.text?.trim())
      .map((complaint) => ({
        complaint: complaint.text.trim(),
        duration: complaint.duration?.trim() || '',
      })),

    history: history.value,

    examination: examination.value,

    provisional_diagnosis: provisionalDiagnosis.value,

    investigations: investigations.value
      .filter((investigation) => investigation?.trim())
      .map((investigation) => ({
        investigation: investigation.trim(),
      })),

    follow_up_advice: followUpAdvice.value,

    diet_advice: dietAdvice.value,

    exercise_advice: exerciseAdvice.value,
  }

  try {
    const response = await saveClinicalRecordResource.submit({
      appointment,
      data: JSON.stringify(data),
    })

    console.log('Clinical record saved:', response)

    const vitalReadings = vitals.value
      .filter((vital) => vital.value?.trim())
      .map((vital) => ({
        vital_type: vital.vitalType,
        unit: vital.unit,
        value: vital.value.trim(),
      }))

    const vitalsResponse = await saveVitalsResource.submit({
      appointment,
      readings: JSON.stringify(vitalReadings),
    })

    console.log('Vitals saved:', vitalsResponse)

    alert('Clinical record saved successfully.')
  } catch (error) {
    console.error('Failed to save clinical record:', error)
    alert('Failed to save clinical record:', error)
  }
}

function removeMedicine(index) {
  medicines.value.splice(index, 1)
}

function removeComplaint(index) {
  complaints.value.splice(index, 1)
}

function insertComplaintSuggestion() {
  complaints.value.push({
    id: Date.now(),
    text: 'Elevated fasting glucose readings',
    duration: '7 days',
  })
}

function insertHistorySuggestion() {
  history.value =
    'Known history of diabetes and hypertension.'
}

function insertExaminationSuggestion() {
  examination.value =
    'General condition reviewed and relevant systems examined.'
}

function insertDiagnosisSuggestion() {
  console.log('Diagnosis suggestion selected.')
}

function previewTemplate() {
  showPreview.value = true
}

defineExpose({
  previewTemplate,
  complaints,
  history,
  vitals,
  medicines,
  followUpAdvice,
  dietAdvice,
  exerciseAdvice,
  provisionalDiagnosis,
  investigations,
  previewDetails,
  doctorDetails,
})

async function finalizeDraft() {
  if (!prescriptionName.value) {
    alert('No prescription found.')
    return
  }

  try {
    const response = await confirmPrescriptionResource.submit({
      name: prescriptionName.value,
    })

    prescriptionWorkflowState.value =
      response.workflow_state

    console.log('Prescription confirmed:', response)

    alert('Prescription confirmed successfully.')
  } catch (error) {
    console.error('Failed to confirm prescription:', error)
    alert('Failed to confirm prescription.')
  }
}
</script>