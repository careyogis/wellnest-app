<template>
    <div>
        <nav>
            <Avatar
                :shape="'circle'"
                :image= "beneficiary.photo"
                label="EY"
                size="3xl"
            />
            <div>
                {{ beneficiary.full_name }}
            </div>
            <div>
                {{ beneficiary.gender }} {{ beneficiary.age }}
            </div>
        </nav>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { Avatar } from 'frappe-ui';
import { createDocumentResource } from 'frappe-ui';

let beneficiaryResource = createDocumentResource({
    doctype: 'Beneficiary',
    name: 'BENF-000017',
    auto: true,
    // onSuccess(data) {
    //     console.log(data.agency)
    //     const agency_data = data.agency
    // }
})
const beneficiary = computed(() => {if (beneficiaryResource.doc) {
    return beneficiaryResource.doc
}
})

</script>
