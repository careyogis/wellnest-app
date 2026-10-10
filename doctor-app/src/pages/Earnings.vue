<template>
  <div class="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Earnings & Payouts</h1>
        <p class="text-sm md:text-base text-gray-500 mt-1">
          Review your accrued teleconsultation revenue, weekly settlement batches, and payout history.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="refreshData"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 bg-white text-sm font-semibold text-gray-700 hover:bg-gray-50 transition shadow-sm cursor-pointer"
        >
          <FeatherIcon name="refresh-cw" class="w-4 h-4" :class="{ 'animate-spin': isRefreshing }" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Payout Cadence Banner -->
    <div class="mb-6 flex items-center gap-3 p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-amber-900 text-sm">
      <div class="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center shrink-0 text-amber-700">
        <FeatherIcon name="info" class="w-4 h-4" />
      </div>
      <div class="flex-1">
        <span class="font-semibold">Weekly Settlement Schedule:</span>
        Payout batches are generated automatically every Monday for all completed teleconsultations from the preceding week.
      </div>
    </div>

    <!-- KPI Metric Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <!-- 1. Accrued (Unbilled) Earnings -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider text-gray-500">Accrued Earnings</span>
          <div class="w-9 h-9 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600">
            <FeatherIcon name="clock" class="w-4 h-4" />
          </div>
        </div>
        <div class="text-2xl md:text-3xl font-bold text-gray-900 mb-1">
          {{ formatCurrency(summary.accrued_amount) }}
        </div>
        <div class="text-xs text-amber-700 font-medium flex items-center gap-1">
          <span>{{ summary.accrued_count || 0 }} completed consultation{{ summary.accrued_count === 1 ? '' : 's' }}</span>
          <span>pending cycle</span>
        </div>
      </div>

      <!-- 2. Last Payout -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider text-gray-500">Last Payout</span>
          <div class="w-9 h-9 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
            <FeatherIcon name="check-circle" class="w-4 h-4" />
          </div>
        </div>
        <div class="text-2xl md:text-3xl font-bold text-gray-900 mb-1">
          {{ formatCurrency(summary.last_payout?.net_payable_amount || 0) }}
        </div>
        <div class="text-xs text-gray-500 truncate">
          <template v-if="summary.last_payout">
            <span>Disbursed {{ formatDate(summary.last_payout.payout_date) }}</span>
            <span v-if="summary.last_payout.payment_reference" class="block text-emerald-700 font-mono text-[11px] truncate">
              Ref: {{ summary.last_payout.payment_reference }}
            </span>
          </template>
          <template v-else>
            No disbursements yet
          </template>
        </div>
      </div>

      <!-- 3. Lifetime Earnings -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider text-gray-500">Lifetime Paid</span>
          <div class="w-9 h-9 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
            <FeatherIcon name="trending-up" class="w-4 h-4" />
          </div>
        </div>
        <div class="text-2xl md:text-3xl font-bold text-gray-900 mb-1">
          {{ formatCurrency(summary.lifetime_earnings) }}
        </div>
        <div class="text-xs text-gray-500">
          Across {{ summary.lifetime_consultations || 0 }} total consultations
        </div>
      </div>

      <!-- 4. Linked Bank Account -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold uppercase tracking-wider text-gray-500">Payout Account</span>
            <div class="w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
              <FeatherIcon name="credit-card" class="w-4 h-4" />
            </div>
          </div>

          <div v-if="summary.bank_account" class="space-y-0.5">
            <div class="text-sm font-bold text-gray-900 truncate">
              {{ summary.bank_account.bank_name }}
            </div>
            <div class="text-xs font-mono text-gray-600">
              {{ summary.bank_account.account_number_masked }}
            </div>
            <div v-if="summary.bank_account.ifsc" class="text-[11px] text-gray-400 font-mono">
              IFSC: {{ summary.bank_account.ifsc }}
            </div>
          </div>

          <div v-else class="text-xs text-gray-500 space-y-1">
            <div class="font-medium text-amber-700">Account setup pending</div>
            <div class="text-[11px] text-gray-400">
              Managed by CY Operations
            </div>
          </div>
        </div>

        <div class="pt-2 mt-2 border-t border-gray-100 flex items-center justify-between text-[11px]">
          <span class="text-gray-400">Contract Rate:</span>
          <span class="font-semibold text-gray-900">{{ formatCurrency(summary.practitioner?.online_charge) }}/consult</span>
        </div>
      </div>
    </div>

    <!-- Tabs Container -->
    <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
      <div class="flex items-center border-b border-gray-200 px-6 pt-4 gap-6">
        <button
          type="button"
          @click="activeTab = 'history'"
          class="pb-3 text-sm font-semibold border-b-2 transition-colors cursor-pointer flex items-center gap-2"
          :class="activeTab === 'history' ? 'border-amber-500 text-amber-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          <FeatherIcon name="file-text" class="w-4 h-4" />
          Payout Statements
          <span
            v-if="payoutHistory.length"
            class="px-2 py-0.5 rounded-full text-xs"
            :class="activeTab === 'history' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'"
          >
            {{ payoutHistory.length }}
          </span>
        </button>

        <button
          type="button"
          @click="activeTab = 'unbilled'"
          class="pb-3 text-sm font-semibold border-b-2 transition-colors cursor-pointer flex items-center gap-2"
          :class="activeTab === 'unbilled' ? 'border-amber-500 text-amber-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          <FeatherIcon name="list" class="w-4 h-4" />
          Unbilled Consultations
          <span
            v-if="unbilledList.length"
            class="px-2 py-0.5 rounded-full text-xs"
            :class="activeTab === 'unbilled' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'"
          >
            {{ unbilledList.length }}
          </span>
        </button>
      </div>

      <!-- Tab Content 1: Payout Statements -->
      <div v-if="activeTab === 'history'" class="p-6">
        <div v-if="loadingHistory" class="py-12 text-center text-gray-400 text-sm">
          <FeatherIcon name="loader" class="w-6 h-6 animate-spin mx-auto mb-2 text-amber-500" />
          Loading payout statements...
        </div>

        <div v-else-if="!payoutHistory.length" class="py-16 text-center">
          <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 mx-auto mb-3">
            <FeatherIcon name="inbox" class="w-6 h-6" />
          </div>
          <div class="text-sm font-semibold text-gray-900">No payout statements yet</div>
          <p class="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
            Once a weekly payout cycle is generated by CY Operations, your itemized statements will appear here.
          </p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="payout in payoutHistory"
            :key="payout.name"
            class="border border-gray-200 rounded-xl p-5 hover:border-gray-300 transition bg-white"
          >
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <!-- Left: Cycle & Batch ID -->
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="font-bold text-gray-900 text-base">
                    {{ formatDateRange(payout.cycle_start_date, payout.cycle_end_date) }}
                  </span>
                  <span
                    class="px-2.5 py-0.5 rounded-full text-xs font-semibold"
                    :class="getStatusBadgeClass(payout.status)"
                  >
                    {{ payout.status }}
                  </span>
                </div>

                <div class="text-xs text-gray-500 flex flex-wrap items-center gap-x-3 gap-y-1">
                  <span class="font-mono text-gray-600">{{ payout.name }}</span>
                  <span>•</span>
                  <span>{{ payout.consultation_count }} consultation{{ payout.consultation_count === 1 ? '' : 's' }}</span>
                  <template v-if="payout.payout_date">
                    <span>•</span>
                    <span>Disbursed: {{ formatDate(payout.payout_date) }}</span>
                  </template>
                  <template v-if="payout.payment_reference">
                    <span>•</span>
                    <span class="font-mono text-emerald-700 font-medium">Ref: {{ payout.payment_reference }}</span>
                  </template>
                </div>
              </div>

              <!-- Right: Amounts & Actions -->
              <div class="flex flex-wrap items-center justify-between lg:justify-end gap-4 pt-3 lg:pt-0 border-t lg:border-t-0 border-gray-100">
                <div class="text-left lg:text-right">
                  <div class="text-xs text-gray-400">Net Disbursed</div>
                  <div class="text-xl font-bold text-gray-900">
                    {{ formatCurrency(payout.net_payable_amount) }}
                  </div>
                  <div v-if="payout.adjustments > 0" class="text-[11px] text-red-600">
                    Gross: {{ formatCurrency(payout.gross_amount) }} (Adj: -{{ formatCurrency(payout.adjustments) }})
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    @click="viewPayoutDetails(payout.name)"
                    class="px-3 py-2 rounded-lg border border-gray-200 text-gray-700 text-xs font-semibold hover:bg-gray-50 transition cursor-pointer flex items-center gap-1.5"
                  >
                    <FeatherIcon name="eye" class="w-3.5 h-3.5 text-gray-500" />
                    Details
                  </button>

                  <a
                    :href="`/api/method/wellnest.api.earnings.download_payout_statement?payout_name=${payout.name}`"
                    target="_blank"
                    class="px-3 py-2 rounded-lg bg-amber-500 text-white text-xs font-semibold hover:bg-amber-600 transition cursor-pointer flex items-center gap-1.5"
                  >
                    <FeatherIcon name="download" class="w-3.5 h-3.5" />
                    Statement PDF
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content 2: Unbilled Consultations -->
      <div v-if="activeTab === 'unbilled'" class="p-6">
        <div v-if="loadingUnbilled" class="py-12 text-center text-gray-400 text-sm">
          <FeatherIcon name="loader" class="w-6 h-6 animate-spin mx-auto mb-2 text-amber-500" />
          Loading unbilled consultations...
        </div>

        <div v-else-if="!unbilledList.length" class="py-16 text-center">
          <div class="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-500 mx-auto mb-3">
            <FeatherIcon name="check" class="w-6 h-6" />
          </div>
          <div class="text-sm font-semibold text-gray-900">All completed consultations are billed!</div>
          <p class="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
            New completed teleconsultations will automatically accrue here until the next Monday cycle runs.
          </p>
        </div>

        <div v-else>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-50/50">
                  <th class="py-3 px-4">Appointment</th>
                  <th class="py-3 px-4">Date & Time</th>
                  <th class="py-3 px-4">Patient</th>
                  <th class="py-3 px-4 text-right">Customer Fee</th>
                  <th class="py-3 px-4 text-right">Your Share</th>
                  <th class="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 text-sm">
                <tr v-for="appt in unbilledList" :key="appt.name" class="hover:bg-gray-50/70 transition">
                  <td class="py-3.5 px-4 font-mono font-medium text-gray-900 text-xs">
                    {{ appt.name }}
                  </td>
                  <td class="py-3.5 px-4 text-gray-600 text-xs">
                    {{ formatDateTime(appt.scheduled_time) }}
                  </td>
                  <td class="py-3.5 px-4 text-gray-900 font-medium">
                    {{ appt.patient_name || appt.patient }}
                  </td>
                  <td class="py-3.5 px-4 text-right text-gray-500 text-xs">
                    {{ formatCurrency(appt.consultation_fee) }}
                  </td>
                  <td class="py-3.5 px-4 text-right font-bold text-gray-900">
                    {{ formatCurrency(appt.practitioner_payout_rate) }}
                  </td>
                  <td class="py-3.5 px-4 text-center">
                    <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                      Accrued
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mt-4 p-4 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between text-xs text-gray-500">
            <span>Total unbilled appointments: <strong>{{ unbilledList.length }}</strong></span>
            <span>Total accrued amount: <strong class="text-gray-900 text-sm">{{ formatCurrency(summary.accrued_amount) }}</strong></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Payout Detail Modal -->
    <div
      v-if="selectedPayoutModal"
      class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
      @click.self="selectedPayoutModal = null"
    >
      <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50/50">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Payout Batch Details</h3>
            <div class="text-xs text-gray-500 font-mono mt-0.5">{{ selectedPayoutModal.name }}</div>
          </div>
          <button
            type="button"
            @click="selectedPayoutModal = null"
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
          >
            <FeatherIcon name="x" class="w-5 h-5" />
          </button>
        </div>

        <!-- Modal Body -->
        <div class="p-6 overflow-y-auto space-y-5">
          <!-- Summary grid -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-gray-50 border border-gray-200 text-xs">
            <div>
              <div class="text-gray-400">Cycle Period</div>
              <div class="font-semibold text-gray-900 mt-0.5">
                {{ formatDate(selectedPayoutModal.cycle_start_date) }} - {{ formatDate(selectedPayoutModal.cycle_end_date) }}
              </div>
            </div>
            <div>
              <div class="text-gray-400">Status</div>
              <div class="font-semibold mt-0.5" :class="getStatusTextColor(selectedPayoutModal.status)">
                {{ selectedPayoutModal.status }}
              </div>
            </div>
            <div>
              <div class="text-gray-400">Consultations</div>
              <div class="font-semibold text-gray-900 mt-0.5">
                {{ selectedPayoutModal.consultation_count }}
              </div>
            </div>
            <div>
              <div class="text-gray-400">Net Disbursed</div>
              <div class="font-bold text-gray-900 text-sm mt-0.5">
                {{ formatCurrency(selectedPayoutModal.net_payable_amount) }}
              </div>
            </div>
          </div>

          <!-- Line items -->
          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
              Included Consultations
            </h4>
            <div class="border border-gray-200 rounded-xl overflow-hidden max-h-60 overflow-y-auto">
              <table class="w-full text-left text-xs border-collapse">
                <thead class="bg-gray-50 border-b border-gray-200 text-gray-500">
                  <tr>
                    <th class="py-2.5 px-3">#</th>
                    <th class="py-2.5 px-3">Appointment</th>
                    <th class="py-2.5 px-3">Patient</th>
                    <th class="py-2.5 px-3 text-right">Doctor Share</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="(it, idx) in selectedPayoutModal.items" :key="it.name" class="hover:bg-gray-50">
                    <td class="py-2.5 px-3 text-gray-400">{{ idx + 1 }}</td>
                    <td class="py-2.5 px-3 font-mono font-medium text-gray-900">{{ it.patient_appointment }}</td>
                    <td class="py-2.5 px-3 text-gray-700">{{ it.patient_name }}</td>
                    <td class="py-2.5 px-3 text-right font-bold text-gray-900">{{ formatCurrency(it.payout_rate) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Adjustments if any -->
          <div v-if="selectedPayoutModal.adjustments > 0" class="p-3 rounded-lg bg-red-50 border border-red-100 text-xs">
            <div class="font-semibold text-red-900">
              Deductions / Adjustments: -{{ formatCurrency(selectedPayoutModal.adjustments) }}
            </div>
            <div v-if="selectedPayoutModal.adjustment_reason" class="text-red-700 mt-1">
              Reason: {{ selectedPayoutModal.adjustment_reason }}
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-end gap-3">
          <button
            type="button"
            @click="selectedPayoutModal = null"
            class="px-4 py-2 rounded-lg border border-gray-200 text-xs font-semibold text-gray-700 hover:bg-gray-100 transition"
          >
            Close
          </button>
          <a
            :href="`/api/method/wellnest.api.earnings.download_payout_statement?payout_name=${selectedPayoutModal.name}`"
            target="_blank"
            class="px-4 py-2 rounded-lg bg-amber-500 text-white text-xs font-semibold hover:bg-amber-600 transition flex items-center gap-1.5"
          >
            <FeatherIcon name="download" class="w-3.5 h-3.5" />
            Download Statement
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';

const activeTab = ref('history');
const isRefreshing = ref(false);
const selectedPayoutModal = ref(null);

const summary = ref({
  accrued_amount: 0,
  accrued_count: 0,
  last_payout: null,
  lifetime_earnings: 0,
  lifetime_consultations: 0,
  bank_account: null,
  practitioner: null,
});

const payoutHistory = ref([]);
const unbilledList = ref([]);
const loadingHistory = ref(false);
const loadingUnbilled = ref(false);

const summaryResource = createResource({
  url: 'wellnest.api.earnings.get_doctor_earnings_summary',
  onSuccess(data) {
    if (data) {
      summary.value = data;
    }
  },
});

const historyResource = createResource({
  url: 'wellnest.api.earnings.get_doctor_payout_history',
  onSuccess(data) {
    if (data && data.payouts) {
      payoutHistory.value = data.payouts;
    }
  },
});

const unbilledResource = createResource({
  url: 'wellnest.api.earnings.get_doctor_unbilled_consultations',
  onSuccess(data) {
    if (data) {
      unbilledList.value = data;
    }
  },
});

const detailsResource = createResource({
  url: 'wellnest.api.earnings.get_payout_details',
  onSuccess(data) {
    if (data) {
      selectedPayoutModal.value = data;
    }
  },
});

async function refreshData() {
  isRefreshing.value = true;
  loadingHistory.value = true;
  loadingUnbilled.value = true;

  try {
    await Promise.all([
      summaryResource.fetch(),
      historyResource.fetch(),
      unbilledResource.fetch(),
    ]);
  } finally {
    isRefreshing.value = false;
    loadingHistory.value = false;
    loadingUnbilled.value = false;
  }
}

async function viewPayoutDetails(payoutName) {
  await detailsResource.fetch({ payout_name: payoutName });
}

function formatCurrency(amount) {
  const num = Number(amount) || 0;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(num);
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return '';
  const d = new Date(dateTimeStr);
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDateRange(startDate, endDate) {
  if (!startDate || !endDate) return '';
  return `${formatDate(startDate)} – ${formatDate(endDate)}`;
}

function getStatusBadgeClass(status) {
  switch (status) {
    case 'Paid':
      return 'bg-emerald-100 text-emerald-800 border border-emerald-200';
    case 'Approved':
      return 'bg-blue-100 text-blue-800 border border-blue-200';
    case 'Draft':
      return 'bg-amber-100 text-amber-800 border border-amber-200';
    case 'Cancelled':
      return 'bg-red-100 text-red-800 border border-red-200';
    default:
      return 'bg-gray-100 text-gray-700 border border-gray-200';
  }
}

function getStatusTextColor(status) {
  switch (status) {
    case 'Paid':
      return 'text-emerald-600';
    case 'Approved':
      return 'text-blue-600';
    case 'Draft':
      return 'text-amber-600';
    case 'Cancelled':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
}

onMounted(() => {
  refreshData();
});
</script>
