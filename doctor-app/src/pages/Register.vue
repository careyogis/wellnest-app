<template>
  <div class="w-full min-h-screen p-0 bg-[#f5f7fb]">
    <div class="flex flex-col lg:flex-row min-h-screen">
      <!-- Left Side -->
      <div class="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12 bg-gradient-to-br from-[#fff8f0] via-[#fdeee0] to-[#fbe6d3]">
        <div class="text-gray-900 py-4 max-w-[520px] w-full">
          <img src="@/assets/images/logo-01.png" class="w-[220px] mb-4" />

          <span class="inline-flex items-center rounded-full bg-white text-gray-900 px-3 py-1.5 mb-3 text-sm font-medium shadow-sm border border-orange-100"> Join CareYogi </span>

          <h1 class="text-3xl lg:text-4xl font-bold text-gray-900">CareYogi Doctor App</h1>

          <p class="mt-3 text-gray-500 leading-relaxed">Create your doctor account and start managing your professional profile, availability, consultations, and patient care from one workspace.</p>

          <div class="bg-white rounded-2xl shadow-sm mt-4 p-4 space-y-1">
            <div class="flex items-start py-2 border-b border-gray-200">
              <FeatherIcon name="user-plus" class="w-6 h-6 mr-3 shrink-0 text-[#f5a623]" />
              <div>
                <strong class="text-gray-900 font-semibold"> Quick registration </strong>
                <div class="text-sm text-gray-500">Create your CareYogi doctor account in a few simple steps.</div>
              </div>
            </div>

            <div class="flex items-center py-2 border-b border-gray-200">
              <FeatherIcon name="user-check" class="w-5 h-5 mr-3 shrink-0 text-[#f5a623]" />
              <span class="text-gray-700"> Your doctor profile is created automatically. </span>
            </div>

            <div class="flex items-center py-2 border-b border-gray-200">
              <FeatherIcon name="calendar" class="w-5 h-5 mr-3 shrink-0 text-[#f5a623]" />
              <span class="text-gray-700"> Add your professional details and availability later. </span>
            </div>

            <div class="flex items-center pt-2">
              <FeatherIcon name="shield" class="w-5 h-5 mr-3 shrink-0 text-[#f5a623]" />
              <span class="text-gray-700"> Secure access to your doctor workspace. </span>
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

            <div class="mb-6">
              <h2 class="text-2xl font-bold text-gray-900">Create your account</h2>

              <p class="mt-1 text-sm text-gray-500">Register as a CareYogi doctor</p>
            </div>

            <form v-if="!otpSent" @submit.prevent="register">
              <!-- First + Last Name -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="w-full">
                  <Input v-model="form.full_name" class="doctor-input w-full" label="Full Name" placeholder="Enter your full name" />
                </div>
              </div>

              <!-- Email -->
              <Input v-model="form.email" class="doctor-input mt-3" type="email" label="Email ID" placeholder="Enter email address" required />

              <!-- Mobile -->
              <Input v-model="form.mobile" class="doctor-input mt-3" label="Mobile Number" placeholder="Enter mobile number" required />

              <!-- Message -->
              <div v-if="message" :class="['p-3 rounded-lg mt-4 text-sm border', messageType === 'success' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200']">
                {{ message }}
              </div>

              <!-- Register -->
              <Button class="w-full mt-6 doctor-btn" variant="solid" type="submit" :disabled="loading">
                {{ loading ? 'Creating Account...' : 'Create Account' }}
              </Button>
            </form>

            <div v-else>
              <div class="mb-5">
                <h3 class="text-lg font-semibold text-gray-900">Verify your mobile number</h3>

                <p class="mt-1 text-sm text-gray-500">Enter the 6-digit OTP sent to +91 {{ form.mobile }}</p>
              </div>

              <Input v-model="otp" class="doctor-input" label="OTP" placeholder="Enter 6-digit OTP" maxlength="6" />

              <Button
                class="w-full mt-5 doctor-btn !bg-black !text-white hover:!bg-gray-800 disabled:!bg-black disabled:!text-white"
                variant="solid"
                :disabled="otp.length !== 6 || verifyingOtp"
                @click="verifyOtp"
              >
                {{ verifyingOtp ? 'Verifying...' : 'Verify & Continue' }}
              </Button>
            </div>

            <!-- Login -->
            <div class="text-center mt-6">
              <span class="text-sm text-gray-500"> Already have an account? </span>

              <button type="button" class="ml-1 text-sm font-medium text-blue-600 hover:underline" @click="goToLogin">Login</button>
            </div>
          </div>
        </Card>
      </div>
    </div>
    <div id="register-recaptcha-container"></div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';
import { useRouter } from 'vue-router';
import { session, sessionUser } from '../data/session';
import { userResource } from '../data/user';

declare const grecaptcha: any;

const router = useRouter();

const RECAPTCHA_SITE_KEY = '6LcMZR0UAAAAALgPMcgHwga7gY5p8QMg1Hj-bmUv';

const OTP_LENGTH = 6;

const form = reactive({
  full_name: '',
  email: '',
  mobile: '',
});

const loading = ref(false);
const message = ref('');
const messageType = ref<'success' | 'error' | ''>('');

const otp = ref('');
const otpSent = ref(false);
const sessionInfo = ref('');
const verifyingOtp = ref(false);

let recaptchaWidgetId: number | null = null;

const sendOtpResource = createResource({
  url: 'wellnest.api.auth.send_registration_otp',
});

const verifyOtpResource = createResource({
  url: 'wellnest.api.auth.verify_registration_otp',
});

onMounted(() => {
  if (!document.getElementById('recaptcha-script')) {
    const script = document.createElement('script');
    script.id = 'recaptcha-script';
    script.src = 'https://www.google.com/recaptcha/api.js?render=explicit';
    script.async = true;
    document.head.appendChild(script);
  }
});

function goToLogin() {
  router.push({ name: 'Login' });
}

function renderRecaptcha(): Promise<number> {
  return new Promise((resolve) => {
    const check = setInterval(() => {
      if (typeof grecaptcha !== 'undefined' && grecaptcha.render) {
        clearInterval(check);

        const id = grecaptcha.render('register-recaptcha-container', {
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

        if (token) {
          resolve(token);
        } else {
          reject(new Error('No reCAPTCHA token received'));
        }
      })
      .catch(reject);
  });
}

async function register() {
  message.value = '';
  messageType.value = '';

  const mobile = form.mobile.trim();

  // Allow spaces in the mobile. Permits using firebase test numbers.
  if (!/^\d(?:\s?\d){9}$/.test(mobile)) {
    message.value = 'Please enter a valid 10-digit mobile number.';
    messageType.value = 'error';
    return;
  }

  loading.value = true;

  try {
    const recaptchaToken = await getRecaptchaToken();

    const otpResponse = await sendOtpResource.submit({
      phone: '+91' + mobile,
      recaptcha_token: recaptchaToken,
    });

    sessionInfo.value = otpResponse.session_info;
    otpSent.value = true;

    message.value = 'OTP sent to your mobile number.';
    messageType.value = 'success';
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err?.messages?.length) {
      message.value = err.messages[0];
    } else {
      message.value = 'Unable to send OTP.';
    }
  } finally {
    loading.value = false;
  }
}

async function verifyOtp() {
  if (verifyingOtp.value) return;

  if (otp.value.length !== OTP_LENGTH) {
    return;
  }

  message.value = '';
  messageType.value = '';
  verifyingOtp.value = true;

  try {
    const fullName = form.full_name.trim();
    const nameParts = fullName.split(/\s+/);

    const first_name = nameParts[0];
    const last_name = nameParts.slice(1).join(' ');

    if (!first_name || !last_name) {
      message.value = 'Please enter your full name.';
      messageType.value = 'error';
      return;
    }
    const response = await verifyOtpResource.submit({
      session_info: sessionInfo.value,
      code: otp.value,
      first_name,
      last_name,
      email: form.email.trim(),
      mobile: form.mobile.trim(),
    });

    session.user = response.user;

    message.value = 'Registration successful.';
    messageType.value = 'success';

    router.replace({ name: 'Dashboard' });
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err?.messages?.length) {
      message.value = err.messages[0];
    } else {
      message.value = 'Invalid OTP.';
    }
  } finally {
    verifyingOtp.value = false;
  }
}

watch(otp, (newValue) => {
  if (newValue.length === OTP_LENGTH) {
    verifyOtp();
  }
});
</script>
