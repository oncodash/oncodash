<template>
  <section class="genomic-numbers" v-if="genomicData">
    <div class="genomic-number" v-for="genomicNumber in genomicData.genomic">
      <div class="number">{{ genomicNumber[0] }}</div>
      <div class="name">{{ genomicNumber[1] }}</div>
    </div>
  </section>

  <section class="genomic-summaries">
    <div class="genes-summary">
      <span class="summary-label">Genes involved:</span>
      <a v-if="aggregateGenes().length" class="gene-link" v-for="gene in aggregateGenes()" :href="'#' + gene">{{ gene }}</a>
      <span v-else>None</span>
    </div>

    <div class="drugs-summary">
      <span class="summary-label">Drugs involved:</span>
      <span v-if="aggregateDrugs().length" class="drug" v-for="gene in aggregateDrugs()">{{ gene }}</span>
      <span v-else>None</span>
    </div>
  </section>

  <section class="genomic-data" v-if="genomicData">
    <details open class="genomic-group" v-for="(metadata, genomicGroup) in genomicData.genomic">
      <summary class="genomic-header">
        <h1 class="genomic-title">
          {{ metadata[1] }} -
          <span class="number">{{ metadata[0] }}</span>
        </h1>
      </summary>

      <details
        open
        class="gene-section"
        v-for="(geneData, geneName) in genomicData[genomicGroup]">
        <summary class="gene-header">
          <h2 :id="geneName">{{ geneName }}</h2>
        </summary>

        <p>{{ geneData.description }}</p>

        <details open class="alteration-section" v-for="alteration in geneData.alterations">
          <summary class="alteration-header">
            <h3>
              Alteration -
              <span class="alteration-name">{{ alteration.name }}</span>
            </h3>
          </summary>

          <div class="alteration-data">
            <p v-html="linkifyText(alteration.description)"></p>
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
                  <td>{{ displayDrugs(row.reported_sensitivity) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
      </details>
    </details>
  </section>
</template>

<script setup lang="ts">
import linkifyHtml from "linkify-html"
import { onMounted, ref } from 'vue'
import { computed } from '@vue/reactivity'
import api from '../api'
import { Patient } from '../models/Patient'
import { GenomicData } from '../models/GenomicData'

const props = defineProps<{
  patient: Patient
}>()

const genomicData = ref<GenomicData>()
const genomicGroups = computed(() => {
  return Object.keys(genomicData.value?.genomic || {}) as Array<keyof GenomicData['genomic']>
})

/**
 * Fetch the genomic data of the patient on component start.
 */
onMounted(() => {
  api.getPatientGenomic(props.patient.patient_id)
    .then(async response => {
      genomicData.value = response.data
    }).catch(err => {
      alert(err.message)
      console.error(err)
    })
})

/**
 * Lists all the genes involved in the current genomic data.
 * @returns The list of genes
 */
function aggregateGenes(): string[] {
  return genomicGroups.value.reduce<string[]>((list, group) => {
    const genes = Object.keys(genomicData.value?.[group] || {})
    return list.concat(genes)
  }, [])
}

/**
 * Lists all the drugs involved in the current genomic data.
 * @returns The list of drugs
 */
function aggregateDrugs(): string[] {
  const allDrugs = genomicGroups.value.reduce<string[]>((list, group) => {
    if (!genomicData.value?.[group]) return list

    let drugs: string[] = []

    Object.values(genomicData.value?.[group]).forEach(geneData => {
      geneData.alterations.forEach(alteration => {
        alteration.row.forEach((sample) => {
          drugs = drugs.concat(displayDrugs(sample.reported_sensitivity).split(', '))
        })
      })
    })

    return list.concat(drugs)
  }, [])
    .filter(drug => {
      return drug !== "None"
    })

  // Make all drugs unique by using a set and
  // turning it back to an array
  return Array.from(new Set(allDrugs)).sort()
}

/**
 * Transforms PMIDS and url in a text into html a tags
 * for proper linking.
 * @param text - The text to linkify
 * @returns The linkified text
 */
function linkifyText(text: string): string {
  // Special process for linkifying PMIDs
  const linkifiedPmids = text.replace(/\(PMID:([\s\d,]+)\)/gm, function (match: string, group: string) {
    let linkifiedMatch: string = match

    group
      .trim()
      .split(',')
      .map((pmid: string) => pmid.trim())
      .filter((pmid, i, self) => { return i == self.indexOf(pmid) }) // filter duplicates if there is some to avoid issues with the next foreach
      .forEach((pmid: string) => {
        linkifiedMatch = linkifiedMatch.replaceAll(pmid, buildPubmedLink(pmid))
      })

    return linkifiedMatch
  })

  // Use linkifyHtml for handling normal urls
  return linkifyHtml(linkifiedPmids, {
    target: '_blank'
  })
}

/**
 * Transform a PMID into an html a tag for linking.
 * @param pmid - The PMID to link
 * @returns The html a tag containing the link, as a string
 */
function buildPubmedLink(pmid: string): string {
  return `<a href="https://pubmed.ncbi.nlm.nih.gov/${pmid}" target="_blank">${pmid}</a>`
}

/**
 * Display the list of drugs in the "reported sensitivity response"
 * as a comma-separated list.
 * @param value - The initial string
 * @returns The comma-separated string
 */
function displayDrugs(value: string): string {
  return value.replaceAll(/[;\s]/g, ', ')
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

.genomic-summaries {
  padding: var(--spacing);
  display: flex;
  flex-flow: column wrap;
  gap: var(--spacing);
  align-items: center;
}

.genes-summary,
.drugs-summary {
  display: flex;
  flex-flow: row wrap;
  gap: calc(var(--spacing) / 2);
  justify-content: center;
}

.summary-label {
  font-weight: bold;
}

summary {
  cursor: pointer;
  margin-bottom: var(--spacing);

  &:hover {
    color: var(--primary);
  }
}

summary h1,
summary h2,
summary h3 {
  display: inline;
}

.genomic-header {
  background-color: var(--green-light);
  color: var(--black);
  padding: calc(var(--spacing) / 2) var(--spacing);
}

.genomic-title {
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

.alteration-header {
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
