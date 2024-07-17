<template>
  <section class="genomic-numbers" v-if="genomicData">
    <div class="genomic-number">
      <div class="number">{{ genomicData.genomic.actionable_aberrations[0] }}</div>
      <div class="name">{{ genomicData.genomic.actionable_aberrations[1] }}</div>
      <div class="genes">
        <a v-if="actionableGenes.length" class="gene-link" v-for="gene in actionableGenes" :href="'#' + gene">
          {{ gene }}
        </a>
      </div>
    </div>

    <div class="genomic-number">
      <div class="number">{{ genomicData.genomic.putative_functionally_relevant_variants[0] }}</div>
      <div class="name">{{ genomicData.genomic.putative_functionally_relevant_variants[1] }}</div>
      <div class="genes">
        <a v-if="putativelyActionableGenes.length" class="gene-link" v-for="gene in putativelyActionableGenes" :href="'#' + gene">
          {{ gene }}
        </a>
      </div>
    </div>

    <div class="genomic-number">
      <div class="number">{{ genomicData.genomic.other_variants[0] }}</div>
      <div class="name">{{ genomicData.genomic.other_variants[1] }}</div>
      <div class="genes">
        <a v-if="otherGenes.length" class="gene-link" v-for="gene in otherGenes" :href="'#' + gene">
          {{ gene }}
        </a>
      </div>
    </div>
  </section>

  <section class="genomic-summaries">
    <div class="drugs-summary">
      <span class="summary-label">Associated drugs :</span>
      <span v-if="aggregateActionableDrugs().length" class="drug" v-for="gene in aggregateActionableDrugs()">{{ gene }}</span>
      <span v-else>None</span>
    </div>
  </section>

  <section class="samples-summary" v-if="genomicData?.samples_info.row.length">
    <table class="samples-table">
      <thead>
        <tr>
          <th>Sample</th>
          <th>Tumor fraction</th>
          <th>Ploidy</th>
          <th>Tumor site</th>
          <th>Sample time</th>
          <th>Sample type</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in genomicData.samples_info.row">
          <td>{{ row.sample }}</td>
          <td>{{ row.purity }}</td>
          <td>{{ row.ploidy }}</td>
          <td>{{ row.tumor_site }}</td>
          <td>{{ row.sample_time }}</td>
          <td>{{ row.sample_type }}</td>
        </tr>
      </tbody>
    </table>
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

        <details class="alteration-section" v-for="alteration in geneData.alterations">
          <summary class="alteration-header">
            <h3>
              Alteration -
              <span class="alteration-name">{{ alteration.name }}</span>
            </h3>
          </summary>

          <div class="alteration-data">
            <p class="alteration-drugs">
              Associated drugs -
              <span v-if="alteration.reported_sensitivity !== 'None'">
                {{ formatDrugs(alteration.reported_sensitivity).effect }} :
              </span>
              <span
                v-if="alteration.reported_sensitivity !== 'None'" class="drug"
                v-for="drug in formatDrugs(alteration.reported_sensitivity).drugList">
                {{ drug }}
              </span>
              <span v-else>None</span>
            </p>
            <p>
            <ul>
              <li v-for="sentence in listifyText(alteration.description)">
                <span v-html="linkifyText(sentence)"></span>
              </li>
            </ul>
            </p>
            <table class="alteration-table">
              <thead>
                <tr>
                  <th v-for="column in Object.keys(alteration.row[0])">
                    {{ column }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in alteration.row">
                  <td v-for="(value, column) in row" :class="{ 'highlight-cell': highlightCell(column, row) }">
                    {{ value }}
                  </td>
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
import { AlterationSampleData, GenomicData } from '../models/GenomicData'

const props = defineProps<{
  patient: Patient
}>()

const genomicData = ref<GenomicData>()
const genomicGroups = computed(() => {
  return Object.keys(genomicData.value?.genomic || {}) as Array<keyof GenomicData['genomic']>
})
const actionableGroups = computed(() => {
  return genomicGroups.value.filter((group) => {
    return group !== "other_variants"
  })
})

const actionableGenes = computed(() => {
  if (!genomicData.value) return []
  return Object.keys(genomicData.value?.actionable_aberrations)
})

const putativelyActionableGenes = computed(() => {
  if (!genomicData.value) return []
  return Object.keys(genomicData.value?.putative_functionally_relevant_variants)
})

const otherGenes = computed(() => {
  if (!genomicData.value) return []
  return Object.keys(genomicData.value?.other_variants)
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
 * Lists all the drugs involved in the current genomic data.
 * @returns The list of drugs
 */
function aggregateActionableDrugs(): string[] {
  const allDrugs = actionableGroups.value.reduce<string[]>((list, group) => {
    if (!genomicData.value?.[group]) return list

    let drugs: string[] = []

    Object.values(genomicData.value?.[group]).forEach(geneData => {
      geneData.alterations.forEach(alteration => {
        const drugList = alteration.reported_sensitivity
          .replace('Responsive:', '')
          .replace('Resistant:', '')
          .trim()
          .split(' ')

        drugs = drugs.concat(drugList)
      })
    })

    return list.concat(drugs)
  }, [])
    .filter(drug => { return drug !== "None" })

  // Make all drugs unique by using a set and
  // turning it back to an array
  return [...new Set(allDrugs)].sort()
}

function formatDrugs(drugs: string) {
  const [effect, drugsString] = drugs.split(':')
  const drugList = drugsString?.trim().split(" ")

  return {
    effect,
    drugList
  }
}

function listifyText(text: string): any {
  return text.match(/(.+?\.\s*)/g)
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

function highlightCell(column: string, row: AlterationSampleData): boolean {
  return (column === 'nMinor' || column === 'nMajor') && MajorMinorNot11(row)
}

function MajorMinorNot11(row: AlterationSampleData): boolean {
  if (row.nMajor === '1' && row.nMinor === '1') return false
  if (row.nMajor === 'NA' || row.nMinor === 'NA') return false
  return true
}
</script>

<style scoped>
table {
  border-collapse: collapse;
  width: 100%;
}

table th {
  background-color: var(--grey-light);
  padding: calc(var(--spacing) / 2);
  text-align: start;
  text-wrap: wrap;
}

table td {
  padding: calc(var(--spacing) / 2);
  text-wrap: wrap;
}

table tbody tr:hover {
  background-color: var(--primary-light);
}

.genomic-numbers {
  display: flex;
  gap: var(--spacing);
  padding: var(--spacing);
  justify-content: center;
  flex-flow: row wrap;
}

.genomic-number {
  display: flex;
  flex-flow: column wrap;
  gap: 12px;
  border: 3px solid var(--primary);
  border-radius: 20px;
  text-align: center;
  padding: var(--spacing) 0;
  width: clamp(300px, 20%, 500px);
}

.genomic-number .number {
  color: var(--primary);
  font-size: 50px;
}

.genomic-number .genes {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.genomic-number .genes .gene-link {
  border: 1px solid var(--primary);
  border-radius: 20px;
  padding: 0 8px;
}

.genomic-summaries {
  padding: var(--spacing);
  display: flex;
  flex-flow: column wrap;
  gap: var(--spacing);
  align-items: center;
}

.drugs-summary {
  display: flex;
  flex-flow: row wrap;
  gap: calc(var(--spacing) / 2);
  justify-content: center;
  align-items: center;
}

.drug {
  border: 1px solid var(--black-translucent);
  border-radius: 18px;
  padding: 4px 8px;
}

.samples-summary {
  margin: var(--spacing);
  display: flex;
  justify-content: center;
}

.samples-table {
  width: min(1200px, 100%);
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

.gene-section {
  padding-bottom: var(--spacing);
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

.alteration-drugs {
  display: flex;
  flex-flow: row wrap;
  font-weight: bold;
  align-items: center;
  gap: 6px;
}

.alteration-data {
  display: flex;
  flex-flow: column wrap
}

.alteration-data p {
  margin-top: 0;
}

.alteration-table {
  align-self: center;
  width: min(1500px, 100%);
}

.highlight-cell {
  color: orangered;
}
</style>
