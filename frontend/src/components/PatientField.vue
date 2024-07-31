<template>
  <div class="data-field">
    <span class="field">{{ field }}</span>
    <span
      v-if="valueExists()"
      class="value"
      :class="{ red: isNegative(), green: isPositive() }"
    >
      {{ value }}
    </span>
    <span
      v-else
      class="value empty">
      -
    </span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  field: string,
  value: string | number | boolean | null
}>()

const negativeValues = [
  'No',
  'Deceased'
]

const positiveValues = [
  'Yes'
]

function isNegative(): boolean {
  return negativeValues.includes(String(props.value))
}

function isPositive(): boolean {
  return positiveValues.includes(String(props.value))
}

function valueExists(): boolean {
  return props.value !== ''
    && props.value !== null
    && props.value !== undefined
}
</script>

<style scoped>
.data-field {
  display: flex;
  flex-flow: row wrap;
  gap: var(--spacing);
  align-items: center;
}

.data-field:hover {
  background-color: var(--primary-light);
}

.field,
.value {
  flex: 1 1;
}

.field {
  text-align: end;
}

.value {
  color: var(--primary);
}

.value.red {
  color: var(--red);
}

.value.green {
  color: var(--green);

  &::before {
    content: "\2705";
    margin-right: 5px;
  }
}

.value.empty {
  color: var(--grey);
}
</style>
