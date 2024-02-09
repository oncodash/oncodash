<template>
  <section class="genomic-numbers">
    <div class="genomic-number" v-for="genomicNumber in genomicData.genomic">
      <div class="number">{{ genomicNumber[0] }}</div>
      <div class="name">{{ genomicNumber[1] }}</div>
    </div>
  </section>

  <section class="genomic-data">
    <details class="genomic-group" v-for="(data, genomicGroup) in genomicData.genomic">
      <summary class="genomic-header">
        <h1 class="genomic-title">
          {{ genomicData.genomic[genomicGroup][1] }} -
          <span class="number">{{ genomicData.genomic[genomicGroup][0] }}</span>
        </h1>
      </summary>

      <section
        class="gene-section"
        v-for="(geneData, geneName) in genomicData[genomicGroup]">
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
                  <th>SAMPLES IDS</th>
                  <th>SAMPLES INFO</th>
                  <th>TREATMENT PHASE</th>
                  <th>TUMOR PURITY</th>
                  <th>MUTATION AFFECTS</th>
                  <th>REPORTED SENSITIVITY RESPONSE</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in alteration.row">
                  <td>{{ row.samples_ids }}</td>
                  <td>{{ row.samples_info }}</td>
                  <td>{{ row.treatment_phase }}</td>
                  <td>{{ row.tumor_purity }}</td>
                  <td>{{ row.mutation_affects }}</td>
                  <td>{{ displaySensitivity(row.reported_sensitivity) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </details>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '../api'
import { PatientID } from '../models/Patient'

const props = defineProps<{
  patientID: PatientID
}>()

onMounted(() => {
  api.getPatientGenomic(props.patientID)
    .then(async response => {
      genomicData.value = response.data
    }).catch(err => {
      alert(err.message)
      console.error(err)
    })
})

const genomicData: any = ref({})

function displaySensitivity(value: string): string {
  return value.replaceAll(';', ', ')
}
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

.genomic-group {
  padding-bottom: var(--spacing);
}

.genomic-header {
  background-color: var(--green-light);
  color: var(--black);
  cursor: pointer;
  padding: calc(var(--spacing) / 2) var(--spacing);

  &:hover {
    color: var(--primary);
  }
}

.genomic-title {
  display: inline;
  color: inherit;
  font-size: 25px;
  margin: 0;
  text-align: start;
}

.genomic-title .number {
  color: var(--primary);
}

.genomic-group,
.gene-section,
.alteration-section,
.alteration-data {
  padding-left: var(--spacing);
}

.genomic-group {
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
