<template>
  <header>
    <a href="/">
      <img
        src="/oncodash-logo.png"
        alt="The logo of Oncodash"
        height="64"
      >
    </a>
    <button type="button">LOGIN</button>
  </header>
</template>

<script setup lang="ts"></script>

<style scoped>
header {
  color: var(--white);
  display: flex;
  align-items: center;
  flex-flow: row wrap;
  gap: var(--spacing);
  justify-content: space-between;
  padding: var(--spacing);
}

button {
  border-radius: 20px;
  padding-left: 20px;
  padding-right: 20px;
}
</style>
