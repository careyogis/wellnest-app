<template>
    <div>
        <!-- Component: Outline accordion -->
        <section class="w-full bg-white border divide-y rounded divide-slate-200 border-slate-200">
        <details class="p-4 group" open>
            <summary class="[&::-webkit-details-marker]:hidden relative pr-8 font-medium list-none cursor-pointer text-slate-700 focus-visible:outline-none transition-colors duration-300 group-hover:text-slate-900 ">
                Blood Pressure
            <svg xmlns="http://www.w3.org/2000/svg" class="absolute right-0 w-4 h-4 transition duration-300 top-1 stroke-slate-700 shrink-0 group-open:rotate-45" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-labelledby="title-ac21 desc-ac21">
                <title id="title-ac21">Open icon</title>
                <desc id="desc-ac21">icon that represents the state of the summary</desc>
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            </summary>
            <p class="mt-4 text-slate-500">
                <div class="p-8">
                    <TextInput
                    :type="'text'"
                    size="sm"
                    variant="outline"
                    placeholder="120/65"
                    /> 
                    mm/hg
                </div>
                <div>
                    Notes: <br>
                    Lorem ipsum, dolor sit amet consectetur adipisicing elit. Voluptatum iste suscipit laudantium, odit sunt ipsa dolorem dolorum beatae voluptatem ratione in, neque ea culpa provident doloribus tempore a facere veritatis.
                </div>
                <div>

                </div>
                    <FileUploader
                    :fileTypes="['image/*']"
                    :validateFile="(fileObject) => {
                        }"
                    @success="(file) => {
                        }"
                    >
                        <template #default="{ file, uploading, progress, uploaded, message, error, total, success, openFileSelector }">
                            <Button
                            @click="openFileSelector"
                            :loading="uploading"
                            >
                                {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
                            </Button>
                        </template>
                    </FileUploader>
                    <Button
                    :variant="'outline'"
                    theme="gray"
                    size="lg"
                    label="Button"
                    >
                        Mark as Completed
                    </Button>
            </p>
        </details>
        </section>
        <!-- End Outlined accordion -->
         <div>

         </div>
    </div>
</template>

<script setup>
import { TextInput, FileUploader, Button } from 'frappe-ui';
import { createListResource } from 'frappe-ui'



</script>

