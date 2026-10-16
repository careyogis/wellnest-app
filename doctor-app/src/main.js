import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import './assets/style.css'

import {
  Button,
  Card,
  Input,
  Dialog,
  Popover,
  FeatherIcon,
  setConfig,
  frappeRequest,
  resourcesPlugin,
} from 'frappe-ui'

import { session } from './data/session'
import { userResource } from './data/user'
import { profileData } from './data/doctorProfile'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)
app.component('Dialog', Dialog)
app.component('Popover', Popover)
app.component('FeatherIcon', FeatherIcon)

if (session?.isLoggedIn && !profileData?.data) {
  profileData.reload()
}

app.provide('$session', session)
app.provide('$user', userResource)
app.provide('$profile', profileData)

const registerServiceWorker = () => {
  if ('serviceWorker' in navigator) {
    let serviceWorkerURL = '/sw.js'
    navigator.serviceWorker
      .register(serviceWorkerURL, { scope: '/doctor-app/' })
      .then((registration) => {
        console.log('PWA ServiceWorker registered with scope:', registration.scope)
      })
      .catch((error) => {
        console.warn('PWA ServiceWorker registration failed:', error)
      })
  } else {
    console.warn('Service worker not supported by the browser')
  }
}

router.isReady().then(async () => {
  if (import.meta.env.DEV) {
    await frappeRequest({
      url: '/api/method/wellnest.www.doctor_app.get_context_for_dev',
    })
      .then((values) => {
        if (!window.frappe) window.frappe = {}
        window.frappe.boot = values
        if (values?.csrf_token) {
          window.csrf_token = values.csrf_token
        }
      })
      .catch((err) => {
        console.warn('Could not load dev context:', err)
      })
  }

  registerServiceWorker()
  app.mount('#app')
})
