<template>
  <section class="patient-summary">
    <img src="../assets/patient.svg">

    <div>
      <PatientField field="Patient ID" :value="patientID()" />
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

const props = defineProps<{
  patient: Patient
}>()

function patientID(): string {
    return props.patient.patient_id.replace(":patient", "");
}
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

.aiforia-row {
  display: flex;
  flex-flow: row wrap;
  gap: var(--spacing);
  align-items: center;
  margin-top: 4px;
  padding-left: calc(50% + var(--spacing) / 2);
}

.aiforia-btn {
  display: inline-block;
  padding: 4px 12px;
  color: var(--primary);
  font-size: 0.85em;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid var(--primary);
  border-radius: var(--radius);
  transition: background-color 0.15s, color 0.15s;
}

.aiforia-btn:hover {
  background-color: var(--primary);
  color: white;
}
</style>
