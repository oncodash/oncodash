import { createRouter, createWebHistory } from 'vue-router'

// =========================================================================

export default createRouter({
  // Use the History API of the browser
  history: createWebHistory(),

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
      props: true
    },
    {
      path: '/:pathMatch(.*)*',
      component: async () => await import('./components/404Page.vue'),
      name: '404Page'
    }
  ]
})
