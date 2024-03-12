<template>
  <div class="patient-card">
    <div class="header">
      <span class="id">PATIENT {{ patient.patient_id }}</span>
      <span class="cohort">Cohort {{ patient.cohort_code }}</span>
    </div>

    <div class="content">
      <PatientField field="Age" :value="patient.age_at_diagnosis" />
      <PatientField field="Status" :value="props.patient.displayStatus()" />
      <PatientField field="Stage" :value="patient.stage" />
    </div>

    <div class="footer">
      <RouterLink
        :to="{ name: 'PatientPage', params: { id: patient.patient_id } }"
        v-slot="{ navigate }"
      >
        <button type="button" @click="navigate">Read more</button>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import PatientField from './PatientField.vue'
import { Patient } from '../models/Patient'

const props = defineProps<{
  patient: Patient
}>()
</script>

<style scoped>
.patient-card {
  background-color: var(--green-light);
  border-radius: var(--radius);
  padding: var(--spacing);
  display: flex;
  flex-flow: column wrap;
  gap: var(--spacing);
  box-shadow:
    0 2px 3px hsla(0, 0%, 0%, 0.15),
    0 1px 3px hsla(0, 0%, 0%, 0.3);
  transition: box-shadow 0.2s;
}

.patient-card:hover {
  box-shadow:
    0 10px 10px hsla(0, 0%, 0%, 0.3),
    0 2px 10px hsla(0, 0%, 0%, 0.3)
}

.header {
  display: flex;
  flex-flow: column wrap;
  text-align: center;
}

.id {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: calc(var(--spacing) / 2);
}

.cohort {
  font-style: italic;
}

.content {
  display: flex;
  flex-flow: column wrap;
}

.footer {
  text-align: center;
}
</style>
