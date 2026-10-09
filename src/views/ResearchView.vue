<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import researchData from '@/data/research.json'
const route = useRoute()
const directions = researchData.directions
const baseUrl = import.meta.env.BASE_URL
const activeDirection = computed(() => directions.find(item => item.id === route.params.id))
</script>

<template>
  <div class="research-page">
    <div class="container">
      <template v-if="!route.params.id">
        <div class="section-title" v-reveal><h1>研究方向</h1><p>高性能计算、图计算、人工智能与绿色计算</p></div>
        <div class="research-directory">
          <article v-for="direction in directions" :key="direction.id" class="research-directory-item" v-reveal>
            <RouterLink :to="'/research/' + direction.id" class="research-image"><img :src="baseUrl + 'research/' + direction.icon" :alt="direction.name" loading="lazy" /></RouterLink>
            <div><h2><RouterLink :to="'/research/' + direction.id">{{ direction.name }}</RouterLink></h2><p>{{ direction.description }}</p><RouterLink :to="'/research/' + direction.id" class="text-link">了解研究方向 →</RouterLink></div>
          </article>
        </div>
      </template>
      <template v-else-if="activeDirection">
        <div class="back-nav"><RouterLink to="/research" class="text-link">← 全部研究方向</RouterLink></div>
        <div class="research-layout">
          <aside class="sidebar"><nav class="sidebar-nav" aria-label="研究方向"><RouterLink v-for="item in directions" :key="item.id" :to="'/research/' + item.id" class="sidebar-item" :class="{ active: item.id === route.params.id }">{{ item.name }}</RouterLink></nav></aside>
          <article class="content-card"><h1 class="content-title">{{ activeDirection.name }}</h1><p class="research-lead">{{ activeDirection.description }}</p><div class="content-body"><p v-for="(paragraph, index) in activeDirection.content.split('\n\n')" :key="index">{{ paragraph }}</p></div></article>
        </div>
      </template>
      <div v-else class="not-found"><h1>未找到该研究方向</h1><RouterLink to="/research" class="text-link">返回研究方向</RouterLink></div>
    </div>
  </div>
</template>
