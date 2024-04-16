import { createApp } from 'vue'
import { createPinia } from 'pinia'
import CanvasJSStockChart from '@canvasjs/vue-stockcharts'
import App from './components/App.vue'
import router from './router'
import 'modern-normalize'
import './globals.css'

createApp(App)
  .use(createPinia())
  .use(router)
  .use(CanvasJSStockChart)
  .mount('#app')
