import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/city',
    name: 'City',
    component: () => import('@/pages/City.vue'),
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    name: 'Profile',
    path: '/profile',
    component: () => import('@/pages/Profile.vue'),
  },
  {
    name: 'Activity',
    path: '/activity/:dailyRecordId',
    component: () => import('@/pages/Activity.vue'),
    props: true
  },
  {
    name: 'Test',
    path: '/test',
    component: () => import('@/pages/Test.vue'),
  },
  {
    name: 'staticLogin',
    path: '/staticLogin',
    component: () => import('@/pages/static_login.vue')
  },
]

let router = createRouter({
  history: createWebHistory('/caregiver-app'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Dashboard' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
