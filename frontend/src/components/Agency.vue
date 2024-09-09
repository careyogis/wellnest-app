<template>
  <div
    class="agencyDetails mb-7"
    v-if="agencyResource && !agencyResource.loading && agencyResource.data[0]"
  >
    <div class="text-xl text-[#070707] font-semibold mb-3">Agency Details</div>
    <div class="mb-3 flex gap-2">
      <FeatherIcon class="w-5" name="user" />
      <div>
        {{ agencyResource.data[0].supplier_name }}
      </div>
    </div>
    <div class="mb-3 flex gap-2">
      <FeatherIcon class="w-4" name="phone" />
      <div>
        {{ agencyResource.data[0].mobile_no }}
      </div>
    </div>
    <div class="flex gap-2">
      <FeatherIcon class="w-4 self-start mt-1" name="map-pin" />
      <div v-html="agencyResource.data[0].primary_address"></div>
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
      doctype: 'Supplier',
      fields: [
        'supplier_name',
        'supplier_primary_contact',
        'primary_address',
        'mobile_no',
        'email_id',
      ],
      name: props.agencyName,
    },
    auto: true,
  })
}
</script>
