<template>
  <!-- Component: Outline accordion -->
  <section
    class="w-full bg-white border divide-y rounded divide-slate-200 border-slate-200"
  >
    <details class="p-3 group" open>
      <summary
        class="[&::-webkit-details-marker]:hidden flex justify-between items-center relative font-medium list-none cursor-pointer text-slate-700 focus-visible:outline-none transition-colors duration-300 group-hover:text-slate-900"
      >
        <div class="order-2 text-[#070707] font-semibold">Blood Pressure</div>
        <div class="order-3 flex justify-between items-center">
          <div>
            <FeatherIcon
              class="w-6 mr-1 stroke-[#78abaf] stroke-2"
              name="clock"
            />
          </div>
          <div class="text-[#070707] font-semibold">10 AM</div>
        </div>

        <!-- <Button
            :variant="'ghost'"
            class="transition duration-300 stroke-slate-700 group-open:rotate-90 w-8 h-8"
          >
            <FeatherIcon
              class="w-5 stroke-[#070707] stroke-2"
              name="chevron-right"
            />
          </Button> -->
        <FeatherIcon
          class="transition duration-300 stroke-slate-700 group-open:rotate-90 w-5 stroke-[#070707] stroke-2"
          name="chevron-right"
        />
      </summary>
      <div class="mt-4 px-7 text-slate-500">
        <div class="flex">
          <TextInput
            :type="'text'"
            size="lg"
            variant="outline"
            placeholder="120/65"
          />
          <div class="self-end">mm/hg</div>
        </div>
        <FeatherIcon
          class="inline-block w-3 -rotate-45 mr-1 stroke-[blue] stroke-1"
          name="paperclip"
        />
        <div class="inline-block my-5 text-blue-500">reading1.png</div>
        <div class="text-[#070707] font-semibold">Notes:</div>
        <div>
          Lorem ipsum, dolor sit amet consectetur adipisicing elit. Voluptatum
          iste suscipit laudantium, odit sunt ipsa dolorem dolorum beatae
          voluptatem ratione in, neque ea culpa provident doloribus tempore a
          facere veritatis.
        </div>
        <FileUploader
          class="mt-5"
          :fileTypes="['image/*']"
          :validateFile="validateFileFunction"
          @success="onSuccess"
        >
          <template
            #default="{
              file,
              uploading,
              progress,
              uploaded,
              message,
              error,
              total,
              success,
              openFileSelector,
            }"
          >
            <!-- <Button :variant="'outline'" theme="gray" size="lg" @click="openFileSelector" :loading="uploading">
                {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
              </Button> -->
            <button
              class="text-xl font-medium border-2 border-gray-500 rounded w-full py-2 mb-1"
              @click="openFileSelector"
              :loading="updloading"
            >
              {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
            </button>
          </template>
        </FileUploader>
        <div class="flex justify-between items-center">
          <button
            class="text-xl font-medium border-2 border-gray-500 rounded w-2/3 py-2 mb-2"
          >
            Mark as Completed
            <!-- TODO: Items are not centered properly -->
          </button>
          <div class="order-3 flex justify-between items-center">
              <FeatherIcon
                class="w-6 mr-1 stroke-[#78abaf] stroke-2"
                name="clock"
              />
            <div class="text-[#070707] font-semibold">10 AM</div>
          </div>
        </div>
        <!-- <Button :variant="'outline'" theme="gray" size="xl" label="Button">
          Mark as Completed
        </Button> -->
      </div>
    </details>
  </section>
  <!-- End Outlined accordion -->
</template>

<script setup>
import { TextInput, FileUploader, Button, FeatherIcon } from 'frappe-ui'
import { createListResource } from 'frappe-ui'

const validateFileFunction = (fileObject) => {}
const onSuccess = (file) => {
  console.log(file)
}
</script>
