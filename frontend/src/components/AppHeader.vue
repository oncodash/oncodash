<template>
  <header>
    <RouterLink :to="{ name: 'PatientsListPage' }" v-slot="{ navigate }">
      <img
        src="/oncodash-logo.svg"
        alt="The logo of Oncodash"
        height="64"
        width="300"
        @click="navigate">
    </RouterLink>
    <RouterLink v-if="!isLoggedIn" :to="{ name: 'LoginPage' }" v-slot="{ navigate }">
      <button type="button" @click="navigate">LOGIN</button>
    </RouterLink>
    <button v-else type="button" @click="logout">LOGOUT</button>
  </header>
</template>

<script setup lang="ts">
import { useCookies } from '@vueuse/integrations/useCookies'
import router from '../router'
import { computed } from 'vue'
import api from '../api'

const cookies = useCookies()
const isLoggedIn = computed<boolean>(() => {
  return cookies.get('token') ? true : false
})

function logout(): void {
  api.logout().then(() => {
    cookies.remove('token')
    router.push({ name: 'LoginPage'})
  }).catch(err => {
    alert(err.message)
    console.error(err)
  })
}
</script>

<style scoped>
header {
  color: var(--white);
  display: flex;
  align-items: center;
  flex-flow: row wrap;
  gap: var(--spacing);
  justify-content: space-between;
  padding: var(--spacing);
}

button {
  border-radius: 20px;
  padding-left: 20px;
  padding-right: 20px;
}
</style>
