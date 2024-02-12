<template>
  <section class="login-panel">
    <header>
      <h1>LOGIN</h1>
    </header>
    <label>
      <div>Email</div>
      <input
        v-model="email"
        @keyup.enter="login"
        type="email"
        name="email"
        autocomplete="email">
    </label>
    <label>
      <div>Password</div>
      <input
        v-model="password"
        @keyup.enter="login"
        type="password"
        name="password">
    </label>
    <footer>
      <button
        @click="login"
        :disabled="!inputsAreValid"
        type="button">
        SUBMIT
      </button>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useCookies } from '@vueuse/integrations/useCookies'
import api from '../api'
import router from '../router'

const cookies = useCookies()
const email = ref<string>('')
const password = ref<string>('')

const inputsAreValid = computed<boolean>(() => {
  return email.value.length > 0 && password.value.length > 0
})

function login(): void {
  if (!inputsAreValid.value) return

  api.login(email.value, password.value).then(async response => {
    cookies.set('token', response.data.token)
    router.replace({ name: "PatientsListPage" })
  }).catch(err => {
    alert(err.message)
    console.error(err.message)
  })
}
</script>

<style scoped>
.login-panel {
  display: flex;
  flex-flow: column wrap;
  gap: var(--spacing);
  width: clamp(280px, 50%, 500px);
  margin: 10vh auto 0 auto;
  border-radius: var(--radius);
  padding: var(--spacing);
  background-color: var(--white);
}

header h1 {
  color: var(--black);
  font-size: 20px;
  font-weight: normal;
  margin: 0;
}

label div {
  margin-bottom: calc(var(--spacing) / 2);
}

label input {
  width: 100%;
}

footer {
  display: flex;
  align-items: center;
  justify-content: end;
}
</style>
