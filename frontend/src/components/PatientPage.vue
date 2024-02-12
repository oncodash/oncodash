<template>
  <h1>PATIENT {{ id }}</h1>

  <PatientSummary :patient="patient" v-if="patient"></PatientSummary>

  <section class="patient-data" v-if="patient">
    <AppTabs>
      <AppTabsPanel name="CLINICAL DATA">
        <PatientClinical :patient="patient"></PatientClinical>
      </AppTabsPanel>

      <AppTabsPanel name="GENOMIC DATA">
        <PatientGenomic :patientID="id"></PatientGenomic>
      </AppTabsPanel>

      <AppTabsPanel name="EXPLAINER">
        EXPLAINER
      </AppTabsPanel>

      <AppTabsPanel name="OTHER">
        OTHER
      </AppTabsPanel>
    </AppTabs>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../api'
import AppTabs from "./AppTabs.vue"
import AppTabsPanel from './AppTabsPanel.vue'
import PatientSummary from "./PatientSummary.vue"
import PatientClinical from "./PatientClinical.vue"
import PatientGenomic from "./PatientGenomic.vue"
import { Patient, PatientID } from '../models/Patient'

const props = defineProps<{
  id: PatientID
}>()

const patient = ref<Patient>()

onMounted(async (): Promise<void> => {
  api.getPatientClinical(props.id).then(async response => {
    patient.value = new Patient(response.data)
  }).catch(err => {
    alert(err.message)
    console.error(err)
  })
})
</script>

<style scoped>
.patient-data {
  font-size: 18px;
  margin: var(--spacing);
}
</style>
