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
        {{ agencyAddress.doc.phone }}
      </div>
    </div>
    <div class="flex gap-2">
      <FeatherIcon class="w-4 self-start mt-1" name="map-pin" />
      <!-- <div v-html="agencyResource.data[0].primary_address"></div> -->
      <p>
        {{ agencyAddress.doc.address_line1 }} <br />
        {{ agencyAddress.doc.address_line2 }} <br />
        {{ agencyAddress.doc.city }} <br />
        {{ agencyAddress.doc.state }} <br />
        {{ agencyAddress.doc.country }} <br />
        {{ agencyAddress.doc.pincode }}
      </p>
    </div>
  </div>
</template>

<script setup>
import {
  createResource,
  createDocumentResource,
  FeatherIcon,
  Badge,
} from 'frappe-ui'

const props = defineProps({
  agencyName: String,
})

let agencyResource
let agencyAddress
if (props.agencyName) {
  apiCall()
}

async function apiCall() {
  agencyResource = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Supplier',
      fields: ['*'],
      name: props.agencyName,
    },
    auto: true,
  })
  await agencyResource.promise

  agencyAddress = createDocumentResource({
    doctype: 'Address',
    name: agencyResource.data[0].supplier_primary_address,
    auto: true,
  })
}
</script>
