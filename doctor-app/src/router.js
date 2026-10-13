import { createRouter, createWebHistory } from 'vue-router';
import { session } from './data/session';
import { userResource } from '@/data/user';

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
        component: () => import('@/pages/ComingSoon.vue'),
        props: { title: 'Messages' },
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

let isInitialAuthChecked = false;

router.beforeEach(async (to, from, next) => {
  // On initial app launch / page load, verify session with Frappe backend
  if (!isInitialAuthChecked) {
    isInitialAuthChecked = true;
    try {
      await userResource.reload();
      if (userResource.data && userResource.data !== 'Guest') {
        session.user = userResource.data;
        if (typeof window !== 'undefined') {
          localStorage.setItem('user_id', userResource.data);
        }
      } else {
        session.user = null;
        if (typeof window !== 'undefined') {
          localStorage.removeItem('user_id');
        }
      }
    } catch (error) {
      if (error && (error.exc_type === 'AuthenticationError' || error.httpStatus === 401 || error.httpStatus === 403)) {
        session.user = null;
        if (typeof window !== 'undefined') {
          localStorage.removeItem('user_id');
        }
      }
    }
  }

  const isLoggedIn = session.isLoggedIn;

  // Login and Register are public pages
  if (to.name === 'Login' || to.name === 'Register') {
    if (isLoggedIn) {
      next({ name: 'Dashboard' });
    } else {
      next();
    }
    return;
  }

  // All other pages are protected
  if (!isLoggedIn) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;
