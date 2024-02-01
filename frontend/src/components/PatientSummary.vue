<template>
  <section class="patient-summary">
    <img src="../assets/patient.svg">

    <div>
      <div>
        Patient ID -
        <span class="value">{{ patient.patient_id }}</span>
      </div>
      <div>
        Cohort -
        <span class="value">{{ patient.cohort_code }}</span>
      </div>
      <div>
        Age -
        <span class="value">{{ patient.age_at_diagnosis }}</span>
      </div>
      <div>
        Stage -
        <span class="value">{{ patient.stage }}</span>
      </div>
    </div>

    <div>
      <div>
        Status -
        <span class="value">{{ patientStatus }}</span>
      </div>
      <div>
        Current phase -
        <span class="value">{{ patient.current_treatment_phase }}</span>
      </div>
      <div>
        Progression -
        <span class="value">{{ patient.progression }}</span>
      </div>
    </div>

    <div>
      <div>
        PFS -
        <span class="value">{{ patient.paired_fresh_samples_available }}</span>
      </div>
      <div>
        PFI -
        <span class="value">{{ patient.platinum_free_interval }}</span>
      </div>
      <div>
        Days to death -
        <span class="value">{{ patient.days_to_death }}</span>
      </div>
      <div>
        Follow-up time -
        <span class="value">{{ patient.followup_time }}</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  patient: any
}>()

const patientStatus = computed(() => {
  if (props.patient.survival === 'True') return 'Alive'
  else if (props.patient.survival === 'False') return 'Deceased'
  else 'Unknown'
})
</script>

<style scoped>
.patient-summary {
  align-items: center;
  background-color: var(--white);
  border-radius: var(--radius);
  display: flex;
  justify-content: space-around;
  margin: auto;
  padding: var(--spacing);
  width: max(500px, 70%);
}

.patient-summary > div {
  display: flex;
  flex-flow: column wrap;
  gap: 5px;
}

.patient-summary .value {
  font-weight: bold;
}
</style>
