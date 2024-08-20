<template>
  <nav class="flex mx-5 my-2 items-center justify-between">
    <div class="w-15 h-15 flex items-center">
      <button @click="$router.go(-1)" class="w-8 h-8 outline outline-[#EDEDED] outline-1 rounded-full flex justify-center items-center">
        <FeatherIcon class="w-5  stroke-[#070707] stroke-2" name="arrow-left" />
      </button>
    </div>
    <h1 class="text-2xl text-[#070707] font-semibold justify-self-center">{{ title }}</h1>
    <img class="w-15" src="/favicon.png" alt="" />
  </nav>
  <hr>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
defineProps(['title'])

</script>
