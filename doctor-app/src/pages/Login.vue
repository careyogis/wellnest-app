<template>
  <div class="container-fluid min-vh-100 p-0" style="background: #f5f7fb">
    <div class="row min-vh-100 g-0">
      <!-- Left Side -->
      <div
        class="col-12 col-lg-6 d-flex align-items-center justify-content-center p-4 p-lg-5"
        style="background: linear-gradient(135deg, #fff8f0 0%, #fdeee0 60%, #fbe6d3 100%)"
      >
        <div class="text-dark py-4" style="max-width: 520px">
          <img src="@/assets/images/logo-01.png" style="width: 220px" class="mb-4" />

          <span class="badge rounded-pill bg-white text-dark px-3 py-2 mb-3 shadow-sm">
            Continuity of Care Platform
          </span>

          <h1 class="fw-bold">CareYogi Doctor App</h1>

          <p class="mt-3 text-muted">
            Stay connected with patients after discharge, review reports, manage follow-ups, and run consultations from one calm workspace.
          </p>

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
            <div class="d-flex align-items-center mb-4">
              <div
                class="rounded-circle text-white fw-bold d-flex align-items-center justify-content-center"
                style="width: 60px; height: 60px; font-size: 20px; background: linear-gradient(135deg, #4c8c6b, #f0a93a)"
              >
                YB
              </div>

              <div class="ms-3">
                <div class="text-muted small">Welcome back</div>
                <h4 class="mb-0 fw-semibold">Brig. (Retd.) Dr. Y. S. Bisht</h4>
              </div>
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

              <Button class="w-100 mt-4 doctor-btn" variant="solid"  type="submit"> Sign In </Button>
            </form>

            <!-- OTP -->
            <div v-else>
              <Input class="doctor-input" v-model="phone" label="Mobile Number" placeholder="Enter Mobile Number" />

              <Button class="w-100 mt-3 doctor-btn" variant="solid" @click="sendOtp"> Send OTP </Button>
              <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-danger', 'mt-3']">
                {{ message }}
              </div>

              <div v-if="otpSent">
                <Input class="mt-3 doctor-input" v-model="otp" label="OTP" placeholder="Enter OTP" />

                <Button class="w-100 mt-3 doctor-btn" variant="solid" @click="verifyOtp"> Verify OTP </Button>
              </div>
            </div>

            <div class="alert alert-info mt-4 mb-0">
              <i class="bi bi-shield-check me-2"></i>
              Prototype only. No backend or clinical data storage.
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
  <div id="recaptcha-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { session } from '../data/session';
import { userResource } from '../data/user';
import { sessionUser } from '../data/session';
import { createResource } from 'frappe-ui';
import router from '../router';

declare const grecaptcha: any;

//Public site key from https://www.google.com/recaptcha/admin - safe to expose in frontend acc. to documentation
const RECAPTCHA_SITE_KEY = '6LcMZR0UAAAAALgPMcgHwga7gY5p8QMg1Hj-bmUv';

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
const sessionInfo = ref('');
const message = ref('');
const messageType = ref<'success' | 'error' | ''>('');
let recaptchaWidgetId: number | null = null;

const loginWithPhone = createResource({
  url: 'wellnest.api.login_with_phone',
  makeParams() {
    return {
      phone: phone.value,
    };
  },
});

const sendOtpResource = createResource({ url: 'wellnest.api.send_otp' });
const verifyOtpResource = createResource({ url: 'wellnest.api.verify_otp' });

function submit(e: Event) {
  const formData = new FormData(e.target as HTMLFormElement);

  session.login.submit({
    email: formData.get('email'),
    password: formData.get('password'),
  });
}

function getErrorMessage(err: any) {
  if (err?._server_messages) {
    try {
      const messages = JSON.parse(err._server_messages);
      return JSON.parse(messages[0]).message;
    } catch (e) {}
  }

  return err?.message || 'Something went wrong.';
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

async function sendOtp() {
  message.value = '';
  messageType.value = '';

  if (!phone.value) {
    alert('Please enter your mobile number');
    return;
  }

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
  } catch (err: any) {
    console.error(err);

    messageType.value = 'error';

    if (err.messages && err.messages.length > 0) {
      message.value = err.messages[0];
    } else {
      message.value = 'Failed to send OTP.';
    }
  }
}

async function verifyOtp() {
  message.value = '';
  messageType.value = '';

  try {
    const response = await verifyOtpResource.submit({
      session_info: sessionInfo.value,
      code: otp.value,
    });

    await loginWithPhone.submit();

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
</script>
