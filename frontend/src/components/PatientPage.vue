<template>
  <h1>PATIENT {{ id }}</h1>

  <PatientSummary :patient="patient"></PatientSummary>

  <section class="patient-data">
    <AppTabs>
      <AppTabsPanel name="CLINICAL DATA">{{  patient }}</AppTabsPanel>
      <AppTabsPanel name="GENOMIC DATA">GENOMIC</AppTabsPanel>
      <AppTabsPanel name="EXPLAINER">EXPLAINER</AppTabsPanel>
      <AppTabsPanel name="OTHER">OTHER</AppTabsPanel>
    </AppTabs>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../api'
import AppTabs from "./AppTabs.vue"
import AppTabsPanel from './AppTabsPanel.vue'
import PatientSummary from "./PatientSummary.vue";

const props = defineProps<{
  id: string
}>()

onMounted(async () => {
  api.getPatientClinical(props.id).then(async response => {
    patient.value = response.data
  }).catch(err => {
    alert(err.message)
    console.error(err)
  })
})

const patient: any = ref({})
</script>

<style scoped>
.patient-data {
  margin: var(--spacing);
}
</style>
