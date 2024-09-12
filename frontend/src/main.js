import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
// import VueStarRating from 'vue-star-rating'

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
