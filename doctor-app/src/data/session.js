import router from '@/router'
import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'
import { userResource } from './user'
import { profileData } from './doctorProfile'

export function sessionUser() {
  let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  let _sessionUser = cookies.get('user_id')
  if (_sessionUser === 'Guest') {
    _sessionUser = null
  }
  return _sessionUser
}

export const session = reactive({
  login: createResource({
    url: 'login',
    makeParams({ email, password }) {
      return {
        usr: email,
        pwd: password,
        device: 'mobile',
      }
    },
    onSuccess(data) {
      if (data?.csrf_token) {
        window.csrf_token = data.csrf_token
      }
      session.user = sessionUser() || data?.user
      userResource.reload().then(() => {
        session.user = sessionUser() || userResource.data || data?.user
        profileData.reload()
      })
      session.login.reset()
      router.replace({ name: 'Dashboard' })
    },
  }),
  logout: createResource({
    url: 'logout',
    onSuccess() {
      userResource.reset()
      profileData.reset()
      session.user = sessionUser()
      router.replace({ name: 'Login' })
      window.location.reload()
    },
  }),
  user: sessionUser(),
  isLoggedIn: computed(() => !!session.user),
})
