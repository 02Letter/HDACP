<script setup>
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import ScrollTools from './components/ScrollTools.vue'
</script>

<template>
  <div id="app-container">
    <AppHeader />
    <main id="site-content" class="main-content" tabindex="-1">
      <router-view />
    </main>
    <AppFooter />
    <ScrollTools />
  </div>
</template>

<style>
#app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}
</style>
