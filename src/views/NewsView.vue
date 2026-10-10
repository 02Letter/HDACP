<script setup>
import newsData from '@/data/news.json'
const baseUrl = import.meta.env.BASE_URL

const allNews = [...newsData.news, ...newsData.papers].sort((a, b) => {
  return parseInt(b.date) - parseInt(a.date)
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
          <div class="news-date-badge">
            <span class="year">{{ item.date }}</span>
          </div>
          <div class="news-content">
            <h4 class="news-title">
              <a v-if="item.link" :href="/^https?:\/\//.test(item.link) ? item.link : `${baseUrl}${item.link}`" target="_blank" rel="noopener noreferrer">
                {{ item.title }}
                <span class="external-icon">↗</span>
              </a>
              <span v-else>{{ item.title }}</span>
            </h4>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>
