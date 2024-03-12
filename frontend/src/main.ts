import { createApp } from 'vue'
import App from './components/App.vue'
import router from './router'
import 'modern-normalize'
import './globals.css'

createApp(App)
  .use(router)
  .mount('#app')
