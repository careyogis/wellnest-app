<template>
  <!-- TODO: MAKE THIS AS A SETTLEMENT COMPONENT => FETCH FROM PAYMENT ENTRY DOCTYPE -->
  <div class="block max-w py-5 px-6 border border-gray-400 rounded-lg">
    <p class="text-xl text-[#070707] font-semibold mb-1">Total Earnings</p>
    <p class="text-[36px] text-[#070707] font-semibold mb-2">
      {{ formatCurrency(165000, 'INR') }}
    </p>
    <div class="grid grid-cols-2 grid-rows-2">
      <div>Next Settlement</div>
      <div class="flex gap-2">
        <FeatherIcon class="w-4 stroke-[#78abaf] stroke-2" name="calendar" />
        <div class="font-semibold text-[#78abaf]">15 July 2024</div>
      </div>
      <div>Amount</div>
      <div class="flex gap-2">
        <div class="font-semibold text-[#78abaf] ml-1">
          {{ formatCurrency(0, 'INR').slice(0, 1) }}
        </div>
        <div class="font-semibold text-[#78abaf] ml-0.5">
          {{ formatCurrency(65000, 'INR').slice(1) }}
        </div>
      </div>
    </div>
    <button class="bg-[#DB7706] text-white rounded-sm w-full mr-5 mt-15">
      <div class="flex justify-center gap-1">
        <FeatherIcon
          class="w-4 mr-1 stroke-[#ffffff] stroke-2"
          name="rotate-ccw"
        />
        Settlement History
      </div>
    </button>
  </div>
</template>

<script setup>
import { formatCurrency } from '../utils';
import { FeatherIcon } from 'frappe-ui';
</script>
