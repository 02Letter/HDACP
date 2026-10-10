<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppNavbar from './AppNavbar.vue'
import SiteSearch from './SiteSearch.vue'
const searchOpen = ref(false)
const baseUrl = import.meta.env.BASE_URL
function skipToContent() {
  const content = document.getElementById('site-content')
  content?.focus({ preventScroll: true })
  content?.scrollIntoView({ block: 'start' })
}
</script>

<template>
  <a class="skip-link" href="#site-content" @click.prevent="skipToContent">跳转到正文</a>
  <header class="site-header">
    <div class="header-inner">
      <RouterLink to="/" class="site-brand" aria-label="绿色算力创新与应用研究团队首页">
        <img class="brand-mark" :src="`${baseUrl}team-logo.jpg`" alt="绿色算力创新与应用研究团队标志" width="56" height="56" />
        <span class="brand-copy"><strong>HDACP</strong><small>绿色算力创新与应用研究团队</small></span>
      </RouterLink>
      <AppNavbar />
      <button class="search-toggle" aria-label="搜索网站" @click="searchOpen = true">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" /></svg>
      </button>
    </div>
  </header>
  <SiteSearch v-model="searchOpen" />
</template>
