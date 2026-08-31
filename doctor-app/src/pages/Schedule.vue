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
            v-if="loadingTimeaway"
            class="py-4 text-gray-500"
          >
            Loading unavailable dates...
          </div>

          <div
            v-else-if="!timeawayRecords.length"
            class="py-4 text-gray-500"
          >
            No unavailable dates configured.
          </div>

          <div
            v-else
            class="space-y-0"
          >
            <div
              v-for="record in timeawayRecords"
              :key="record.name"
              class="flex items-center
                     justify-between
                     gap-4
                     py-4
                     border-b border-gray-200"
            >
              <span class="text-gray-700">
                {{ formatDate(record.from_date) }}
                <span
                  v-if="record.to_date && record.to_date !== record.from_date"
                >
                  - {{ formatDate(record.to_date) }}
                </span>
              </span>

              <div class="text-right">
                <div class="font-semibold text-gray-900">
                  {{ formatTime(record.from_time) }}
                  -
                  {{ formatTime(record.to_time) }}
                </div>

                <div
                  v-if="record.reason"
                  class="text-sm text-gray-500 mt-1"
                >
                  {{ record.reason }}
                </div>

                <div class="flex justify-end gap-3 mt-2">
                  <button
                    type="button"
                    class="text-sm font-medium text-amber-600 hover:text-amber-700"
                    @click="editTimeaway(record)"
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    class="text-sm font-medium text-red-600 hover:text-red-700"
                    @click="cancelTimeaway(record)"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
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
        {{ editingTimeaway ? 'Edit unavailable date' : 'Unavailable dates' }}
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
            type="date"
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
              hover:bg-amber-600
              disabled:opacity-50"
        :disabled="savingTimeaway"
        @click="saveUnavailableDate"
      >
        {{ savingTimeaway ? 'Saving...' : 'Save unavailable date' }}
      </button>
    </div>

  </div>
</div>

</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createResource } from 'frappe-ui'

const showPublishModal = ref(false)

const showUnavailableModal = ref(false)
const unavailableDate = ref('')
const unavailableType = ref('Full day unavailable')
const unavailableReason = ref('')

const timeawayRecords = ref([])
const loadingTimeaway = ref(false)
const savingTimeaway = ref(false)
const editingTimeaway = ref(null)

const timeawayResource = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.get_doctor_timeaway',
  onSuccess(data) {
    timeawayRecords.value = data || []
  },
})

const saveTimeawayResource = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.save_doctor_timeaway',
})

const cancelTimeawayResource = createResource({
  url: 'wellnest.health.doctype.practitioner.practitioner.cancel_doctor_timeaway',
})

function getTimeRange(type) {
  switch (type) {
    case 'Morning unavailable':
      return {
        from_time: '00:00:00',
        to_time: '12:00:00',
      }

    case 'After 2 PM unavailable':
      return {
        from_time: '14:00:00',
        to_time: '23:59:59',
      }

    case 'Full day unavailable':
    default:
      return {
        from_time: '00:00:00',
        to_time: '23:59:59',
      }
  }
}

function getUnavailableType(fromTime, toTime) {
  if (fromTime === '00:00:00' && toTime === '23:59:59') {
    return 'Full day unavailable'
  }

  if (fromTime === '00:00:00' && toTime === '12:00:00') {
    return 'Morning unavailable'
  }

  if (fromTime === '14:00:00' && toTime === '23:59:59') {
    return 'After 2 PM unavailable'
  }

  return 'Full day unavailable'
}

function editTimeaway(record) {
  editingTimeaway.value = record
  unavailableDate.value = record.from_date
  unavailableType.value = getUnavailableType(
    record.from_time,
    record.to_time
  )
  unavailableReason.value = record.reason || ''
  showUnavailableModal.value = true
}

async function saveUnavailableDate() {
  if (!unavailableDate.value) {
    alert('Please select a date.')
    return
  }

  const { from_time, to_time } = getTimeRange(unavailableType.value)

  savingTimeaway.value = true

  try {
    await saveTimeawayResource.submit({
      name: editingTimeaway.value?.name || null,
      from_date: unavailableDate.value,
      to_date: unavailableDate.value,
      from_time,
      to_time,
      reason: unavailableReason.value || null,
    })

    await loadTimeaway()

    showUnavailableModal.value = false
    editingTimeaway.value = null
    unavailableDate.value = ''
    unavailableType.value = 'Full day unavailable'
    unavailableReason.value = ''
  } catch (err) {
    console.error('Failed to save unavailable date:', err)
    alert('Failed to save unavailable date.')
  } finally {
    savingTimeaway.value = false
  }
}

async function cancelTimeaway(record) {
  if (!confirm('Remove this unavailable period?')) {
    return
  }

  try {
    await cancelTimeawayResource.submit({
      name: record.name,
    })

    await loadTimeaway()
  } catch (err) {
    console.error('Failed to remove unavailable date:', err)
    alert('Failed to remove unavailable date.')
  }
}

async function loadTimeaway() {
  loadingTimeaway.value = true

  try {
    await timeawayResource.fetch()
  } catch (err) {
    console.error('Failed to load unavailable dates:', err)
  } finally {
    loadingTimeaway.value = false
  }
}

function formatDate(date) {
  if (!date) return ''

  const value = new Date(`${date}T00:00:00`)

  return value.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function formatTime(time) {
  if (!time) return ''

  const [hours, minutes] = time.split(':')
  const value = new Date()

  value.setHours(Number(hours), Number(minutes), 0, 0)

  return value.toLocaleTimeString('en-IN', {
    hour: 'numeric',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadTimeaway()
})
</script>