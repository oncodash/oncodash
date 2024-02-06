<template>
  <section class="genomic-numbers">
    <div class="genomic-number" v-for="genomicNumber in genomicData.genomic">
      <div class="number">{{ genomicNumber[0] }}</div>
      <div class="name">{{ genomicNumber[1] }}</div>
    </div>
  </section>

  <section class="genomic-data">
    <article class="genomic-section" v-for="(data, genomicGroup) in genomicData.genomic">
      <header class="genomic-header">
        <h1 class="genomic-title">
          {{ genomicData.genomic[genomicGroup][1] }} -
          <span class="number">{{ genomicData.genomic[genomicGroup][0] }}</span>
        </h1>
      </header>

      <section class="gene-section" v-for="(geneData, geneName) in genomicData[genomicGroup]">
        <header>
          <h2>{{ geneName }}</h2>
        </header>

        <p>{{ geneData.description }}</p>

        <section class="alteration-section" v-for="alteration in geneData.alterations">
          <header>
            <h3 class="alteration-title">
              Alteration -
              <span class="alteration-name">{{ alteration.name }}</span>
            </h3>
          </header>

          <div class="alteration-data">
            <p>{{ alteration.description }}</p>
            <table class="alteration-table">
              <thead>
                <tr>
                  <th v-for="[field, header] in alterationHeaders">
                    {{ header }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in alteration.row">
                  <td v-for="[field] in alterationHeaders">
                    {{ row[field] }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../api'

const props = defineProps<{
  patientID: string
}>()

const genomicData: any = ref({})
const alterationHeaders = ref(new Map([
  ["samples_ids", "SAMPLES IDS"],
  ["samples_info", "SAMPLES INFO"],
  ["treatment_phase", "TREATMENT PHASE"],
  ["tumor_purity", "TUMOR PURITY"],
  ["mutation_affects", "MUTATION AFFECTS"],
  ["reported_sensitivity", "REPORTED SENSITIVITY RESPONSE"]
]))


function displayDrugList (value) {
  return value.replace(';', ' ')
}

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

.genomic-section {
  padding-bottom: var(--spacing);
}

.genomic-header {
  background-color: var(--green-light);
  padding: calc(var(--spacing) / 2) var(--spacing);
}

.genomic-title {
  color: var(--black);
  font-size: 25px;
  margin: 0;
  text-align: start;
}

.genomic-title .number {
  color: var(--primary);
}

.genomic-section,
.gene-section,
.alteration-section,
.alteration-data {
  padding-left: var(--spacing);
}

.genomic-section {
  padding-right: var(--spacing);
}

.alteration-title {
  background-color: var(--green-light);
  padding: calc(var(--spacing) / 2) var(--spacing);
}

.alteration-name {
  color: var(--primary);
  font-style: italic;
}

.alteration-table {
  border-collapse: collapse;
  width: 100%;
}

.alteration-table th {
  background-color: var(--grey-light);
  padding: var(--spacing);
  text-align: start;
  text-wrap: wrap;
}

.alteration-table td {
  padding: var(--spacing);
  text-wrap: wrap;
}

.alteration-table tbody tr:hover {
  background-color: var(--primary-light);
}
</style>
