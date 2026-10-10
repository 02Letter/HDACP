<script setup>
import { computed } from 'vue'
import { papersData as publicationsData } from '@/data/content.js'

const baseUrl = import.meta.env.BASE_URL

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
                <span v-if="item.displayVenue" class="venue-tag" :title="item.venue || item.displayVenue">{{ item.displayVenue }}</span>
                <span class="paper-text">{{ item.displayTitle }}</span>
                <a v-if="item.link" :href="/^https?:\/\//.test(item.link) ? item.link : `${baseUrl}${item.link}`" target="_blank" rel="noopener noreferrer" class="paper-link">
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
