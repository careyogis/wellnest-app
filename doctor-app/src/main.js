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

// In dev mode, fetch the CSRF token BEFORE mounting the app so it is
// available when the router's beforeEach guard fires its first navigation
// and calls userResource.reload() (a POST). Without this, csrf_token is
// undefined at that point → Frappe returns 403 → redirect to Login.
const initPromise = import.meta.env.DEV
  ? frappeRequest({
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
  : Promise.resolve()

initPromise.then(() => {
  registerServiceWorker()
  app.mount('#app')
})
