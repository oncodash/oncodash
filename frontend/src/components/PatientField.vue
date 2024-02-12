<template>
  <div class="data-field">
    <span class="field">{{ field }}</span>
    <span
      v-if="valueExists()"
      class="value"
      :class="{ red: isImportant() }">
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

const importantValues = [
  'No',
  'Deceased'
]

function isImportant(): boolean {
  return importantValues.includes(String(props.value))
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

.value.empty {
  color: var(--grey);
}
</style>
