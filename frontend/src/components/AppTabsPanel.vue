<template>
  <div v-show="isActive">
    <slot></slot>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  }
})

const activeTab = inject('activeTab')
const isActive = computed(() => {
  return props.name === activeTab.value
})
</script>

<style scoped></style>
