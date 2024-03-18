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
        autocomplete="email"
        ref="emailInput">
    </label>
    <label>
      <div>Password</div>
      <input
        v-model="password"
        @keyup.enter="login"
        type="password"
        name="password"
        autocomplete="off">
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

/**
 * Props that contain an optionnal route to redirect to
 * after the login.
 */
const props = defineProps<{
  to?: string
}>()

const cookies = useCookies()
const email = ref<string>('')
const password = ref<string>('')
const emailInput = ref<HTMLInputElement | null>(null)

const inputsAreValid = computed<boolean>(() => {
  return email.value.length > 0
    && emailInput.value?.checkValidity() === true
    && password.value.length > 0
})

function login(): void {
  if (!inputsAreValid.value) return

  api.login(email.value, password.value).then(async response => {
    cookies.set('token', response.data.token)

    if (props.to) {
      router.replace({ path: props.to })
    } else {
      router.replace({ name: "PatientsListPage" })
    }
  }).catch(err => {
    if (err.response.status === 400) {
      alert('Wrong credentials, please make sure to use the proper email and password.')
    }
    console.error(err)
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
