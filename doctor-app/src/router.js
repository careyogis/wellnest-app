import { createRouter, createWebHistory } from 'vue-router';
import { session } from './data/session';
import { userResource } from '@/data/user';

const routes = [
  {
    path: '/',
    redirect: { name: 'Login' },
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
        component: () => import('@/pages/ComingSoon.vue'),
        props: { title: 'Patients' },
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
        component: () => import('@/pages/ComingSoon.vue'),
        props: { title: 'Earnings' },
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

router.beforeEach(async (to, from, next) => {
  let isLoggedIn = session.isLoggedIn;

  // Login and Register are public pages
  if (to.name === 'Login' || to.name === 'Register') {
    if (to.name === 'Login' && isLoggedIn) {
      next({ name: 'Dashboard' });
    } else {
      next();
    }
    return;
  }

  if (!isLoggedIn) {
    try {
      await userResource.reload();
      isLoggedIn = session.isLoggedIn;
    } catch (error) {
      isLoggedIn = false;
    }
  }

  if (!isLoggedIn) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;
