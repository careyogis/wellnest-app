import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import './assets/style.css'

import {
  Button,
  Card,
  Input,
  setConfig,
  frappeRequest,
  resourcesPlugin,
} from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)
// app.component('star-rating', VueStarRating)

app.mount('#app')

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js', { scope: '/doctor-app/' })
      .catch((error) => {
        console.warn('PWA ServiceWorker registration failed:', error)
      })
  })
}

