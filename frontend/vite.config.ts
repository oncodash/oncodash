import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue()
  ],
  root: 'src',
  base: process.env.ONCODASH_PUBLIC_PATH || '/',
  build: {
    outDir: '../dist',
    emptyOutDir: true
  },
  server: {
    port: 8080
  },
  define: {
    // Bundle feature flags to make the build slightly lighter.
    // https://github.com/vuejs/core/tree/main/packages/vue#bundler-build-feature-flags
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,

    // URL of the backend
    // https://vitejs.dev/config/shared-options.html#envprefix
    'import.meta.env.ONCODASH_API_URL': JSON.stringify(process.env.ONCODASH_API_URL) || "'http://127.0.0.1:8888'",

    // Public URL in case of proxy rewrites to handle
    'import.meta.env.ONCODASH_PUBLIC_PATH': JSON.stringify(process.env.ONCODASH_PUBLIC_PATH) || "'/'"
  }
})
