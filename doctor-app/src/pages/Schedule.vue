<template>
  <div class="p-6 md:p-8">

    <!-- Page header -->
    <div
      class="flex flex-col
             xl:flex-row
             xl:items-start
             xl:justify-between
             gap-4
             mb-6"
    >
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          Doctor Availability
        </h1>

        <p class="text-gray-500 mt-1">
          Publish the time ranges when CareYogi can offer patient teleconsult bookings.
        </p>
      </div>

      <div class="flex flex-wrap gap-3">
        <button
          type="button"
          class="px-5 py-3
                 rounded-xl
                 bg-amber-500
                 text-white
                 font-semibold
                 hover:bg-amber-600"
          @click="showPublishModal = true"
        >
          Publish availability
        </button>

        <button
          type="button"
          class="px-5 py-3
                 rounded-xl
                 border border-amber-400
                 text-amber-700
                 font-semibold
                 hover:bg-amber-50"
                   @click="showUnavailableModal = true"
        >
          Update unavailable dates
        </button>
      </div>
    </div>

    <!-- Availability patterns -->
    <div
      class="grid grid-cols-1
             lg:grid-cols-3
             gap-5"
    >

      <!-- Weekly -->
      <section
        class="bg-white
               border border-gray-200
               rounded-2xl
               p-5"
      >
        <span
          class="inline-flex
                 px-2.5 py-1
                 rounded-lg
                 bg-amber-50
                 text-amber-600
                 text-xs
                 font-semibold"
        >
          Weekly
        </span>

        <h2 class="text-2xl font-semibold text-gray-900 mt-4">
          Monday to Saturday
        </h2>

        <div class="space-y-3 mt-5">

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Video consults
            </p>

            <p class="text-gray-500 mt-1">
              9:00 AM - 12:30 PM
            </p>
          </div>

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Clinic consults
            </p>

            <p class="text-gray-500 mt-1">
              2:00 PM - 5:00 PM
            </p>
          </div>

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Home visits
            </p>

            <p class="text-gray-500 mt-1">
              6:00 PM - 7:30 PM
            </p>
          </div>

        </div>
      </section>

      <!-- Biweekly -->
      <section
        class="bg-white
               border border-gray-200
               rounded-2xl
               p-5"
      >
        <span
          class="inline-flex
                 px-2.5 py-1
                 rounded-lg
                 bg-amber-50
                 text-amber-600
                 text-xs
                 font-semibold"
        >
          Biweekly
        </span>

        <h2 class="text-2xl font-semibold text-gray-900 mt-4">
          Alternate Sundays
        </h2>

        <div class="space-y-3 mt-5">

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Video consults
            </p>

            <p class="text-gray-500 mt-1">
              10:00 AM - 1:00 PM
            </p>
          </div>

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Clinic consults
            </p>

            <p class="text-gray-500 mt-1">
              Not available
            </p>
          </div>

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Home visits
            </p>

            <p class="text-gray-500 mt-1">
              Not available
            </p>
          </div>

        </div>
      </section>

      <!-- Monthly -->
      <section
        class="bg-white
               border border-gray-200
               rounded-2xl
               p-5"
      >
        <span
          class="inline-flex
                 px-2.5 py-1
                 rounded-lg
                 bg-amber-50
                 text-amber-600
                 text-xs
                 font-semibold"
        >
          Monthly
        </span>

        <h2 class="text-2xl font-semibold text-gray-900 mt-4">
          First Friday blocked for CME
        </h2>

        <div class="space-y-3 mt-5">

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Video consults
            </p>

            <p class="text-gray-500 mt-1">
              Not available
            </p>
          </div>

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Clinic consults
            </p>

            <p class="text-gray-500 mt-1">
              Not available
            </p>
          </div>

          <div
            class="border border-gray-200
                   rounded-xl
                   p-4"
          >
            <p class="font-semibold text-gray-900">
              Home visits
            </p>

            <p class="text-gray-500 mt-1">
              Not available
            </p>
          </div>

        </div>
      </section>

    </div>

    <!-- Published availability + unavailable dates -->
    <div
      class="grid grid-cols-1
             xl:grid-cols-[2fr_1fr]
             gap-5
             mt-6"
    >

      <!-- Published availability -->
      <section
        class="bg-white
               border border-gray-200
               rounded-2xl
               p-5"
      >
        <h2 class="text-2xl font-bold text-gray-900">
          Published availability
        </h2>

        <div class="overflow-x-auto mt-5">
          <table class="w-full text-left">
            <thead>
              <tr
                class="border-b border-gray-200
                       text-sm
                       text-gray-500"
              >
                <th class="py-3 pr-4">
                  Pattern
                </th>

                <th class="py-3 pr-4">
                  Applies to
                </th>

                <th class="py-3 pr-4">
                  Video
                </th>

                <th class="py-3 pr-4">
                  Clinic
                </th>

                <th class="py-3">
                  Home visit
                </th>
              </tr>
            </thead>

            <tbody class="text-gray-900">
              <tr class="border-b border-gray-200">
                <td class="py-4 pr-4">
                  Weekly
                </td>

                <td class="py-4 pr-4">
                  Monday to Saturday
                </td>

                <td class="py-4 pr-4">
                  9:00 AM - 12:30 PM
                </td>

                <td class="py-4 pr-4">
                  2:00 PM - 5:00 PM
                </td>

                <td class="py-4">
                  6:00 PM - 7:30 PM
                </td>
              </tr>

              <tr class="border-b border-gray-200">
                <td class="py-4 pr-4">
                  Biweekly
                </td>

                <td class="py-4 pr-4">
                  Alternate Sundays
                </td>

                <td class="py-4 pr-4">
                  10:00 AM - 1:00 PM
                </td>

                <td class="py-4 pr-4">
                  Not available
                </td>

                <td class="py-4">
                  Not available
                </td>
              </tr>

              <tr>
                <td class="py-4 pr-4">
                  Monthly
                </td>

                <td class="py-4 pr-4">
                  First Friday blocked for CME
                </td>

                <td class="py-4 pr-4">
                  Not available
                </td>

                <td class="py-4 pr-4">
                  Not available
                </td>

                <td class="py-4">
                  Not available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Unavailable dates -->
      <section
        class="bg-white
               border border-gray-200
               rounded-2xl
               p-5"
      >
        <h2 class="text-2xl font-bold text-gray-900">
          Unavailable dates
        </h2>

        <p class="text-gray-500 mt-2">
          These are doctor availability blocks only.
          No patient booking data is shown here.
        </p>

        <div class="mt-5">

          <div
            class="flex items-center
                   justify-between
                   gap-4
                   py-4
                   border-b border-gray-200"
          >
            <span class="text-gray-700">
              15 Aug 2026
            </span>

            <span class="font-semibold text-gray-900">
              Full day
            </span>
          </div>

          <div
            class="flex items-center
                   justify-between
                   gap-4
                   py-4
                   border-b border-gray-200"
          >
            <span class="text-gray-700">
              First Friday monthly
            </span>

            <span class="font-semibold text-gray-900">
              CME block
            </span>
          </div>

          <div
            class="flex items-center
                   justify-between
                   gap-4
                   py-4"
          >
            <span class="text-gray-700">
              28 Jul 2026
            </span>

            <span class="font-semibold text-gray-900">
              After 2 PM
            </span>
          </div>

        </div>

        <button
          type="button"
          class="w-full
                 mt-4
                 px-5 py-3
                 rounded-xl
                 border border-amber-400
                 text-amber-700
                 font-semibold
                 hover:bg-amber-50"
                 @click="showUnavailableModal = true"
        >
          Manage unavailable dates
        </button>
      </section>

    </div>

  </div>

  <!-- Publish availability modal -->
  <div
    v-if="showPublishModal"
    class="fixed inset-0 z-50
           bg-black/50
           flex items-center justify-center
           p-4"
    @click.self="showPublishModal = false"
  >
    <div
      class="w-full
             max-w-5xl
             max-h-[90vh]
             bg-white
             rounded-2xl
             shadow-xl
             overflow-hidden"
    >

      <!-- Modal header -->
      <div
        class="flex items-center
               justify-between
               px-6 py-4
               border-b border-gray-200"
      >
        <h2 class="text-2xl font-semibold text-gray-900">
          Publish availability
        </h2>

        <button
          type="button"
          class="text-gray-500
                 hover:text-gray-900
                 text-3xl
                 leading-none"
          @click="showPublishModal = false"
        >
          ×
        </button>
      </div>

      <!-- Modal body -->
      <div
        class="px-6 py-5
               max-h-[70vh]
               overflow-y-auto"
      >
        <p class="text-gray-500 mb-6">
          Set simple doctor availability windows. Patients can book only inside these ranges.
        </p>

        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr
                class="border-b border-gray-200
                       text-sm
                       font-semibold
                       text-gray-900"
              >
                <th class="px-2 py-3">
                  Pattern
                </th>

                <th class="px-2 py-3">
                  Days
                </th>

                <th class="px-2 py-3">
                  Video
                </th>

                <th class="px-2 py-3">
                  Clinic
                </th>

                <th class="px-2 py-3">
                  Home
                </th>
              </tr>
            </thead>

            <tbody>

              <!-- Weekly -->
              <tr class="border-b border-gray-200">
                <td class="px-2 py-3 font-medium text-gray-900">
                  Weekly
                </td>

                <td class="px-2 py-3 text-gray-700">
                  Monday to Saturday
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="9:00 AM - 12:30 PM"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="2:00 PM - 5:00 PM"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="6:00 PM - 7:30 PM"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>
              </tr>

              <!-- Biweekly -->
              <tr class="border-b border-gray-200">
                <td class="px-2 py-3 font-medium text-gray-900">
                  Biweekly
                </td>

                <td class="px-2 py-3 text-gray-700">
                  Alternate Sundays
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="10:00 AM - 1:00 PM"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="Not available"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="Not available"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>
              </tr>

              <!-- Monthly -->
              <tr>
                <td class="px-2 py-3 font-medium text-gray-900">
                  Monthly
                </td>

                <td class="px-2 py-3 text-gray-700">
                  First Friday blocked for CME
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="Not available"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="Not available"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>

                <td class="px-2 py-3">
                  <input
                    type="text"
                    value="Not available"
                    class="w-full
                           rounded-lg
                           border border-gray-200
                           px-3 py-2
                           focus:outline-none
                           focus:ring-2
                           focus:ring-amber-200"
                  />
                </td>
              </tr>

            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal footer -->
      <div
        class="flex items-center
               justify-end
               gap-3
               px-6 py-4
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
          @click="showPublishModal = false"
        >
          Cancel
        </button>

        <button
          type="button"
          class="px-5 py-3
                 rounded-xl
                 bg-amber-500
                 text-white
                 font-semibold
                 hover:bg-amber-600"
          @click="showPublishModal = false"
        >
          Publish ranges
        </button>
      </div>

    </div>
  </div>
<!-- Unavailable dates modal -->
<div
  v-if="showUnavailableModal"
  class="fixed inset-0 z-50
         bg-black/50
         flex items-center justify-center
         p-4"
  @click.self="showUnavailableModal = false"
>
  <div
    class="w-full
           max-w-4xl
           bg-white
           rounded-2xl
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
        Unavailable dates
      </h2>

      <button
        type="button"
        class="text-gray-500
               hover:text-gray-900
               text-3xl
               leading-none"
        @click="showUnavailableModal = false"
      >
        ×
      </button>
    </div>

    <!-- Modal body -->
    <div class="px-5 py-5">

      <p class="text-gray-500 mb-6">
        Block doctor availability. This does not show or edit patient bookings.
      </p>

      <div
        class="grid grid-cols-1
               md:grid-cols-2
               gap-5"
      >

        <!-- Date -->
        <div>
          <label
            class="block
                   text-sm
                   font-medium
                   text-gray-900
                   mb-2"
          >
            Date
          </label>

          <input
            v-model="unavailableDate"
            type="text"
            class="w-full
                   rounded-xl
                   border border-gray-200
                   px-4 py-3
                   text-gray-900
                   focus:outline-none
                   focus:ring-2
                   focus:ring-amber-200"
          />
        </div>

        <!-- Availability -->
        <div>
          <label
            class="block
                   text-sm
                   font-medium
                   text-gray-900
                   mb-2"
          >
            Availability
          </label>

          <select
            v-model="unavailableType"
            class="w-full
                   rounded-xl
                   border border-gray-200
                   px-4 py-3
                   text-gray-900
                   bg-white
                   focus:outline-none
                   focus:ring-2
                   focus:ring-amber-200"
          >
            <option value="Full day unavailable">
              Full day unavailable
            </option>

            <option value="Morning unavailable">
              Morning unavailable
            </option>

            <option value="After 2 PM unavailable">
              After 2 PM unavailable
            </option>
          </select>
        </div>

      </div>

      <!-- Reason -->
      <div class="mt-5">
        <label
          class="block
                 text-sm
                 font-medium
                 text-gray-900
                 mb-2"
        >
          Reason shown internally
        </label>

        <input
          v-model="unavailableReason"
          type="text"
          class="w-full
                 rounded-xl
                 border border-gray-200
                 px-4 py-3
                 text-gray-900
                 focus:outline-none
                 focus:ring-2
                 focus:ring-amber-200"
        />
      </div>

    </div>

    <!-- Footer -->
    <div
      class="flex items-center
             justify-end
             px-5 py-4
             border-t border-gray-200"
    >
      <button
        type="button"
        class="px-5 py-3
               rounded-xl
               bg-amber-500
               text-white
               font-semibold
               hover:bg-amber-600"
        @click="showUnavailableModal = false"
      >
        Save unavailable date
      </button>
    </div>

  </div>
</div>

</template>

<script setup>
import { ref } from 'vue'

const showPublishModal = ref(false)

const showUnavailableModal = ref(false)
const unavailableDate = ref('15 Aug 2026')
const unavailableType = ref('Full day unavailable')
const unavailableReason = ref('Personal leave')
</script>