import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue()
  ],
  root: 'src',
  build: {
    outDir: '../dist',
    emptyOutDir: true
  },
  server: {
    port: 8080,
    proxy: {
      // Proxy to the backend API during development
      '^/api/.*': 'http://127.0.0.1:8888',
      '/api-token-auth/': 'http://127.0.0.1:8888'
    }
  },
  define: {
    // Bundle feature flags to make the build slightly lighter.
    // https://github.com/vuejs/core/tree/main/packages/vue#bundler-build-feature-flags
    __VUE_OPTIONS_API__: false,
    __VUE_PROD_DEVTOOLS__: false
  }
})
