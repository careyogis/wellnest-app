<template>
  <div class="m-5">
    <div class="my-5">
      <div class="inline-flex gap-1">
        <p class="font-bold text-[20px]">Login</p>
        <FeatherIcon class="w-5 stroke-2" name="user" />
      </div>
      <p>Welcome to CareYogi Caregiver App</p>
    </div>
    <img
      class="w-[125px] h-[125px] mx-auto mt-10 mb-5"
      src="/favicon.png"
      alt=""
    />
    <div
      class="w-[90%] mx-auto mr-5 ml-5 mt-10 flex rounded-sm shadow-sm"
      role="group"
    >
      <button
        type="button"
        class="w-full px-4 py-2 font-bold text-gray-900 border border-black focus:border-[#78ABAF] rounded-l-sm focus:z-10 focus:ring-2 focus:bg-[#78ABAF] focus:ring-[#78ABAF] focus:text-white"
        @click="stateChange(0)"
      >
        Username
      </button>
      <button
        type="button"
        class="w-full px-4 py-2 font-bold text-gray-900 border border-black focus:border-[#78ABAF] rounded-r-sm focus:z-10 focus:ring-2 focus:bg-[#78ABAF] focus:ring-[#78ABAF] focus:text-white"
        @click="stateChange(1)"
      >
        Phone Number
      </button>
    </div>
    <div v-if="state === 0">
      <div class="w-[95%] mx-auto my-10">
        <input
          class="w-full mb-3 rounded-sm outline outline-1 outline-gray-500"
          type="text"
          placeholder="Username"
        />
        <input
          class="w-full rounded-sm outline outline-1 outline-gray-500"
          type="password"
          placeholder="password"
        />
        <p class="text-right mr-2">
          <a href="#" class="text-right text-blue-600">Forgot Password?</a>
        </p>
      </div>
      <button
        class="w-full mx-auto px-4 py-2 text-white font-bold rounded-sm bg-[#E49A54]"
      >
        Login
      </button>
    </div>
    <div v-if="state === 1">
      <div class="w-[95%] mx-auto my-10">
        <input
          class="w-full rounded-sm outline outline-1 outline-gray-500"
          type="text"
          placeholder="Provide OTP"
        />
        <p class="text-right mr-2"></p>
      </div>
      <button
        class="w-full mx-auto px-4 py-2 text-white font-bold rounded-sm bg-[#E49A54]"
      >
        Login
      </button>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { ref } from 'vue'

let state = ref(0)

let stateChange = (num) => {
  state.value = num
}
</script>
