import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import { FrappeUI } from 'frappe-ui'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)
//app.use(FrappeUI)

app.component('Button', Button)
app.mount('#app')
