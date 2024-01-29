import { createRouter, createWebHistory } from 'vue-router'

// =========================================================================

export default createRouter({
  // Use the History API of the browser
  history: createWebHistory(),

  // Routes of the application
  routes: [
    {
      path: '/',
      component: async () => await import('./components/PatientsPage.vue'),
      name: 'PatientsPage'
    },
    {
      path: '/patients',
      redirect: { name: 'PatientsPage' }
    },
    {
      path: '/patients/:id',
      component: async () => await import('./components/PatientPage.vue'),
      name: 'PatientPage'
    },
    {
      path: '/:pathMatch(.*)*',
      component: async () => await import('./components/404Page.vue'),
      name: '404Page'
    }
  ]
})
