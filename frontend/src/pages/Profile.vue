<template>
    <div v-if="caregiver">
        <nav>
            <h1 class="text-gray-900 font-bold text-[32px]">
                Profile
            </h1>
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
        <Tabs
            v-model="state.index"
            :tabs="[
                {
                label: 'General',
                },
                {
                label: 'Earnings',
                },
                {
                label: 'Ratings',
                },
            ]"
        >
  <template #default="{ tab }">
    <div class="p-5">
        <div>
            <div v-if="state.index === 0">
                <div class="contactInfo">
                    <b>Contact Information</b>
                    <div>
                        <Badge 
                        :variant="'ghost'"
                        theme="gray">
                            <template #prefix>
                                <FeatherIcon class="w-4" name="phone" />
                            </template>
                        </Badge>
                        {{ caregiver.phone_number.slice(0, 3) }} {{ caregiver.phone_number.slice(4) }}
                    </div>
                    <div v-if="caregiver.email">
                        <Badge 
                        :variant="'ghost'"
                        theme="gray">
                            <template #prefix>
                                <FeatherIcon class="w-4" name="phone" />
                            </template>
                        </Badge>
                        {{ caregiver.email }}
                    </div>
                    <div v-else-if="caregiver.email === null">
                        <Badge 
                        :variant="'ghost'"
                        theme="gray">
                            <template #prefix>
                                <FeatherIcon class="w-4" name="mail" />
                            </template>
                        </Badge>
                        None 
                    </div>
                </div>
                <!-- TODO: MAKE ALL THE BELOW INFO DYNAMIC -->
                <div class="agencyDetails">
                    <b>Agency Info</b>
                    <div>
                        <Badge 
                        :variant="'ghost'"
                        theme="gray">
                            <template #prefix>
                                <FeatherIcon class="w-5" name="user" />
                            </template>
                        </Badge>

                    </div>
                    <div>
                        <Badge 
                        :variant="'ghost'"
                        theme="gray">
                            <template #prefix>
                                <FeatherIcon class="w-4" name="phone" />
                            </template>
                        </Badge>
                        <!-- {{ caregiver.phone_number.slice(0, 3) }} {{ caregiver.phone_number.slice(4) }} -->
                          User Number Here
                    </div>
                    <div>
                        <Badge 
                        :variant="'ghost'"
                        theme="gray">
                            <template #prefix>
                                <FeatherIcon class="w-4" name="map-pin" />
                            </template>
                        </Badge>
                        User Adress here
                    </div>
                </div>
                <div class="mySpecialities">
                    <b>My Specialities</b>
                    <div>
                        <span>
                            <Badge
                            :variant="'solid'"
                            size="sm"
                            label="Badge"
                            theme="orange"
                            >
                            Meal Preperation
                            </Badge>
                        </span>
                        
                        <span>
                            <Badge
                            :variant="'solid'"
                            size="sm"
                            label="Badge"
                            theme="orange"
                            >
                            Bathing
                            </Badge>
                        </span>
                    </div>

                </div>
            </div>
            <div v-else-if="state.index === 1">
            </div>
            <div v-else-if="state.index === 2">
            </div>
        </div>
    </div>
  </template>
</Tabs>
    </div>
</template>

<script setup>
import { Avatar, Tabs, FeatherIcon, Badge } from 'frappe-ui'
import { computed, reactive } from 'vue';
import { createDocumentResource } from 'frappe-ui';


const state = reactive({
    index: 0
})

let caregiverResource = createDocumentResource({
    doctype: 'Caregiver',
    name: 'Caregiver-0009',
    auto: true
})

const caregiver = computed(() => caregiverResource.doc)
// console.log(caregiverResource.agency)

// TODO: Dynamically fetch data (something like caregiverResource.agency)

let agencyResource = createDocumentResource({
    doctype: 'Agency',
    name: 'Agency-0008',
    auto: true
})

const agency = computed(() => agencyResource.doc)

// console.log(agencyResource.doc.agency_name)

</script>