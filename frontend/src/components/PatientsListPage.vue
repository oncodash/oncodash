<template>
  <h1>PATIENTS LIST</h1>

  <section class="patients-search">
    <input
      id="patients-filter"
      v-model="patientsFilter"
      type="search"
      placeholder="Search by patient ID or stage">
  </section>

  <section class="patients-list">
    <PatientCard v-for="patient in filteredPatients" :patient="patient" />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PatientCard from "../components/PatientCard.vue"
import api from '../api'

/**
 * Add a pagination
 * Fix the cards width
 * Link to get back to the patients lists
 *
 */

const patientsList = ref<any>([])
const patientsFilter = ref<string>('')

const filteredPatients = computed(() => {
  const filter = patientsFilter.value

  return patientsList.value.filter((patient: any) => {
    return patient.patient_id.toString().includes(filter)
      || patient.stage?.toString().includes(filter)
  })
})

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
.patients-search {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: var(--spacing);

  &::before {
    content: url("../assets/magnifying-glass-icon.svg");
    margin-right: calc(var(--spacing) / 2);
  }
}

#patients-filter {
  width: min(600px, 100%);
}

.patients-list {
  background-color: var(--white);
  padding: var(--spacing);
  display: flex;
  flex-flow: row wrap;
  gap: var(--spacing);
  justify-content: center;
}

.patients-list > * {
  width: 300px;
}
</style>
