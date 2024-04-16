<template>
  <div class="loading-overlay" v-if="apiState.isLoading">
    <span class="loader"></span>
  </div>
</template>

<script setup lang="ts">
import { useApiState } from '../apiState'

const apiState = useApiState()
</script>

<style scoped>
.loading-overlay {
  align-items: center;
  background-color: var(--black-translucent);
  bottom: 0;
  display: flex;
  justify-content: center;
  left: 0;
  position: fixed;
  right: 0;
  top: 0;
  z-index: 1;
}

.loader {
  animation: rotation 1s linear infinite;
  border-radius: 50%;
  border-right: 4px solid transparent;
  border-top: 4px solid var(--white);
  box-sizing: border-box;
  display: inline-block;
  height: 64px;
  width: 64px;
}

@keyframes rotation {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>
