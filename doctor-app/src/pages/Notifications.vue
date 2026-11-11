
<template>
  <main class="mx-auto w-full max-w-7xl px-4 py-5 sm:px-6 sm:py-7 lg:px-8">
    <!-- Page heading -->
    <section class="mb-7 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
      <div>
        <div class="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-teal-700">
          <span class="h-2 w-2 rounded-full bg-teal-500"></span>
          Activity centre
        </div>
        <h1 class="text-2xl font-bold tracking-tight text-gray-950 sm:text-3xl">
          Notifications
        </h1>
        <p class="mt-2 max-w-xl text-sm leading-6 text-gray-500 sm:text-base">
          Stay informed about your consultations and patient conversations.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          class="inline-flex h-10 items-center gap-2 rounded-xl border border-gray-200 bg-white px-3.5 text-sm font-semibold text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="loading"
          @click="loadNotifications"
        >
          <FeatherIcon
            name="refresh-cw"
            class="h-4 w-4"
            :class="{ 'animate-spin': loading }"
          />
          <span>Refresh</span>
        </button>

        <button
          v-if="unreadCount > 0"
          type="button"
          class="inline-flex h-10 items-center gap-2 rounded-xl bg-gray-900 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="markingAll"
          @click="markAllAsRead"
        >
          <FeatherIcon
            :name="markingAll ? 'loader' : 'check-check'"
            class="h-4 w-4"
            :class="{ 'animate-spin': markingAll }"
          />
          Mark all as read
        </button>
      </div>
    </section>

    <!-- Overview -->
    <section class="mb-7 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div class="relative overflow-hidden rounded-2xl border border-amber-200/70 bg-gradient-to-br from-amber-50 via-white to-white p-5 shadow-sm">
        <div class="relative z-10 flex items-center justify-between gap-4">
          <div>
            <p class="text-sm font-medium text-amber-900/75">Unread notifications</p>
            <p class="mt-2 text-3xl font-bold tracking-tight text-gray-950 tabular-nums">
              {{ unreadCount }}
            </p>
            <p class="mt-1 text-xs text-gray-500">Items that may need your attention</p>
          </div>
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-amber-100 text-amber-700">
            <FeatherIcon name="bell-ring" class="h-6 w-6" />
          </div>
        </div>
        <div class="pointer-events-none absolute -bottom-9 -right-5 h-28 w-28 rounded-full border-[18px] border-amber-100/60"></div>
      </div>

      <div class="relative overflow-hidden rounded-2xl border border-teal-100 bg-gradient-to-br from-teal-50 via-white to-white p-5 shadow-sm">
        <div class="relative z-10 flex items-center justify-between gap-4">
          <div>
            <p class="text-sm font-medium text-teal-900/75">Your notification inbox</p>
            <p class="mt-2 text-3xl font-bold tracking-tight text-gray-950 tabular-nums">
              {{ totalCount }}
            </p>
            <p class="mt-1 text-xs text-gray-500">Total notifications in your history</p>
          </div>
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-teal-100 text-teal-700">
            <FeatherIcon name="inbox" class="h-6 w-6" />
          </div>
        </div>
        <div class="pointer-events-none absolute -bottom-9 -right-5 h-28 w-28 rounded-full border-[18px] border-teal-100/60"></div>
      </div>
    </section>

    <!-- Notification inbox -->
    <section class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <!-- Toolbar -->
      <div class="border-b border-gray-100 px-4 py-4 sm:px-6">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-base font-bold text-gray-900">Your activity</h2>
            <p class="mt-0.5 text-xs text-gray-500">
              Consultation bookings and messages from patients
            </p>
          </div>

          <div
            class="flex w-full items-center gap-1 rounded-xl bg-gray-100 p-1 sm:w-auto"
            role="tablist"
            aria-label="Filter notifications"
          >
            <button
              v-for="tab in tabs"
              :key="tab.value"
              type="button"
              role="tab"
              :aria-selected="activeFilter === tab.value"
              class="flex-1 rounded-lg px-3 py-2 text-xs font-semibold transition sm:flex-none sm:px-4"
              :class="activeFilter === tab.value
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-800'"
              @click="changeFilter(tab.value)"
            >
              {{ tab.label }}
              <span
                v-if="tab.value === 'Unread' && unreadCount > 0"
                class="ml-1.5 rounded-full bg-amber-100 px-1.5 py-0.5 text-[10px] text-amber-800"
              >
                {{ unreadCount }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Error state -->
      <div v-if="error" class="m-4 flex flex-col gap-3 rounded-xl border border-red-200 bg-red-50 p-4 sm:m-6 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-start gap-3">
          <FeatherIcon name="alert-circle" class="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
          <div>
            <p class="text-sm font-semibold text-red-900">Couldn't load notifications</p>
            <p class="mt-1 break-words text-xs leading-5 text-red-700">{{ error }}</p>
          </div>
        </div>
        <button
          type="button"
          class="self-start rounded-lg border border-red-200 bg-white px-3 py-2 text-xs font-semibold text-red-700 hover:bg-red-100 sm:self-center"
          @click="loadNotifications"
        >
          Try again
        </button>
      </div>

      <!-- Loading skeleton -->
      <div v-else-if="loading && !notifications.length" class="space-y-4 p-4 sm:p-6" aria-label="Loading notifications" aria-busy="true">
        <div v-for="item in 5" :key="item" class="flex animate-pulse gap-4 rounded-xl border border-gray-100 p-4">
          <div class="h-11 w-11 shrink-0 rounded-xl bg-gray-100"></div>
          <div class="min-w-0 flex-1 space-y-3 py-1">
            <div class="h-3 w-2/5 rounded bg-gray-100"></div>
            <div class="h-3 w-4/5 rounded bg-gray-100"></div>
            <div class="h-2.5 w-1/4 rounded bg-gray-100"></div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!notifications.length" class="px-5 py-16 text-center sm:py-20">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-50 ring-1 ring-gray-100">
          <FeatherIcon
            :name="activeFilter === 'Unread' ? 'check-circle' : 'bell'"
            class="h-7 w-7 text-gray-400"
          />
        </div>
        <h3 class="mt-5 text-base font-bold text-gray-900">
          {{ emptyTitle }}
        </h3>
        <p class="mx-auto mt-2 max-w-sm text-sm leading-6 text-gray-500">
          {{ emptyDescription }}
        </p>
        <button
          v-if="activeFilter !== 'All'"
          type="button"
          class="mt-5 text-sm font-semibold text-teal-700 hover:text-teal-800"
          @click="changeFilter('All')"
        >
          View all notifications
        </button>
      </div>

      <!-- Notification list -->
      <div v-else class="divide-y divide-gray-100">
        <section
          v-for="group in groupedNotifications"
          :key="group.key"
        >
          <div class="flex items-center justify-between bg-gray-50/70 px-4 py-3 sm:px-6">
            <h3 class="text-xs font-bold uppercase tracking-wider text-gray-500">
              {{ group.label }}
            </h3>
            <span class="text-[11px] font-medium text-gray-400">
              {{ group.items.length }} {{ group.items.length === 1 ? 'notification' : 'notifications' }}
            </span>
          </div>

          <article
            v-for="notification in group.items"
            :key="notification.name"
            class="group relative flex min-w-0 gap-3 px-4 py-4 transition-colors hover:bg-gray-50/80 sm:gap-4 sm:px-6"
            :class="notification.is_read ? 'bg-white' : 'bg-amber-50/30'"
          >
            <div
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl"
              :class="notification.notification_type === 'Consultation Booked'
                ? 'bg-blue-50 text-blue-700'
                : 'bg-teal-50 text-teal-700'"
            >
              <FeatherIcon
                :name="notification.notification_type === 'Consultation Booked' ? 'calendar-check' : 'message-circle'"
                class="h-5 w-5"
              />
            </div>

            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
                <h4 class="min-w-0 break-words text-sm font-bold text-gray-900">
                  {{ notification.title }}
                </h4>
                <span
                  v-if="!notification.is_read"
                  class="inline-flex shrink-0 items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-800"
                >
                  <span class="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
                  New
                </span>
              </div>

              <p class="mt-1 break-words text-sm leading-6 text-gray-600">
                {{ notification.description }}
              </p>

              <div class="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-gray-400">
                <span class="font-semibold text-gray-600">
                  {{ notification.patient_name || notification.patient }}
                </span>
                <span aria-hidden="true">·</span>
                <span>{{ formatDateTime(notification.event_time) }}</span>
                <template v-if="notification.is_read && notification.read_at">
                  <span aria-hidden="true">·</span>
                  <span>Read {{ formatRelativeTime(notification.read_at) }}</span>
                </template>
              </div>

              <div class="mt-3 flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  class="inline-flex min-h-9 items-center gap-1.5 rounded-lg bg-gray-900 px-3 py-2 text-xs font-semibold text-white transition hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
                  @click="openNotification(notification)"
                >
                  {{ notification.notification_type === 'Consultation Booked' ? 'View consultation' : 'Open conversation' }}
                  <FeatherIcon name="arrow-up-right" class="h-3.5 w-3.5" />
                </button>

                <button
                  v-if="!notification.is_read"
                  type="button"
                  class="inline-flex min-h-9 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold text-gray-600 transition hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-300"
                  :disabled="busyNotification === notification.name"
                  @click="markAsRead(notification)"
                >
                  <FeatherIcon name="check" class="h-3.5 w-3.5" />
                  Mark as read
                </button>
              </div>
            </div>

            <span
              v-if="!notification.is_read"
              class="mt-2 h-2 w-2 shrink-0 rounded-full bg-amber-500"
              aria-label="Unread"
            ></span>
          </article>
        </section>
      </div>

      <!-- Pagination -->
      <footer
        v-if="totalPages > 1"
        class="flex flex-col gap-3 border-t border-gray-100 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6"
      >
        <p class="text-xs text-gray-500">
          Showing
          <span class="font-semibold text-gray-800">{{ firstItem }}</span>
          –
          <span class="font-semibold text-gray-800">{{ lastItem }}</span>
          of
          <span class="font-semibold text-gray-800">{{ filteredTotal }}</span>
        </p>

        <div class="flex items-center gap-2">
          <button
            type="button"
            class="inline-flex h-9 items-center gap-1 rounded-lg border border-gray-200 px-3 text-xs font-semibold text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="page <= 1 || loading"
            @click="changePage(page - 1)"
          >
            <FeatherIcon name="chevron-left" class="h-4 w-4" />
            Previous
          </button>
          <span class="px-2 text-xs font-medium text-gray-500">
            {{ page }} / {{ totalPages }}
          </span>
          <button
            type="button"
            class="inline-flex h-9 items-center gap-1 rounded-lg border border-gray-200 px-3 text-xs font-semibold text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="page >= totalPages || loading"
            @click="changePage(page + 1)"
          >
            Next
            <FeatherIcon name="chevron-right" class="h-4 w-4" />
          </button>
        </div>
      </footer>
    </section>

    <p class="mt-4 flex items-center justify-center gap-2 text-center text-[11px] text-gray-400">
      <FeatherIcon name="shield-check" class="h-3.5 w-3.5" />
      Your notification history is private to your account.
    </p>

    <div
      v-if="successMessage"
      class="fixed bottom-5 left-1/2 z-50 flex max-w-[calc(100vw-2rem)] -translate-x-1/2 items-center gap-2 rounded-xl bg-gray-900 px-4 py-3 text-sm font-medium text-white shadow-xl"
      role="status"
      aria-live="polite"
    >
      <FeatherIcon name="check-circle" class="h-4 w-4 shrink-0 text-emerald-400" />
      {{ successMessage }}
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const PAGE_LENGTH = 20
const API_BASE = '/api/method/wellnest.api.doctor_notifications'

const tabs = [
  { label: 'All', value: 'All' },
  { label: 'Unread', value: 'Unread' },
  { label: 'Read', value: 'Read' },
]

const notifications = ref([])
const activeFilter = ref('All')
const loading = ref(false)
const error = ref('')
const page = ref(1)
const filteredTotal = ref(0)
const totalCount = ref(0)
const unreadCount = ref(0)
const busyNotification = ref(null)
const markingAll = ref(false)
const successMessage = ref('')
let requestVersion = 0
let successTimer = null

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredTotal.value / PAGE_LENGTH)),
)

const firstItem = computed(() =>
  filteredTotal.value ? (page.value - 1) * PAGE_LENGTH + 1 : 0,
)

const lastItem = computed(() =>
  Math.min(page.value * PAGE_LENGTH, filteredTotal.value),
)

const emptyTitle = computed(() => {
  if (activeFilter.value === 'Unread') return "You're all caught up"
  if (activeFilter.value === 'Read') return 'No read notifications yet'
  return 'Your inbox is quiet'
})

const emptyDescription = computed(() => {
  if (activeFilter.value === 'Unread') {
    return 'There are no unread notifications. New consultation bookings and patient messages will appear here.'
  }
  if (activeFilter.value === 'Read') {
    return 'Notifications you have read will remain available here for future reference.'
  }
  return 'When patients book consultations or send you messages, you will see them here.'
})

const groupedNotifications = computed(() => {
  const groups = new Map()

  for (const item of notifications.value) {
    const date = item.event_time ? new Date(item.event_time.replace(' ', 'T')) : null
    const key = date && !Number.isNaN(date.getTime())
      ? date.toLocaleDateString('en-IN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
        })
      : 'unknown'

    if (!groups.has(key)) {
      groups.set(key, {
        key,
        label: getDateGroupLabel(date),
        items: [],
      })
    }

    groups.get(key).items.push(item)
  }

  return Array.from(groups.values())
})

async function requestApi(method, args = {}, httpMethod = 'GET') {
  const url = new URL(`${API_BASE}.${method}`, window.location.origin)

  const options = {
    method: httpMethod,
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
    },
  }

  if (httpMethod === 'GET') {
    Object.entries(args).forEach(([key, value]) => {
      url.searchParams.set(key, String(value))
    })
  } else {
    options.headers['Content-Type'] = 'application/json'
    options.headers['X-Frappe-CSRF-Token'] = window.csrf_token || ''
    options.body = JSON.stringify(args)
  }

  const response = await fetch(url.toString(), options)
  const result = await response.json()

  if (!response.ok || result.exc || result.exception) {
    throw new Error(
      result.message || result._server_messages || `Request failed (${response.status})`,
    )
  }

  return result.message
}

async function loadNotifications() {
  const currentRequest = ++requestVersion
  loading.value = true
  error.value = ''

  try {
    const [listResult, unreadResult, allResult] = await Promise.all([
      requestApi('get_doctor_notifications', {
        page: page.value,
        page_length: PAGE_LENGTH,
        status: activeFilter.value,
      }),
      requestApi('get_doctor_notifications', {
        page: 1,
        page_length: 1,
        status: 'Unread',
      }),
      requestApi('get_doctor_notifications', {
        page: 1,
        page_length: 1,
        status: 'All',
      }),
    ])

    if (currentRequest !== requestVersion) return

    notifications.value = listResult?.notifications || []
    filteredTotal.value = Number(listResult?.total || 0)
    unreadCount.value = Number(unreadResult?.total || 0)
    totalCount.value = Number(allResult?.total || 0)

    if (page.value > totalPages.value) {
      page.value = totalPages.value
      await loadNotifications()
    }
  } catch (err) {
    if (currentRequest !== requestVersion) return
    console.error('Failed to load doctor notifications:', err)
    error.value = typeof err.message === 'string'
      ? err.message
      : 'Please check your connection and try again.'
  } finally {
    if (currentRequest === requestVersion) {
      loading.value = false
    }
  }
}

async function changeFilter(filter) {
  if (activeFilter.value === filter) return
  activeFilter.value = filter
  page.value = 1
  await loadNotifications()
}

async function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  page.value = nextPage
  await loadNotifications()
}

async function markAsRead(notification) {
  if (notification.is_read || busyNotification.value) return

  busyNotification.value = notification.name

  try {
    const result = await requestApi(
      'mark_doctor_notification_read',
      { notification_name: notification.name },
      'POST',
    )

    notification.is_read = true
    notification.read_at = result?.read_at || new Date().toISOString()
    unreadCount.value = Math.max(0, unreadCount.value - 1)

    if (activeFilter.value === 'Unread') {
      await loadNotifications()
    }

    showSuccess('Notification marked as read')
  } catch (err) {
    console.error('Failed to mark notification as read:', err)
    error.value = err.message || 'Could not update notification.'
  } finally {
    busyNotification.value = null
  }
}

async function markAllAsRead() {
  if (!unreadCount.value || markingAll.value) return

  markingAll.value = true

  try {
    await requestApi('mark_all_doctor_notifications_read', {}, 'POST')

    notifications.value.forEach((item) => {
      item.is_read = true
      item.read_at = new Date().toISOString()
    })

    unreadCount.value = 0

    if (activeFilter.value === 'Unread') {
      page.value = 1
      await loadNotifications()
    } else {
      await loadNotifications()
    }

    showSuccess('All notifications marked as read')
  } catch (err) {
    console.error('Failed to mark all notifications as read:', err)
    error.value = err.message || 'Could not update notifications.'
  } finally {
    markingAll.value = false
  }
}

async function openNotification(notification) {
  try {
    if (!notification.is_read) {
      await markAsRead(notification)
    }

    if (notification.notification_type === 'Consultation Booked') {
      await router.push({
        name: 'ConsultationDetails',
        params: { bookingId: notification.patient_appointment },
      })
      return
    }

    if (notification.notification_type === 'Patient Message') {
      await router.push({
        name: 'Messages',
        query: {
          patient: notification.patient,
          appointment: notification.patient_appointment,
        },
      })
    }
  } catch (err) {
    console.error('Failed to open notification destination:', err)
  }
}

function showSuccess(message) {
  successMessage.value = message
  if (successTimer) clearTimeout(successTimer)
  successTimer = setTimeout(() => {
    successMessage.value = ''
  }, 2600)
}

function getDateGroupLabel(date) {
  if (!date || Number.isNaN(date.getTime())) return 'Date unavailable'

  const today = new Date()
  const yesterday = new Date()
  yesterday.setDate(today.getDate() - 1)

  if (date.toDateString() === today.toDateString()) return 'Today'
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday'

  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function formatDateTime(value) {
  if (!value) return 'Time unavailable'

  const date = new Date(value.replace(' ', 'T'))
  if (Number.isNaN(date.getTime())) return 'Time unavailable'

  return date.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatRelativeTime(value) {
  if (!value) return ''

  const date = new Date(value.replace(' ', 'T'))
  if (Number.isNaN(date.getTime())) return ''

  return date.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  })
}

onMounted(loadNotifications)
</script>
