<template>
  <nav class="flex mx-5 my-2 items-center justify-between">
    <div class="w-15 h-15 flex items-center">
      <Button :variant="'outline'" class="w-8 h-8 rounded-full">
        <FeatherIcon class="w-5 stroke-[#070707] stroke-2" name="arrow-left" />
      </Button>
    </div>
    <!-- <Badge class="flex-auto w-15" :variant="'ghost'" theme="gray">
    </Badge> -->
    <h1 class="text-2xl text-[#070707] font-medium justify-self-center">Profile</h1>
    <img class="w-15" src="/public/favicon.png" alt="" />
  </nav>
  <hr>
  <center class="my-3">
    <Avatar
      class="flex-auto"
      :shape="'circle'"
      :image="caregiver.passport_size_photo"
      label="EY"
      size="3xl"
    />
    <div class="text-xl text-[#070707] font-medium">
      {{ caregiver.full_name }}
    </div>
    <div>
      {{ caregiver.caregiver_type }}
    </div>
    <div>Member Since: {{ caregiver.creation.slice(0, 11) }}</div>
  </center>
</template>

<script setup>
import { computed } from 'vue'
import { Avatar, Badge, FeatherIcon } from 'frappe-ui'
import { createDocumentResource } from 'frappe-ui'

let caregiverResource = createDocumentResource({
  doctype: 'Caregiver',
  name: 'Caregiver-0009',
  auto: true,
  // onSuccess(data) {
  //     console.log(data.agency)
  //     const agency_data = data.agency
  // }
})
const caregiver = computed(() => {
  if (caregiverResource.doc) {
    return caregiverResource.doc
  }
})
</script>
