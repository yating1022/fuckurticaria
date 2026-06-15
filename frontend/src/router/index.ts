import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/outbreaks',
      name: 'outbreaks',
      component: () => import('../views/OutbreakListView.vue'),
    },
    {
      path: '/outbreaks/new',
      name: 'outbreak-new',
      component: () => import('../views/OutbreakFormView.vue'),
    },
    {
      path: '/outbreaks/:id/edit',
      name: 'outbreak-edit',
      component: () => import('../views/OutbreakFormView.vue'),
    },
    {
      path: '/charts',
      name: 'charts',
      component: () => import('../views/OutbreakChartsView.vue'),
    },
    {
      path: '/medications',
      name: 'medications',
      component: () => import('../views/MedicationView.vue'),
    },
    {
      path: '/uas7',
      name: 'uas7',
      component: () => import('../views/UAS7View.vue'),
    },
    {
      path: '/lifestyle',
      name: 'lifestyle',
      component: () => import('../views/LifestyleView.vue'),
    },
    {
      path: '/weather',
      name: 'weather',
      component: () => import('../views/WeatherView.vue'),
    },
    {
      path: '/ai',
      name: 'ai',
      component: () => import('../views/AIAnalysisView.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!token && to.name !== 'login') {
    return { name: 'login' }
  }
  if (token && to.name === 'login') {
    return { name: 'home' }
  }
})

export default router
