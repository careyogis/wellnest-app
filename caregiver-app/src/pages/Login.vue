<template>
  <div class="m-3 flex flex-row items-center justify-center">
    <Card class="w-full max-w-md mt-4">
      <div class="flex flex-row justify-center">
        <img src="../../public/favicon.png" width="50" alt="" />
      </div>

      <div class="flex flex-row justify-center mt-4">
        <span class="font-bold text-lg">Welcome to CareYogi</span>
      </div>

      <div class="flex justify-center gap-2 my-4">
        <Button @click="loginMethod = 'password'" :variant="loginMethod === 'password' ? 'solid' : 'outline'"> User ID </Button>

        <Button @click="loginMethod = 'otp'" :variant="loginMethod === 'otp' ? 'solid' : 'outline'"> Mobile OTP </Button>
      </div>

      <!-- Existing Login -->
      <div v-if="loginMethod === 'password'">
        <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
          <Input required name="email" type="text" placeholder="johndoe@email.com" label="User ID" />

          <Input required name="password" type="password" placeholder="••••••" label="Password" />

          <Button :loading="session.login.loading" variant="solid"> Login </Button>
        </form>
      </div>

      <!-- Mobile OTP Login -->
      <div v-if="loginMethod === 'otp'" class="flex flex-col space-y-2">
        <Input v-model="phone" label="Mobile Number" placeholder="9876543210" />

        <Button variant="solid" v-if="!otpSent" @click="sendOtp"> Send OTP </Button>

        <template v-if="otpSent">
          <Input v-model="otp" label="OTP" placeholder="Enter OTP" />

          <Button variant="solid" @click="verifyOtp"> Verify OTP </Button>
        </template>
      </div>
      <div id="recaptcha-container"></div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { session } from '../data/session';
import { userResource } from "../data/user";
import { sessionUser } from "../data/session";
import { createResource } from 'frappe-ui';
import { auth } from '../firebase';
import router from "@/router";

import { RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';

const lookupCaregiver = createResource({
  url: 'wellnest.api.lookup_caregiver',
  makeParams() {
    return {
      phone: phone.value,
    };
  },
});

const loginMethod = ref('password');

const phone = ref('');
const otp = ref('');

const otpSent = ref(false);
const confirmationResult = ref<any>(null);
const recaptchaVerifier = ref<any>(null);

const loginWithPhone = createResource({
  url: "wellnest.api.login_with_phone",
  makeParams() {
    return {
      phone: phone.value,
    };
  },
});

function submit(e: Event) {
  const formData = new FormData(e.target as HTMLFormElement);

  session.login.submit({
    email: formData.get('email'),
    password: formData.get('password'),
  });
}

async function sendOtp() {
  if (!phone.value) {
    alert('Please enter your mobile number');
    return;
  }

  try {
    const response = await lookupCaregiver.submit();

    console.log(response);

    if (!response.success) {
      alert(response.message);
      return;
    }

    alert('User found!');

    // Next step: call Firebase to send OTP
    initializeRecaptcha();

    const appVerifier = recaptchaVerifier.value;

    const result = await signInWithPhoneNumber(auth, '+91' + phone.value, appVerifier);

    confirmationResult.value = result;

    otpSent.value = true;

    alert('OTP Sent!');

  } catch (err) {
    console.error(err);
    alert('Lookup failed');
  }
}

function initializeRecaptcha() {
  if (recaptchaVerifier.value) return;

  recaptchaVerifier.value = new RecaptchaVerifier(auth, 'recaptcha-container', {
    size: 'invisible',
  });

  recaptchaVerifier.value.render();
}

async function verifyOtp() {
  try {
    await confirmationResult.value.confirm(otp.value);

    const response = await loginWithPhone.submit();

    console.log(response);
    
    await userResource.reload();

    session.user = sessionUser();

    alert("OTP Verified Successfully!");

    router.replace("/");

  } catch (err) {
    console.error(err);
    alert("Invalid OTP");
  }
}
</script>
