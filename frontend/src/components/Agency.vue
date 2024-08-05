<template>
    <div class="agencyDetails mb-7" v-if="agencyResource && !agencyResource.loading && agencyResource.data">
        <div class="text-xl text-[#070707] font-semibold mb-3">
            Agency Details
        </div>
        <div class="mb-3">
            <Badge :variant="'ghost'" theme="gray">
                <template #prefix>
                    <FeatherIcon class="w-5" name="user" />
                </template>
            </Badge>
            {{ agencyResource.data.agency_name }}
        </div>
        <div class="mb-3">
            <Badge :variant="'ghost'" theme="gray">
                <template #prefix>
                    <FeatherIcon class="w-4" name="phone" />
                </template>
            </Badge>
            {{ agencyResource.data.primary_phone.slice(0, 3) }}
            {{ agencyResource.data.primary_phone.slice(4) }}
        </div>
        <div>
            <Badge :variant="'ghost'" theme="gray">
                <template #prefix>
                    <FeatherIcon class="w-4" name="map-pin" />
                </template>
            </Badge>
            {{ agencyResource.data.complete_address }}
        </div>
    </div>

</template>

<script setup>
import { createResource, FeatherIcon, Badge } from 'frappe-ui';

const props = defineProps({
                agencyName: String
                })

let agencyResource;
if (props.agencyName) {
    agencyResource = createResource({
      url: '/api/method/frappe.client.get',
      params: {
        doctype: 'Agency',
        //fields: ['agency_name', 'primary_contact_full_name', 'primary_phone', 'email', 'complete_address', ],  
        name: props.agencyName,
      },
      auto: true,      
    })
}

</script>