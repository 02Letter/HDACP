<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppNavbar from './AppNavbar.vue'
import SiteSearch from './SiteSearch.vue'
const searchOpen = ref(false)
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
      <RouterLink to="/" class="site-brand" aria-label="HDACP 实验室首页">
        <svg class="brand-mark" viewBox="0 0 44 44" fill="none" aria-hidden="true">
          <rect x="7" y="7" width="30" height="30" rx="7" stroke="currentColor" stroke-width="2.5" />
          <path d="M15 14v16m14-16v16M15 22h14M1 16h6M1 28h6M37 16h6M37 28h6M16 1v6M28 1v6M16 37v6M28 37v6" stroke="currentColor" stroke-width="2.5" />
        </svg>
        <span class="brand-copy"><strong>HDACP<span> Lab</span></strong><small>青海大学 · 高性能与云计算研究所</small></span>
      </RouterLink>
      <AppNavbar />
      <button class="search-toggle" aria-label="搜索网站" @click="searchOpen = true">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" /></svg>
      </button>
    </div>
  </header>
  <SiteSearch v-model="searchOpen" />
</template>
