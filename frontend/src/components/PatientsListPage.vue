<template>
  <h1>PATIENTS LIST</h1>

  <section class="patients-search">
    <input
      id="patients-filter"
      v-model="patientsFilter"
      type="search"
      placeholder="Search by patient ID or stage">
  </section>

  <section class="patients-list">
    <header>
      <div class="page-summary">
        Displaying {{ pageOffset + 1 }} - {{ pageOffset + pageSize }}
        of {{ patientsList.length }}
      </div>

      <div class="pagination">
        <button
          type="button"
          @click="goToFirstPage">
          &#8810;
        </button>
        <button
          type="button"
          @click="previousPage">
          &#60;
        </button>
        <span>{{ pageNumber }} / {{ pagesCount }}</span>
        <button
          type="button"
          @click="nextPage">
          &#62;
        </button>
        <button
          type="button"
          @click="goToLastPage">
          &#8811;
        </button>
      </div>

      <div class="patients-per-page">
        <label>
          Patients per page
          <select
            name="patients-per-page"
            v-model="pageSize">
            <option :value="12">12</option>
            <option :value="24">24</option>
          </select>
        </label>
      </div>
    </header>

    <div class="patients-cards">
      <PatientCard v-for="patient in paginatedPatients" :patient="patient" />
    </div>

    <footer>
      <div class="pagination">
        <button
          type="button"
          @click="goToFirstPage">
          &#8810;
        </button>
        <button
          type="button"
          @click="previousPage">
          &#60;
        </button>
        <span>{{ pageNumber }} / {{ pagesCount }}</span>
        <button
          type="button"
          @click="nextPage">
          &#62;
        </button>
        <button
          type="button"
          @click="goToLastPage">
          &#8811;
        </button>
      </div>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PatientCard from '../components/PatientCard.vue'
import api from '../api'

const patientsList = ref<any>([])
const patientsFilter = ref<string>('')

const filteredPatients = computed(() => {
  const filter = patientsFilter.value

  return patientsList.value.filter((patient: any) => {
    return patient.patient_id.toString().includes(filter)
      || patient.stage?.toString().includes(filter)
  })
})

const pageNumber = ref<number>(1)
const pageSize = ref<number>(12)
const pageOffset = computed<number>(() => {
  return (pageNumber.value - 1) * pageSize.value
})
const pagesCount = computed(() => {
  return Math.ceil(filteredPatients.value.length / pageSize.value)
})

/**
 * Reset pagination when the page count changes
 * due to filtering.
 */
watch(pagesCount, () => {
  pageNumber.value = 1
})

const paginatedPatients = computed(() => {
  return filteredPatients.value.slice(
    pageOffset.value,
    pageOffset.value + pageSize.value
  )
})

function goToFirstPage(): void {
  pageNumber.value = 1
}

function previousPage(): void {
  if (pageNumber.value <= 1) return
  pageNumber.value -= 1
}

function nextPage(): void {
  if (pageNumber.value >= pagesCount.value) return
  pageNumber.value += 1
}

function goToLastPage(): void {
  pageNumber.value = pagesCount.value
}

onMounted(async () => {
  api.getPatientsList().then(async response => {
    patientsList.value = response.data
  }).catch(err => {
    alert(err.message)
    console.error(err)
  })
})
</script>

<style scoped>
.patients-search {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: var(--spacing);

  &::before {
    content: url("../assets/magnifying-glass-icon.svg");
    margin-right: calc(var(--spacing) / 2);
  }
}

#patients-filter {
  width: min(600px, 100%);
}

.patients-list {
  background-color: var(--white);
  padding: var(--spacing);
  display: flex;
  flex-flow: column wrap;
  gap: var(--spacing);
}

.patients-list header,
.patients-list footer {
  display: flex;
  flex-flow: row wrap;
  align-items: center;
  gap: var(--spacing);
  justify-content: space-around;
}

.patients-cards {
  display: flex;
  flex-flow: row wrap;
  gap: var(--spacing);
  justify-content: center;
}

.patients-cards>* {
  width: 300px;
}

.pagination {
  display: flex;
  align-items: center;
  gap: calc(var(--spacing) / 2);
}

.pagination button {
  font-size: 18px;
}
</style>
