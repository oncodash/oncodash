<template>
  <section class="patient-summary">
    <img src="../assets/patient.svg">

    <div>
      <PatientField field="Patient ID" :value="patient.patient_id" />
      <PatientField field="Cohort" :value="patient.cohort_code" />
      <PatientField field="Age at diagnosis" :value="patient.age_at_diagnosis" />
      <PatientField field="Stage" :value="patient.stage" />
    </div>

    <div>
      <PatientField field="Status" :value="patient.displayStatus()" />
      <PatientField field="Current phase" :value="patient.current_treatment_phase" />
      <PatientField field="Progression" :value="patient.displayProgression()" />
    </div>

    <div>
      <PatientField field="PFS" :value="patient.paired_fresh_samples_available" />
      <PatientField field="PFI" :value="patient.platinum_free_interval" />
      <PatientField field="Days to death" :value="patient.days_to_death" />
      <PatientField field="Follow-up time" :value="patient.followup_time" />
    </div>
  </section>
</template>

<script setup lang="ts">
import PatientField from './PatientField.vue'
import { Patient } from '../models/Patient'

defineProps<{
  patient: Patient
}>()
</script>

<style scoped>
.patient-summary {
  align-items: center;
  background-color: var(--white);
  border-radius: var(--radius);
  display: flex;
  margin: auto;
  padding: var(--spacing);
  width: max(500px, 70%);
}

.patient-summary>div {
  flex: 1 1;
}
</style>
