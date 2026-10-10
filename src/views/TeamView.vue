<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import teamData from '@/data/team.json'
import MemberAvatar from '@/components/MemberAvatar.vue'

const activeTab = ref('master')
const baseUrl = import.meta.env.BASE_URL
const teachers = teamData.teachers
const categories = [
  { value: 'master', label: '在读硕士生' },
  { value: 'phd', label: '在读博士' },
  { value: 'undergraduate', label: '在读本科生' },
  { value: 'graduated', label: '已毕业学生' }
]
const inCategory = (student, category) => category === 'graduated'
  ? student.status === 'graduated'
  : student.status === 'current' && student.degree === category
const selectedStudents = computed(() => teamData.students.filter(s => inCategory(s, activeTab.value)))
const selectedLabel = computed(() => categories.find(c => c.value === activeTab.value)?.label)
const count = category => teamData.students.filter(s => inCategory(s, category)).length
</script>

<template>
  <div class="team-page">
    <div class="container">
      <!-- Teachers Section -->
      <div class="section">
        <div class="section-title" v-reveal>
          <h1>师资队伍</h1>
        </div>
        <div class="teacher-grid">
          <RouterLink 
            v-for="teacher in teachers" 
            :key="teacher.id" 
            :to="`/teacher/${teacher.id}`"
            class="teacher-card"
          >
            <MemberAvatar class="teacher-photo" :src="`${baseUrl}people/teacher/${teacher.photo}`" :name="teacher.name" />
            <div class="teacher-info">
              <h4 class="teacher-name">{{ teacher.name }}</h4>
              <p class="teacher-title">{{ teacher.title }}</p>
            </div>
          </RouterLink>
        </div>
      </div>
      
      <!-- Students Section -->
      <div class="section">
        <div class="section-title" v-reveal>
          <h3>学生团队</h3>
        </div>
        
        <div class="tabs student-filters" role="group" aria-label="学生类别">
          <button v-for="category in categories" :key="category.value" type="button"
            :class="{ active: activeTab === category.value }" :aria-pressed="activeTab === category.value"
            @click="activeTab = category.value">
            {{ category.label }} <span class="student-count">{{ count(category.value) }}</span>
          </button>
        </div>
        <p class="sr-only" aria-live="polite">{{ selectedLabel }}，{{ selectedStudents.length }} 人</p>
        <div v-if="selectedStudents.length" class="student-grid">
          <component 
            v-for="student in selectedStudents"
            :key="student.name" 
            :is="student.link ? 'a' : 'div'"
            :href="student.link || undefined"
            :target="student.link ? '_blank' : undefined"
            :rel="student.link ? 'noopener noreferrer' : undefined"
            class="student-card"
            :class="{ 'has-link': student.link }"
          >
            <MemberAvatar class="student-photo" :src="`${baseUrl}people/student/${student.photo}`" :name="student.name" />
            <div class="student-info">
              <h5 class="student-name">{{ student.name }}</h5>
              <p class="student-year">{{ student.year }}</p>
              <p class="student-research">{{ student.research }}</p>
            </div>
          </component>
        </div>
        
        <div v-else class="empty-state"><p>暂无{{ selectedLabel }}信息</p></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.student-filters { flex-wrap: wrap; gap: 8px; }
.student-filters button { white-space: nowrap; }
.student-count { margin-left: 6px; font-size: .8rem; opacity: .7; }
</style>
