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
        <li>
          <RouterLink :to="{ name: 'HomePage' }">
            Homepage
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'PatientsPage' }">
            Patients
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'ContactPage' }">
            Contact
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'AboutPage' }">
            About
          </RouterLink>
        </li>
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

.nav-links ul {
  display: flex;
  flex-flow: row wrap;
  gap: calc(var(--spacing) * 3);
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 20px;
  font-weight: 600;
}

.nav-links ul a {
  color: var(--white);
  text-decoration-thickness: 4px;
  text-underline-offset: 5px;
}

button {
  border-radius: 20px;
  padding-left: 20px;
  padding-right: 20px;
}
</style>
