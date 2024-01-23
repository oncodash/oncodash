<template>
  <header>
    <a href="/">
      <img
        src="/oncodash-logo.png"
        alt="The logo of Oncodash"
        height="64"
      >
    </a>
    <nav class="nav-links">
      <ul>
        <li>Homepage</li>
        <li>Patients list</li>
        <li>Contact</li>
        <li>About</li>
      </ul>
    </nav>
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

.nav-links {
  font-size: 20px;
  font-weight: 600;
}

.nav-links ul {
  display: flex;
  gap: var(--spacing);
  list-style: none;
  margin: 0;
  padding: 0;
}

button {
  border-radius: 20px;
  padding-left: 20px;
  padding-right: 20px;
}
</style>
