<template>
  <section class="genomic-numbers">
    <div class="genomic-number" v-for="genomicNumber in genomicData.genomic">
      <div class="number">{{ genomicNumber[0] }}</div>
      <div class="name">{{ genomicNumber[1] }}</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../api'

const props = defineProps<{
  patientID: string
}>()

const genomicData: any = ref({})

onMounted(() => {
  api.getPatientGenomic(props.patientID)
    .then(async response => {
      genomicData.value = response.data
    }).catch(err => {
      alert(err.message)
      console.error(err)
    })
})
</script>

<style scoped>
.genomic-numbers {
  display: flex;
  gap: var(--spacing);
  padding: var(--spacing);
  justify-content: center;
  flex-flow: row wrap;
}

.genomic-number {
  border: 3px solid var(--primary);
  border-radius: 20px;
  text-align: center;
  padding: var(--spacing);
  width: clamp(200px, 20%, 500px);
}

.genomic-number .number {
  color: var(--primary);
  font-size: 50px;
}
</style>
