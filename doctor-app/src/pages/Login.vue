<template>
  <div class="container-fluid min-vh-100 p-0" style="background: #f5f7fb">
    <div class="row min-vh-100 g-0">
      <!-- Left Side -->
      <div class="col-12 col-lg-6 d-flex align-items-center justify-content-center p-4 p-lg-5" style="background: linear-gradient(135deg, #fff8f0 0%, #fdeee0 60%, #fbe6d3 100%)">
        <div class="text-dark py-4" style="max-width: 520px">
          <img src="@/assets/images/logo-01.png" style="width: 220px" class="mb-4" />

          <span class="badge rounded-pill bg-white text-dark px-3 py-2 mb-3 shadow-sm"> Continuity of Care Platform </span>

          <h1 class="fw-bold">CareYogi Doctor App</h1>

          <p class="mt-3 text-muted">Stay connected with patients after discharge, review reports, manage follow-ups, and run consultations from one calm workspace.</p>

          <div class="bg-white rounded-4 shadow-sm mt-4 p-4">
            <div class="d-flex align-items-start py-2 border-bottom">
              <i class="bi bi-shield-check fs-4 me-3" style="color: #f5a623"></i>
              <div>
                <strong>Private doctor workspace</strong>
                <div class="small text-muted">Secure access for verified CareYogi clinicians.</div>
              </div>
            </div>

            <div class="d-flex align-items-center py-2 border-bottom">
              <i class="bi bi-calendar-check fs-5 me-3" style="color: #f5a623"></i>
              <span>Receive bookings from patients based on your published availability.</span>
            </div>

            <div class="d-flex align-items-center py-2 border-bottom">
              <i class="bi bi-file-earmark-medical fs-5 me-3" style="color: #f5a623"></i>
              <span>Review patient uploads and post-discharge follow-ups.</span>
            </div>

            <div class="d-flex align-items-center pt-2">
              <i class="bi bi-chat-dots fs-5 me-3" style="color: #f5a623"></i>
              <span>Continue care through asynchronous patient messaging.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side -->
      <div class="col-12 col-lg-6 d-flex align-items-center justify-content-center p-4 p-lg-5">
        <Card class="shadow-lg border-0" style="max-width: 460px; width: 100%; border-radius: 20px">
          <div class="p-4">
            <div class="d-flex align-items-center justify-content-center mb-4">
              <img src="@/assets/images/logo-01.png" style="width: 160px" />
            </div>

            <div class="d-flex p-1 rounded-pill mb-4" style="background: #eef1f7">
              <button
                class="btn flex-fill border-0 rounded-pill"
                :class="loginMethod == 'password' ? 'bg-white shadow-sm fw-semibold' : 'bg-transparent text-muted'"
                :style="loginMethod == 'password' ? 'color: #f5a623' : ''"
                @click="loginMethod = 'password'"
              >
                Password
              </button>

              <button
                class="btn flex-fill border-0 rounded-pill"
                :class="loginMethod == 'otp' ? 'bg-white shadow-sm fw-semibold' : 'bg-transparent text-muted'"
                :style="loginMethod == 'otp' ? 'color: #f5a623' : ''"
                @click="loginMethod = 'otp'"
              >
                OTP
              </button>
            </div>

            <!-- PASSWORD -->
            <form v-if="loginMethod == 'password'" @submit.prevent="submit">
              <Input class="doctor-input" name="email" label="Username" placeholder="Enter username" />

              <Input class="doctor-input mt-2" type="password" name="password" label="Password" placeholder="Password" />

                <div v-if="message && loginMethod == 'password'" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-danger', 'mt-3']">
                  {{ message }}
                </div>
                
              <Button class="w-100 mt-4 doctor-btn" variant="solid" type="submit"> Sign In </Button>
            </form>

            <!-- OTP -->
            <div v-else>
              <Input class="doctor-input" v-model="phone" label="Mobile Number" placeholder="Enter Mobile Number" />

              <Button class="w-100 mt-3 doctor-btn" variant="solid" :disabled="otpSending" @click="sendOtp">
                {{ otpSending ? `Resend OTP in ${otpCooldown}s` : 'Send OTP' }}
              </Button>
              <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-danger', 'mt-3']">
                {{ message }}
              </div>

              <div v-if="otpSent">
                <Input class="mt-3 doctor-input" v-model="otp" label="OTP" placeholder="Enter OTP" />

                <Button class="w-100 mt-3 doctor-btn" variant="solid" @click="verifyOtp"> Verify OTP </Button>
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
import { createResource } from 'frappe-ui';
import router from '../router';

declare const grecaptcha: any;

//Public site key from https://www.google.com/recaptcha/admin - safe to expose in frontend acc. to documentation
const RECAPTCHA_SITE_KEY = '6LcMZR0UAAAAALgPMcgHwga7gY5p8QMg1Hj-bmUv';



const loginMethod = ref('password');

const phone = ref('');
const otp = ref('');
const otpSent = ref(false);
const sessionInfo = ref('');
const message = ref('');
const messageType = ref<'success' | 'error' | ''>('');
let recaptchaWidgetId: number | null = null;

// OTP resend cooldown state
const otpSending = ref(false);
const otpCooldown = ref(0);
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
  if (!cleanPhone || !/^\d{10}$/.test(cleanPhone)) {
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

    message.value = 'OTP sent successfully.';
    messageType.value = 'success';

    startOtpCooldown();
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err.messages && err.messages.length > 0) {
      message.value = err.messages[0];
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

  try {
    await verifyOtpResource.submit({
      session_info: sessionInfo.value,
      code: otp.value,
    });

    await userResource.reload();
    session.user = sessionUser();

    message.value = 'OTP verified successfully.';
    messageType.value = 'success';

    router.replace({ name: 'Profile' });
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err.messages && err.messages.length > 0) {
      message.value = err.messages[0];
    } else {
      message.value = 'Invalid OTP.';
    }
  }
}

// Auto-verify once the user has entered a full 6-digit OTP
watch(otp, (newVal) => {
  if (newVal.length === OTP_LENGTH) {
    verifyOtp();
  }
});
</script>
