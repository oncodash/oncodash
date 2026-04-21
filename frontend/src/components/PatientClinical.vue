<template>
  <section class="clinical-data">
    <div>
      <div class="title">BASELINE</div>
      <PatientField field="Age at diagnosis" :value="patient.age_at_diagnosis" />
      <PatientField field="BMI at diagnosis" :value="patientBMI()" />
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
      <PatientField field="HRD status (SBS3)" :value="patient.hr_signature_per_patient" />
      <PatientField field="BRCA mutation" :value="patient.brca_mutation_status" />
      <PatientField field="Germ line pathogenic variants" :value="patient.germline_pathogenic_variant" />
    </div>
  </section>

  <section class="timelines">
     <hr />
     <div class="images-row">
        <h3>Clinical Timeline</h3>
        <a      :href="`../assets/images/timeline_${patient.patient_id}.png`">
            <img :src="`../assets/images/timeline_${patient.patient_id}.png`"
                 :alt="`Clinical timeline for patient ${patient.patient_id}.`"
            />
        </a>
      </div>
  </section>

  <section class="graph">
     <hr />
     <div class="images-row">
        <h3>Signaling network</h3>
        <a      :href="`../assets/images/graph_${patient.patient_id}.png`">
            <img :src="`../assets/images/graph_${patient.patient_id}.png`"
                 :alt="`Signaling network for patient ${patient.patient_id}.`"
            />
        </a>
      </div>
  </section>

  <section class="aiforia">
      <hr />
      <div v-if="aiforiaEnabled" class="images-row">
        <h3>Histopathology Images</h3>
        <a :href="`${aiforiaBridgeUrl}?patientRef=${patient.cohort_code}`"
           target="_blank"
           class="aiforia-btn">View histopathology samples in Aiforia &#x2197;</a>
      </div>
  </section>
</template>

<script setup lang="ts">

import { Patient } from '../models/Patient'
import PatientField from './PatientField.vue'
import PatientTimelines from './PatientTimelines.vue'

const props = defineProps<{
  patient: Patient
}>()

function patientBMI(): string {
    if (props.patient.bmi_at_diagnosis) {
        return props.patient.bmi_at_diagnosis.toFixed(2) + ' kg/m²'; // FIXME round before toFixed
    } else {
        return "-";
    }
}

const aiforiaBridgeUrl = import.meta.env.ONCODASH_AIFORIA_BRIDGE_URL as string
const aiforiaEnabled = !!aiforiaBridgeUrl

</script>

<style scoped>
.clinical-data {
  display: flex;
  flex-flow: row wrap;
  gap: var(--spacing);
  justify-content: center;
  padding: var(--spacing);
}

hr {
    margin-left: 2em;
    margin-right: 2em;
    border: thin solid lightgrey;
}

.timelines {
}

.clinical-data>* {
  flex: 1 1;
}

.title {
  font-weight: bold;
  margin-bottom: var(--spacing);
  text-align: center;
}

.timelines .no-data {
  text-align: center;
  padding: var(--spacing);
  font-style: italic;
}

.images-row {
  gap: var(--spacing);
  text-align: center;
}

.images-row img {
    width: 50%;
}

.aiforia-btn {
  margin: 1em;
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
