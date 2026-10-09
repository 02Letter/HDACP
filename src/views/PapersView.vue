<script setup>
import { computed } from 'vue'
import { papersData as publicationsData } from '@/data/content.js'

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
                <span v-if="item.automated && item.venue" class="venue-tag">{{ item.venue }}</span>
                <span v-else-if="!item.automated && item.content.includes('[')" class="venue-tag">
                  {{ item.content.match(/\[(.*?)\]/)?.[1] || 'Paper' }}
                </span>
                <span v-if="item.automated" class="paper-text">{{ item.title }}<span v-if="item.authors.length"> — {{ item.authors.join(', ') }}</span></span>
                <span v-else class="paper-text" v-html="item.content.replace(/\[(.*?)\]/, '').trim()"></span>
                <a v-if="item.link" :href="item.link" target="_blank" rel="noopener noreferrer" class="paper-link">
                  [来源]
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
