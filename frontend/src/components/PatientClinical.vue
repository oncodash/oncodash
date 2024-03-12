<template>
  <section class="clinical-data">
    <div>
      <div class="title">BASELINE</div>
      <PatientField field="Cohort" :value="patient.cohort_code" />
      <PatientField field="Age at diagnosis" :value="patient.age_at_diagnosis" />
      <PatientField field="BMI at diagnosis" :value="patient.bmi_at_diagnosis + ' kg/m²'" />
      <PatientField field="Previous cancer" :value="patient.previous_cancer" />
    </div>

    <div>
      <div class="title">TREATMENT</div>
      <PatientField field="Strategy" :value="patient.treatment_strategy" />
      <PatientField field="Primary outcome" :value="patient.primary_therapy_outcome" />
      <PatientField field="PDS" :value="patient.residual_tumor_pds" />
      <PatientField field="IDS" :value="patient.residual_tumor_ids" />
      <PatientField field="Maintenance after 1st line" :value="patient.maintenance_therapy" />
      <PatientField field="Participation in drug trial" :value="patient.drug_trial_name" />
      <PatientField field="Progression" :value="patient.displayProgression()" />
    </div>

    <div>
      <div class="title">BASIC GENETICS</div>
      <PatientField field="HRD status" :value="patient.hrd_myriad_status" />
      <PatientField field="BRCA mutation" :value="patient.brca_mutation_status" />
      <PatientField field="Germ line pathogenic variants" :value="patient.germline_pathogenic_variant" />
    </div>
  </section>

  <section class="timelines">
    <div>No time series data available for this patient</div>
  </section>
</template>

<script setup lang="ts">
import { Patient } from '../models/Patient'
import PatientField from './PatientField.vue'

defineProps<{
  patient: Patient
}>()
</script>

<style scoped>
.clinical-data {
  display: flex;
  flex-flow: row wrap;
  gap: var(--spacing);
  justify-content: center;
  padding: var(--spacing);
}

.clinical-data>* {
  flex: 1 1;
}

.title {
  font-weight: bold;
  margin-bottom: var(--spacing);
  text-align: center;
}

.timelines {
  text-align: center;
  padding: var(--spacing);
  font-style: italic;
}
</style>
