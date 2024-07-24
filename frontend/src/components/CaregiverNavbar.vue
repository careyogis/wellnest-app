<template>
    <div>
        <nav>
            <Avatar
                :shape="'circle'"
                :image= "caregiver.passport_size_photo"
                label="EY"
                size="3xl"
            />
            <div>
                {{ caregiver.full_name }}
            </div>
            <div>
                {{ caregiver.caregiver_type }}
            </div>
            <div>
                Member Since: {{ caregiver.creation.slice(0,11) }}
            </div>
        </nav>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { Avatar } from 'frappe-ui';
import { createDocumentResource } from 'frappe-ui';

let caregiverResource = createDocumentResource({
    doctype: 'Caregiver',
    name: 'Caregiver-0009',
    auto: true,
    // onSuccess(data) {
    //     console.log(data.agency)
    //     const agency_data = data.agency
    // }
})
const caregiver = computed(() => {if (caregiverResource.doc) {
    return caregiverResource.doc
}
})

</script>
