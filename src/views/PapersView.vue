<script setup>
import { computed } from 'vue'
import publicationsData from '@/data/publications.json'

// Ensure data is sorted by year descending
const papersByYear = computed(() => {
  return publicationsData.map(group => ({
    ...group,
    year: parseInt(group.year)
  })).sort((a, b) => b.year - a.year)
})
</script>

<template>
  <div class="papers-page">
    <div class="container">
      <div class="section-title" v-reveal>
        <h1>论文发表</h1>
      </div>
      
      <div class="papers-list">
        <div v-for="group in papersByYear" :key="group.year" class="year-group">
          <div class="year-label">{{ group.year }}</div>
          <div class="paper-items">
            <div v-for="(item, index) in group.items" :key="index" class="paper-item">
              <div class="paper-content">
                <span v-if="item.content.includes('[')" class="venue-tag">
                  {{ item.content.match(/\[(.*?)\]/)?.[1] || 'Paper' }}
                </span>
                <span class="paper-text" v-html="item.content.replace(/\[(.*?)\]/, '').trim()"></span>
                <a v-if="item.link" :href="item.link" target="_blank" class="paper-link">
                  [PDF]
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

