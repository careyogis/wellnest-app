<template>
  <div class="container-fluid min-vh-100" style="background: #f5f7fb">
    <div class="row min-vh-100">
      <!-- Left Side -->
      <div class="col-lg-6 d-none d-lg-flex bg-warning align-items-center justify-content-center p-5">
        <div class="text-white" style="max-width: 520px">
          <img src="@/assets/images/logo-01.png" style="width: 330px" class="mb-4" />

          <h1 class="fw-bold">CareYogi Doctor App</h1>

          <p class="mt-3">Stay connected with patients after discharge, manage consultations and follow-ups from one workspace.</p>

          <div class="mt-5">
            <span class="badge rounded-pill bg-light text-dark px-3 py-2 mb-4"> Continuity of Care Platform </span>

            <div class="mt-4">
              <div class="d-flex align-items-start mb-3">
                <i class="bi bi-shield-check fs-4 me-3"></i>
                <div>
                  <strong>Private doctor workspace</strong>
                  <div class="small opacity-75">Secure access for verified CareYogi clinicians.</div>
                </div>
              </div>

              <div class="d-flex align-items-center mb-3">
                <i class="bi bi-calendar-check fs-5 me-3"></i>
                <span> Receive bookings from patients based on your published availability. </span>
              </div>

              <div class="d-flex align-items-center mb-3">
                <i class="bi bi-file-earmark-medical fs-5 me-3"></i>
                <span> Review patient uploads and post-discharge follow-ups. </span>
              </div>

              <div class="d-flex align-items-center">
                <i class="bi bi-chat-dots fs-5 me-3"></i>
                <span> Continue care through asynchronous patient messaging. </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side -->

      <div class="col-lg-6 d-flex align-items-center justify-content-center">
        <Card class="shadow-lg border-0" style="max-width: 560px; width: 100%; border-radius: 20px">
          <div class="p-4">
            <div class="d-flex align-items-center mb-4">
              <div class="rounded-circle bg-warning text-dark fw-bold d-flex align-items-center justify-content-center" style="width: 60px; height: 60px; font-size: 20px">YB</div>

              <div class="ms-3">
                <div class="text-muted small">Welcome back</div>

                <h4 class="mb-0 fw-semibold">Brig. (Retd.) Dr. Y. S. Bisht</h4>
              </div>
            </div>

            <div class="btn-group w-100 mb-4">
              <button class="btn" :class="loginMethod == 'password' ? 'btn-primary' : 'btn-outline-primary'" @click="loginMethod = 'password'">Password</button>

              <button class="btn" :class="loginMethod == 'otp' ? 'btn-primary' : 'btn-outline-primary'" @click="loginMethod = 'otp'">OTP</button>
            </div>

            <!-- PASSWORD -->

            <form v-if="loginMethod == 'password'" @submit.prevent="submit">
              <Input class="doctor-input" name="email" label="Username" placeholder="Enter username" />

              <Input class="doctor-input mt-2" type="password" name="password" label="Password" placeholder="Password" />

              <Button class="w-100 mt-4 doctor-btn" variant="solid" type="submit"> Sign In </Button>
            </form>

            <!-- OTP -->

            <div v-else>
              <Input  class="doctor-input" v-model="phone" label="Mobile Number" placeholder="Enter Mobile Number" />

              <Button class="w-100 mt-3 doctor-btn" variant="solid" @click="sendOtp"> Send OTP </Button>

              <div v-if="otpSent">
                <Input class="mt-3" v-model="otp" label="OTP" placeholder="Enter OTP" />

                <Button class="w-100 mt-3 doctor-input" variant="solid" @click="verifyOtp"> Verify OTP </Button>
              </div>
            </div>

            <div id="recaptcha-container"></div>
            <div class="alert alert-info mt-4 mb-0">
              <i class="bi bi-shield-check me-2"></i>

              Prototype only. No backend or clinical data storage.
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { session } from '../data/session';
import { userResource } from '../data/user';
import { sessionUser } from '../data/session';
import { createResource } from 'frappe-ui';
import { auth } from '../firebase';
import router from '@/router'

import { RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';

const lookupDoctor = createResource({
  url: 'wellnest.api.lookup_doctor',
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
  url: 'wellnest.api.login_with_phone',
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
    const response = await lookupDoctor.submit();

    console.log(response);

    if (!response.success) {
      alert(response.message);
      return;
    }

    alert('Doctor found!');

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

    alert('OTP Verified Successfully!');

    router.replace({ name: "Profile" });
  } catch (err) {
    console.error(err);
    alert('Invalid OTP');
  }
}
</script>
