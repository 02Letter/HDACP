<script setup>
import { computed } from 'vue'
import YearPicker from '@/components/YearPicker.vue'
import { useRoute, useRouter } from 'vue-router'
import { papersData as publicationsData } from '@/data/content.js'

const route = useRoute()
const router = useRouter()

// Ensure data is sorted by year descending
const papersByYear = computed(() => {
  return publicationsData.map(group => ({
    ...group,
    year: parseInt(group.year)
  })).sort((a, b) => b.year - a.year)
})

const selectedGroup = computed(() => papersByYear.value.find(group => String(group.year) === route.query.year) || papersByYear.value[0])
const selectYear = year => router.replace({ query: { ...route.query, year: String(year) } })
</script>

<template>
  <div class="papers-page">
    <div class="container">
      <div class="section-title" v-reveal>
        <h1>论文发表</h1>
      </div>
      
      <div class="papers-list">
        <YearPicker :options="papersByYear.map(group => ({ value: String(group.year), count: group.items.length }))"
          :model-value="String(selectedGroup?.year)" @update:model-value="selectYear" label="选择论文年份" unit="篇" />
        <div v-if="selectedGroup" class="selected-year-heading" aria-live="polite" aria-atomic="true">
          <h2 id="selected-paper-year">{{ selectedGroup.year }} 年</h2>
          <span>{{ selectedGroup.items.length }} 篇论文</span>
        </div>
        <div v-if="selectedGroup" :key="selectedGroup.year" class="selected-year-papers" aria-labelledby="selected-paper-year">
          <div class="paper-items">
            <div v-for="(item, index) in selectedGroup.items" :key="item.id || index" class="paper-item">
              <div class="paper-content">
                <a class="paper-text" :href="item.link" target="_blank" rel="noopener noreferrer">{{ item.displayTitle }}</a>
                <span class="venue-tag" :title="item.venue">{{ item.displayVenue }}</span>
              </div>
              <div class="paper-sources">
                <a :href="item.link" target="_blank" rel="noopener noreferrer" class="publication-source">源文档 ↗</a>
                <a v-if="item.fullText" :href="item.fullText" target="_blank" rel="noopener noreferrer" class="publication-source">完整预印本 ↗</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.selected-year-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 28px 0 24px; }
.selected-year-heading h2 { margin: 0; font-size: 1.55rem; color: var(--primary-color); }
.selected-year-heading > span { color: var(--text-muted); font-size: 0.9rem; }
.paper-sources { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }
.paper-sources a { white-space: nowrap; }
@media (max-width: 600px) { .selected-year-heading { padding-top: 22px; } }
</style>
