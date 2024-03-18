import { NavigationGuard, createRouter, createWebHistory } from 'vue-router'
import Cookies from 'universal-cookie'

// =========================================================================

const base = import.meta.env.ONCODASH_PUBLIC_PATH
const cookies = new Cookies()

/**
 * Navigation guard to redirect to the login page if no cookies are detected.
 */
const checkLogin: NavigationGuard = function (to) {
  if (!cookies.get('token')) {
    return { name: 'LoginPage', query: { to: to.fullPath } }
  }

  return true
}

/**
 * The main router of the application.
 */
const router = createRouter({

  // Use the History API of the browser
  history: createWebHistory(base),

  // Routes of the application
  routes: [
    {
      path: '/',
      component: async () => await import('./components/PatientsListPage.vue'),
      name: 'PatientsListPage',
      beforeEnter: checkLogin
    },
    {
      path: '/patients',
      redirect: { name: 'PatientsListPage' },
    },
    {
      path: '/patients/:id',
      component: async () => await import('./components/PatientPage.vue'),
      name: 'PatientPage',
      props: route => ({ id: parseInt(route.params.id as string) }),
      beforeEnter: checkLogin
    },
    {
      path: '/login',
      component: async () => await import('./components/LoginPage.vue'),
      name: 'LoginPage',
      props: route => ({ to: route.query.to })
    },
    {
      path: '/:pathMatch(.*)*',
      component: async () => await import('./components/404Page.vue'),
      name: '404Page'
    }
  ],
})

// =========================================================================

export default router
