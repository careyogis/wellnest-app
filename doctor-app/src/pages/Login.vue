<template>
  <div class="w-full min-h-screen p-0 bg-[#f5f7fb]">
    <div class="flex flex-col lg:flex-row min-h-screen">
      <!-- Left Side -->
      <div class="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12 bg-gradient-to-br from-[#fff8f0] via-[#fdeee0] to-[#fbe6d3]">
        <div class="text-gray-900 py-4 max-w-[520px] w-full">
          <img src="@/assets/images/logo-01.png" class="w-[220px] mb-4" />

          <span class="inline-flex items-center rounded-full bg-white text-gray-900 px-3 py-1.5 mb-3 text-sm font-medium shadow-sm border border-orange-100"> Continuity of Care Platform </span>

          <h1 class="text-3xl lg:text-4xl font-bold text-gray-900">CareYogi Doctor App</h1>

          <p class="mt-3 text-gray-500 leading-relaxed">Stay connected with patients after discharge, review reports, manage follow-ups, and run consultations from one calm workspace.</p>

          <div class="bg-white rounded-2xl shadow-sm mt-4 p-4 space-y-1">
            <div class="flex items-start py-2 border-b border-gray-200">
              <FeatherIcon name="shield" class="w-6 h-6 mr-3 shrink-0 text-[#f5a623]" />
              <div>
                <strong class="text-gray-900 font-semibold">Private doctor workspace</strong>
                <div class="text-sm text-gray-500">Secure access for verified CareYogi clinicians.</div>
              </div>
            </div>

            <div class="flex items-center py-2 border-b border-gray-200">
              <FeatherIcon name="calendar" class="w-5 h-5 mr-3 shrink-0 text-[#f5a623]" />
              <span class="text-gray-700">Receive bookings from patients based on your published availability.</span>
            </div>

            <div class="flex items-center py-2 border-b border-gray-200">
              <FeatherIcon name="file-text" class="w-5 h-5 mr-3 shrink-0 text-[#f5a623]" />
              <span class="text-gray-700">Review patient uploads and post-discharge follow-ups.</span>
            </div>

            <div class="flex items-center pt-2">
              <FeatherIcon name="message-square" class="w-5 h-5 mr-3 shrink-0 text-[#f5a623]" />
              <span class="text-gray-700">Continue care through asynchronous patient messaging.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side -->
      <div class="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12">
        <Card class="shadow-lg border-0 max-w-[460px] w-full rounded-2xl">
          <div class="p-6">
            <div class="flex items-center justify-center mb-6">
              <img src="@/assets/images/logo-01.png" class="w-[160px]" />
            </div>

            <div class="flex p-1 rounded-full mb-6 bg-[#eef1f7]">
              <button
                class="flex-1 py-2 px-4 border-0 rounded-full transition-colors duration-150 font-semibold text-sm"
                :class="loginMethod == 'password' ? 'bg-white shadow-sm text-[#f5a623]' : 'bg-transparent text-gray-500 hover:text-gray-700'"
                @click="loginMethod = 'password'"
              >
                Password
              </button>

              <button
                class="flex-1 py-2 px-4 border-0 rounded-full transition-colors duration-150 font-semibold text-sm"
                :class="loginMethod == 'otp' ? 'bg-white shadow-sm text-[#f5a623]' : 'bg-transparent text-gray-500 hover:text-gray-700'"
                @click="loginMethod = 'otp'"
              >
                OTP
              </button>
            </div>

            <!-- PASSWORD -->
            <form v-if="loginMethod == 'password'" @submit.prevent="submit">
              <Input class="doctor-input" name="email" label="Username" placeholder="Enter username" />

              <Input class="doctor-input mt-3" type="password" name="password" label="Password" placeholder="Password" />

              <div
                v-if="message && loginMethod == 'password'"
                :class="['p-3 rounded-lg mt-3 text-sm border', messageType === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200']"
              >
                {{ message }}
              </div>

              <Button class="w-full mt-6 doctor-btn" variant="solid" type="submit"> Sign In </Button>

              <div class="text-center mt-6">
                <span class="text-sm text-gray-500"> New here? </span>

                <button type="button" class="ml-1 text-sm font-medium text-blue-600 hover:underline" @click="goToRegister()">Register</button>
              </div>
            </form>

            <!-- OTP -->
            <div v-else>
              <Input class="doctor-input" v-model="phone" label="Mobile Number" placeholder="Enter Mobile Number" />

              <Button class="w-full mt-4 doctor-btn" variant="solid" :disabled="otpSending" @click="sendOtp">
                {{ otpSending ? `Resend OTP in ${otpCooldown}s` : 'Send OTP' }}
              </Button>

              <div v-if="message" :class="['p-3 rounded-lg mt-3 text-sm border', messageType === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200']">
                {{ message }}
              </div>

              <div v-if="showRegisterOption" class="text-center mt-6">
                <span class="text-sm text-gray-500"> New here? </span>
                <button type="button" class="ml-1 text-sm font-medium text-blue-600 hover:underline" @click="goToRegister(phone)">Register</button>
              </div>
              <div v-if="otpSent">
                <Input class="mt-4 doctor-input" v-model="otpEntry" label="OTP" placeholder="Enter OTP" @input="val => otpEntry = val" />
                <Button class="w-full mt-4 doctor-btn" variant="solid" @click="verifyOtp" :disabled="verifyingOtp.value"> {{ verifyingOtp.value ? 'Verifying OTP...' : 'Verify OTP' }} </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
  <div id="recaptcha-container"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { session } from '../data/session';
import { userResource } from '../data/user';
import { sessionUser } from '../data/session';
import { createResource, FeatherIcon } from 'frappe-ui';
import router from '../router';

declare const grecaptcha: any;

//Public site key from https://www.google.com/recaptcha/admin - safe to expose in frontend acc. to documentation
const RECAPTCHA_SITE_KEY = '6LcMZR0UAAAAALgPMcgHwga7gY5p8QMg1Hj-bmUv';

const loginMethod = ref('password');

const phone = ref('');
const otpEntry = ref('');
const otpSent = ref(false);
const sessionInfo = ref('');
const message = ref('');
const messageType = ref<'success' | 'error' | ''>('');
const showRegisterOption = ref(true);
let recaptchaWidgetId: number | null = null;

// OTP resend cooldown state
const otpSending = ref(false);
const otpCooldown = ref(0);
const verifyingOtp = ref(false);
const OTP_COOLDOWN_SECONDS = 30;
let cooldownTimer: ReturnType<typeof setInterval> | null = null;

// OTP length expected from backend
const OTP_LENGTH = 6;

const sendOtpResource = createResource({ url: 'wellnest.api.auth.send_otp' });
const verifyOtpResource = createResource({ url: 'wellnest.api.auth.verify_otp_and_login' });

async function submit(e: Event) {
  message.value = '';
  messageType.value = '';

  const formData = new FormData(e.target as HTMLFormElement);
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  if (!email || !password) {
    message.value = 'Please enter both username and password.';
    messageType.value = 'error';
    return;
  }

  try {
    await session.login.submit({
      email,
      password,
    });
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err?.messages && err.messages.length > 0) {
      message.value = err.messages[0];
    } else {
      message.value = 'Invalid username or password.';
    }
  }
}

onMounted(() => {
  if (!document.getElementById('recaptcha-script')) {
    const script = document.createElement('script');
    script.id = 'recaptcha-script';
    script.src = 'https://www.google.com/recaptcha/api.js?render=explicit';
    script.async = true;
    document.head.appendChild(script);
  }
});

onBeforeUnmount(() => {
  if (cooldownTimer) clearInterval(cooldownTimer);
});

function renderRecaptcha(): Promise<number> {
  return new Promise((resolve) => {
    const check = setInterval(() => {
      if (typeof grecaptcha !== 'undefined' && grecaptcha.render) {
        clearInterval(check);
        const id = grecaptcha.render('recaptcha-container', {
          sitekey: RECAPTCHA_SITE_KEY,
          size: 'invisible',
        });
        resolve(id);
      }
    }, 100);
  });
}

async function getRecaptchaToken(): Promise<string> {
  if (recaptchaWidgetId === null) {
    recaptchaWidgetId = await renderRecaptcha();
  } else {
    grecaptcha.reset(recaptchaWidgetId);
  }
  return new Promise((resolve, reject) => {
    grecaptcha
      .execute(recaptchaWidgetId!)
      .then(() => {
        const token = grecaptcha.getResponse(recaptchaWidgetId!);
        if (token) resolve(token);
        else reject(new Error('No reCAPTCHA token received'));
      })
      .catch(reject);
  });
}

function startOtpCooldown() {
  otpSending.value = true;
  otpCooldown.value = OTP_COOLDOWN_SECONDS;

  cooldownTimer = setInterval(() => {
    otpCooldown.value--;
    if (otpCooldown.value <= 0) {
      if (cooldownTimer) clearInterval(cooldownTimer);
      otpSending.value = false;
    }
  }, 1000);
}

async function sendOtp() {
  message.value = '';
  messageType.value = '';

  const cleanPhone = phone.value ? phone.value.trim() : '';
  // Allow spaces in the mobile. Permits using firebase test numbers.
  if (!cleanPhone || !/^\d(?:\s?\d){9}$/.test(cleanPhone)) {
    message.value = 'Please enter a valid 10-digit mobile number.';
    messageType.value = 'error';
    return;
  }

  // Guard against double clicks while a send is already in flight/cooling down
  if (otpSending.value) return;

  // Disable immediately on click
  otpSending.value = true;
  otpCooldown.value = OTP_COOLDOWN_SECONDS;

  try {
    const recaptchaToken = await getRecaptchaToken();

    const response = await sendOtpResource.submit({
      phone: '+91' + phone.value,
      recaptcha_token: recaptchaToken,
    });

    sessionInfo.value = response.session_info;
    otpSent.value = true;
    showRegisterOption.value = false;
    message.value = 'OTP sent successfully.';
    messageType.value = 'success';

    startOtpCooldown();
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err.messages && err.messages.length > 0) {
      message.value = err.messages[0];

      if (err.messages[0].includes("Couldn't find any doctor with this number")) {
        showRegisterOption.value = true;
      }
    } else {
      message.value = 'Failed to send OTP.';
    }

    // Send failed — don't need to wait for cooldown
    otpSending.value = false;
  }
}

async function verifyOtp() {
  message.value = '';
  messageType.value = '';
  verifyingOtp.value = true;

  try {
    await verifyOtpResource.submit({
      session_info: sessionInfo.value,
      phone: phone.value,
      otp: otpEntry.value,
    });

    await userResource.reload();
    session.user = sessionUser();

    message.value = 'OTP verified successfully.';
    messageType.value = 'success';

    router.replace({ name: 'Dashboard' });
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err.messages && err.messages.length > 0) {
      message.value = err.messages[0];
    } else {
      message.value = 'Invalid OTP.';
    }
    verifyingOtp.value = false;
  }
}

function goToRegister(mobile = '') {
  router.push({
    name: 'Register',
    query: mobile ? { mobile } : {},
  });
}

// Auto-verify once the user has entered a full 6-digit OTP
watch(
  otpEntry,
  (newval) => {
    // Trigger verification when length matches
    if (newval.length === OTP_LENGTH) {      
      verifyOtp();
    }
  }
);
</script>
