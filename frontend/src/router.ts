import { createRouter, createWebHistory } from 'vue-router'
import Cookies from 'universal-cookie'

// =========================================================================

const base = import.meta.env.ONCODASH_PUBLIC_PATH
const cookies = new Cookies()

const router = createRouter({

  // Use the History API of the browser
  history: createWebHistory(base),

  // Routes of the application
  routes: [
    {
      path: '/',
      component: async () => await import('./components/PatientsListPage.vue'),
      name: 'PatientsListPage'
    },
    {
      path: '/patients',
      redirect: { name: 'PatientsListPage' }
    },
    {
      path: '/patients/:id',
      component: async () => await import('./components/PatientPage.vue'),
      name: 'PatientPage',
      props: route => ({ id: parseInt(route.params.id as string) })
    },
    {
      path: '/login',
      component: async () => await import('./components/LoginPage.vue'),
      name: 'LoginPage'
    },
    {
      path: '/:pathMatch(.*)*',
      component: async () => await import('./components/404Page.vue'),
      name: '404Page'
    }
  ],
})

// Navigation guard to redirect to the login page
// if no cookies are detected.
router.beforeEach((to) => {
  if (!cookies.get('token') && to.name !== 'LoginPage') {
    return { name: 'LoginPage' }
  }

  return true
})

// =========================================================================

export default router
