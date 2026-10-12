import router from '@/router'
import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'

import { userResource } from './user'

export function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  let _sessionUser = cookies.get('user_id')
  if (_sessionUser === 'Guest') {
    _sessionUser = null
  }
  if (!_sessionUser && typeof window !== 'undefined') {
    _sessionUser = localStorage.getItem('user_id')
  }
  return _sessionUser || null
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
      // Frappe's /api/method/login always returns csrf_token in the response
      // body. frappeRequest returns the full data object for this URL, so
      // data.csrf_token is always populated. Update window.csrf_token so
      // subsequent POSTs don't carry the stale Guest token.
      if (data?.csrf_token) {
        window.csrf_token = data.csrf_token
      }
      userResource.reload().then(() => {
        session.user = userResource.data || sessionUser() || data?.user
        if (session.user && typeof window !== 'undefined') {
          localStorage.setItem('user_id', session.user)
        }
      })
      session.user = sessionUser() || data?.user
      if (session.user && typeof window !== 'undefined') {
        localStorage.setItem('user_id', session.user)
      }
      session.login.reset()
      router.replace({ name: 'Dashboard' })
    },
  }),
  logout: createResource({
    url: 'logout',
    onSuccess() {
      userResource.reset()
      session.user = null
      if (typeof window !== 'undefined') {
        localStorage.removeItem('user_id')
      }
      router.replace({ name: 'Login' })
    },
  }),
  user: sessionUser(),
  isLoggedIn: computed(() => Boolean(session.user && session.user !== 'Guest')),
})
