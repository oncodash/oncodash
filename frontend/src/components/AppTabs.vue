<template>
  <div>
    <div class="tabs-navigation">
      <button
        v-for="tabName in tabNames"
        @click="selectTab(tabName)"
        class="tab"
        :class="{ active: activeTab === tabName }"
        role="tab">
        {{ tabName }}
      </button>
    </div>

    <div class="tabs-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, provide, ref, useSlots } from 'vue'

const slots = useSlots()

const tabNames = computed(() => {
  return slots.default().map(tab => {
    return tab.props.name
  })
})

const activeTab = ref('')

function selectTab(tabName) {
  activeTab.value = tabName
}

provide('activeTab', activeTab)

onMounted(() => {
  selectTab(tabNames.value[0])
})
</script>

<style scoped>
.tabs-navigation {
  align-items: center;
  border-bottom: 1px solid var(--grey);
  display: flex;
  flex-flow: row wrap;
}

.tab {
  background-color: var(--white);
  border-radius: 20px 20px 0 0;
  border: 1px solid var(--grey);
  box-sizing: border-box;
  color: var(--black);
  flex-grow: 1;
  padding: var(--spacing);
  text-align: center;
}

.tab:hover {
  color: var(--primary);
}

.tab.active {
  background-color: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary);
}

.tabs-content {
  background: var(--white);
}
</style>
