<template>
  <div
    class="agencyDetails mb-7"
    v-if="agencyResource && !agencyResource.loading && agencyResource.data[0]"
  >
    <div class="text-xl text-[#070707] font-semibold mb-3">Agency Details</div>
    <div class="mb-3 flex gap-2">
      <FeatherIcon class="w-5" name="user" />
      <div>
        {{ agencyResource.data[0].agency_name }}
      </div>
    </div>
    <div class="mb-3 flex gap-2">
      <FeatherIcon class="w-4" name="phone" />
      <div>
        {{ agencyResource.data[0].primary_phone.slice(0, 3) }}
        {{ agencyResource.data[0].primary_phone.slice(4) }}
      </div>
    </div>
    <div class="flex gap-2">
      <FeatherIcon class="w-4 self-start mt-1" name="map-pin" />
      <div>
        {{ agencyResource.data[0].complete_address }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource, FeatherIcon, Badge } from 'frappe-ui'

const props = defineProps({
  agencyName: String,
})

let agencyResource
if (props.agencyName) {
  agencyResource = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Agency',
      fields: ['agency_name', 'primary_phone', 'complete_address'],
      name: props.agencyName,
    },
    auto: true,
  })
}
</script>
