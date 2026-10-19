import { createRouter, createWebHistory } from 'vue-router';
import { session, sessionUser } from './data/session';
import { userResource } from '@/data/user';
import { profileData } from '@/data/doctorProfile';

const routes = [
  {
    path: '/',
    redirect: { name: 'Dashboard' },
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    name: 'Register',
    path: '/account/register',
    component: () => import('@/pages/Register.vue'),
  },
  {
    name: 'ConsultationRoom',
    path: '/consultation-room/:bookingId',
    component: () => import('@/pages/ConsultationRoom.vue'),
  },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    children: [
      {
        name: 'Dashboard',
        path: 'dashboard',
        component: () => import('@/pages/Dashboard.vue'),
      },
      {
        name: 'Profile',
        path: 'profile',
        component: () => import('@/pages/Profile.vue'),
      },
      {
        name: 'Patients',
        path: 'patients',
        component: () => import('@/pages/Patient.vue'),
      },
      {
         name: 'PatientDetails',
         path: 'patient-details',
         component: () => import('@/pages/PatientDetails.vue'),
      },
      {
        name: 'Schedule',
        path: 'schedule',
        component: () => import('@/pages/Schedule.vue'),
      },
      {
        name: 'Consultations',
        path: 'consultations',
        component: () => import('@/pages/Consultations.vue'),
      },
      {
        name: 'ConsultationDetails',
        path: 'consultations/:bookingId',
        component: () => import('@/pages/Consultations.vue'),
      },
      {
        name: 'WaitingRoom',
        path: 'consultations/:id/waiting-room',
        component: () => import('@/pages/WaitingRoom.vue'),
      },
      {
        name: 'Messages',
        path: 'messages',
        component: () => import('@/pages/Messages.vue'),
      },
      {
        name: 'Referrals',
        path: 'referrals',
        component: () => import('@/pages/ComingSoon.vue'),
        props: { title: 'Referrals' },
      },
      {
        name: 'Earnings',
        path: 'earnings',
        component: () => import('@/pages/Earnings.vue'),
      },
      {
        name: 'Notifications',
        path: 'notifications',
        component: () => import('@/pages/ComingSoon.vue'),
        props: { title: 'Notifications' },
      },
      {
        name: 'Settings',
        path: 'settings',
        component: () => import('@/pages/ComingSoon.vue'),
        props: { title: 'Settings' },
      },
    ],
  },
  {
    name: 'NotFound',
    path: '/:pathMatch(.*)*',
    component: () => import('@/pages/NotFound.vue'),
  },
];

let router = createRouter({
  history: createWebHistory('/doctor-app'),
  routes,
});

let isInitialAuthChecked = false

router.beforeEach(async (to, from, next) => {
  // On initial page load / browser refresh, verify session with Frappe backend.
  // We do not condition this on session.isLoggedIn because the HttpOnly `sid`
  // cookie is the true auth credential; document.cookie['user_id'] may temporarily
  // be missing or set to 'Guest' after a direct URL navigation.
  if (!isInitialAuthChecked) {
    isInitialAuthChecked = true
    try {
      await userResource.reload()
      if (userResource.data && userResource.data !== 'Guest') {
        session.user = userResource.data
        if (!profileData.data && !profileData.loading) {
          profileData.reload()
        }
      } else {
        session.user = null
      }
    } catch (error) {
      // Re-read the cookie / boot before deciding — if the session cookie is still
      // present the user is likely still authenticated; don't kick them out
      // over a transient network / CSRF error.
      const cookieUser = sessionUser()
      if (cookieUser) {
        console.warn(
          'Session verification failed but session cookie is still present. Continuing.',
          error,
        )
        session.user = cookieUser
      } else {
        session.user = null
      }
    }
  }

  const isLoggedIn = !!session.user

  if (!isLoggedIn) {
    if (!['Login', 'Register'].includes(to.name)) {
      return next({ name: 'Login' })
    }
  }

  if (isLoggedIn) {
    if (['Login', 'Register'].includes(to.name)) {
      return next({ name: 'Dashboard' })
    }
  }

  next()
})

export default router
