<script setup>
import { ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
const route = useRoute()
const menuOpen = ref(false)
const navItems = [
  { path: '/', name: '首页' },
  { path: '/research', name: '研究方向' },
  { path: '/team', name: '团队成员' },
  { path: '/papers', name: '论文成果' },
  { path: '/projects', name: '科研项目' },
  { path: '/teaching', name: '教学' },
  { path: '/news', name: '最新动态' },
  { path: '/life', name: '学术活动' },
  { path: '/contact', name: '加入我们' }
]
watch(() => route.path, () => { menuOpen.value = false })
const isActive = path => path === '/' ? route.path === '/' : route.path.startsWith(path) || (path === '/team' && route.path.startsWith('/teacher/'))
</script>

<template>
  <nav class="site-nav" aria-label="主导航">
    <button class="menu-toggle" :aria-expanded="menuOpen" aria-controls="site-nav-links" @click="menuOpen = !menuOpen" @keydown.esc="menuOpen = false">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path :d="menuOpen ? 'M6 6l12 12M6 18 18 6' : 'M4 6h16M4 12h16M4 18h16'" /></svg>
      <span class="sr-only">{{ menuOpen ? '关闭导航' : '打开导航' }}</span>
    </button>
    <ul id="site-nav-links" class="nav-links" :class="{ 'is-open': menuOpen }">
      <li v-for="item in navItems" :key="item.path"><RouterLink :to="item.path" class="nav-link" :class="{ active: isActive(item.path) }" :aria-current="isActive(item.path) ? 'page' : undefined">{{ item.name }}</RouterLink></li>
    </ul>
  </nav>
</template>
