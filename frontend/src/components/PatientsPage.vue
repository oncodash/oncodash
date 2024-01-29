<template>
  <h1>PATIENTS LIST</h1>
  <div class="patients-list">
    <PatientCard v-for="patient in patientsList" :patient="patient"/>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PatientCard from "../components/PatientCard.vue"
import api from '../api'

const patientsList: any = ref([])

onMounted(async () => {
  api.getPatientsList().then(async response => {
    patientsList.value = response.data
  }).catch(err => {
    alert(err.message)
    console.error(err)
  })
})
</script>

<style scoped>
h1 {
  color: var(--white);
  text-align: center;
}

.patients-list {
  background-color: var(--white);
  padding: var(--spacing);
  display: flex;
  flex-flow: row wrap;
  gap: var(--spacing);
}

.patients-list > * {
  flex-grow: 1;
  width: max(300px);
}
</style>
