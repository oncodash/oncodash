<template>
  <section class="patient-summary">
    <img src="../assets/patient.svg">

    <div>
      <div>
        <span class="field">Patient ID : </span>
        <span class="value">{{ patient.patient_id }}</span>
      </div>
      <div>
        <span class="field">Cohort : </span>
        <span class="value">{{ patient.cohort_code }}</span>
      </div>
      <div>
        <span class="field">Age : </span>
        <span class="value">{{ patient.age_at_diagnosis }}</span>
      </div>
      <div>
        <span class="field">Stage : </span>
        <span class="value">{{ patient.stage }}</span>
      </div>
    </div>

    <div>
      <div>
        <span class="field">Status : </span>
        <span
          class="value"
          :class="{ red: patientStatus === 'Deceased' }">
          {{ patientStatus }}
        </span>
      </div>
      <div>
        <span class="field">Current phase : </span>
        <span class="value">{{ patient.current_treatment_phase }}</span>
      </div>
      <div>
        <span class="field">Progression : </span>
        <span
          class="value"
          :class="{ red: patientProgression === 'No' }">
          {{ patientProgression }}
        </span>
      </div>
    </div>

    <div>
      <div>
        <span class="field">PFS : </span>
        <span class="value">{{ patient.paired_fresh_samples_available }}</span>
      </div>
      <div>
        <span class="field">PFI : </span>
        <span class="value">{{ patient.platinum_free_interval }}</span>
      </div>
      <div>
        <span class="field">Days to death : </span>
        <span class="value">{{ patient.days_to_death }}</span>
      </div>
      <div>
        <span class="field">Follow-up time : </span>
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

const patientProgression = computed(() => {
  if (props.patient.progression === true) return 'Yes'
  else if (props.patient.progression === false) return 'No'
  else props.patient.progression
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

.patient-summary>div {
  display: flex;
  flex-flow: column wrap;
  gap: 5px;
}

.field,
.value {
  font-weight: bold;
}

.value {
  color: var(--primary);
}

.value.red {
  color: var(--red);
}
</style>
