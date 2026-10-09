<script setup>
import { ref } from 'vue'
import lifeData from '@/data/life.json'

const activeTab = ref('academic')
const baseUrl = import.meta.env.BASE_URL

const tabs = [
  { id: 'academic', name: '学术交流' },
  { id: 'honors', name: '奖励荣誉' },
  { id: 'competitions', name: '科技竞赛' }
]
</script>

<template>
  <div class="life-page">
    <div class="container">
      <div class="section-title" v-reveal>
        <h1>科研成果</h1>
      </div>
      
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- Academic Exchange -->
      <div v-if="activeTab === 'academic'" class="tab-content fade-in">
        <div v-for="(event, index) in lifeData.academic" :key="index" class="event-section">
          <h4 class="event-title">{{ event.event }}</h4>
          <div class="gallery-grid">
            <div v-for="(img, idx) in event.images" :key="idx" class="gallery-item">
              <img :src="`${baseUrl}images/life/academic/${img}`" :alt="event.event" loading="lazy" />
            </div>
          </div>
        </div>
      </div>

      <!-- Honors -->
      <div v-if="activeTab === 'honors'" class="tab-content fade-in">
        <div v-for="(category, index) in lifeData.honors" :key="index" class="honor-section">
          <h4 class="category-title">{{ category.category }}</h4>
          <div class="gallery-grid">
            <div v-for="(img, idx) in category.images" :key="idx" class="gallery-item honor-item">
              <img :src="`${baseUrl}images/life/honors/${img}`" :alt="category.category" loading="lazy" />
            </div>
          </div>
        </div>
      </div>

      <!-- Competitions -->
      <div v-if="activeTab === 'competitions'" class="tab-content fade-in">
        <div class="competitions-grid">
          <a 
            v-for="(comp, index) in lifeData.competitions" 
            :key="index" 
            :href="comp.link" 
            target="_blank" 
            rel="noopener noreferrer"
            class="competition-card"
          >
            <div class="comp-logo">
              <img :src="`${baseUrl}images/life/competitions/${comp.logo}`" :alt="comp.name" loading="lazy" />
            </div>
          </a>
        </div>
      </div>

    </div>
  </div>
</template>
