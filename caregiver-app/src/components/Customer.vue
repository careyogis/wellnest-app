<template>
  <div
    class="customerDetails mb-7"
  >
  <!-- TODO: Static data for now, fetch from backend -->
    <div class="text-[#070707] font-semibold mb-3">Customer Details</div>
    <div class="mb-3 flex gap-2">
      <FeatherIcon class="w-5" name="user" />
      <div class="text-[14px]">
        Sankalp Srivastava
        <!-- {{ agencyResource.data[0].agency_name }} -->
      </div>
    </div>
    <div class="mb-3 flex gap-2">
      <FeatherIcon class="w-4" name="phone" />
      <div class="text-[14px]">
        +91 1234567890
        <!-- {{ agencyResource.data[0].primary_phone.slice(0, 3) }}
        {{ agencyResource.data[0].primary_phone.slice(4) }} -->
      </div>
    </div>
    <div class="flex gap-2">
      <FeatherIcon class="w-4 self-start mt-1" name="map-pin" />
      <div class="text-[14px]">
        My Home, Hyderabad - 500081
        <!-- {{ agencyResource.data[0].complete_address }} -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource, FeatherIcon, Badge } from 'frappe-ui'
// TODO: switch api call from agency to customer(Some issue with that doctype, filled as static for now)

// const props = defineProps({
//   agencyName: String,
// })

// let agencyResource
// if (props.agencyName) {
//   agencyResource = createResource({
//     url: 'frappe.client.get_list',
//     params: {
//       doctype: 'Agency',
//       fields: ['agency_name', 'primary_phone', 'complete_address'],
//       name: props.agencyName,
//     },
//     auto: true,
//   })
// }
</script>
