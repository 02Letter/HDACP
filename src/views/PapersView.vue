<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { papersData as publicationsData } from '@/data/content.js'

const baseUrl = import.meta.env.BASE_URL
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
        <div class="year-picker" role="group" aria-label="选择论文年份">
          <button v-for="group in papersByYear" :key="group.year" type="button"
            class="year-option" :class="{ active: selectedGroup?.year === group.year }"
            :aria-pressed="selectedGroup?.year === group.year" @click="selectYear(group.year)">
            <span>{{ group.year }}</span><span class="year-count">{{ group.items.length }} 篇</span>
          </button>
        </div>
        <div v-if="selectedGroup" class="selected-year-heading" aria-live="polite" aria-atomic="true">
          <h2 id="selected-paper-year">{{ selectedGroup.year }} 年</h2>
          <span>{{ selectedGroup.items.length }} 篇论文</span>
        </div>
        <div v-if="selectedGroup" :key="selectedGroup.year" class="selected-year-papers" aria-labelledby="selected-paper-year">
          <div class="paper-items">
            <div v-for="(item, index) in selectedGroup.items" :key="item.id || index" class="paper-item">
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

<style scoped>
.year-picker { display: flex; flex-wrap: wrap; gap: 10px; padding-bottom: 28px; border-bottom: 1px solid var(--border-color); }
.year-option { display: flex; align-items: center; gap: 10px; padding: 10px 16px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-light, #f8fafc); color: var(--text-secondary); font: inherit; font-size: 0.95rem; cursor: pointer; transition: background 160ms ease, border-color 160ms ease, color 160ms ease; }
.year-option:hover { border-color: var(--primary-color); color: var(--primary-color); }
.year-option.active { background: var(--primary-color); border-color: var(--primary-color); color: #fff; }
.year-option:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 3px; }
.year-count { font-size: 0.75rem; opacity: 0.75; white-space: nowrap; }
.selected-year-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 28px 0 24px; }
.selected-year-heading h2 { margin: 0; font-size: 1.55rem; color: var(--primary-color); }
.selected-year-heading > span { color: var(--text-muted); font-size: 0.9rem; }
@media (max-width: 600px) {
  .year-picker { gap: 8px; padding-bottom: 20px; }
  .year-option { flex: 1 0 calc(33.333% - 8px); justify-content: center; gap: 8px; padding: 10px 8px; }
  .selected-year-heading { padding-top: 22px; }
}
@media (prefers-reduced-motion: reduce) { .year-option { transition: none; } }
</style>
