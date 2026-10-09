<script setup>
import { newsData, dateValue } from '@/data/content.js'
const baseUrl = import.meta.env.BASE_URL

const allNews = [...newsData.news, ...newsData.papers].sort((a, b) => {
  return dateValue(b.date) - dateValue(a.date)
})
</script>

<template>
  <div class="news-page">
    <div class="container">
      <div class="section-title" v-reveal>
        <h1>新闻动态</h1>
      </div>
      
      <div class="news-grid">
        <article v-for="item in allNews" :key="item.date + '-' + item.title" class="news-card">
          <time class="news-date-badge" :datetime="String(item.date).length > 4 ? item.date : undefined">
            <span class="year">{{ String(item.date).slice(0, 4) }}</span>
            <span v-if="String(item.date).length > 4" class="month-day">{{ String(item.date).slice(5) }}</span>
          </time>
          <div class="news-content">
            <h4 class="news-title">
              <a v-if="item.link" :href="/^https?:\/\//.test(item.link) ? item.link : `${baseUrl}${item.link}`" target="_blank" rel="noopener noreferrer">
                {{ item.title }}
                <span class="external-icon">↗</span>
              </a>
              <span v-else>{{ item.title }}</span>
            </h4>
            <p v-if="item.source" class="news-source">来源：{{ item.source }}</p>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<style scoped>
.news-source { margin: 0.6rem 0 0; color: var(--text-muted, #64748b); font-size: 0.85rem; }
.news-date-badge .year, .month-day { display: block; white-space: nowrap; }
.month-day { margin-top: 0.2rem; font-size: 0.8rem; }
</style>
