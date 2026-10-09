<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import teamData from '@/data/team.json'
import MemberAvatar from '@/components/MemberAvatar.vue'

const activeTab = ref('current')
const baseUrl = import.meta.env.BASE_URL

const teachers = teamData.teachers
const currentStudents = computed(() => 
  teamData.students.filter(s => s.year.includes('present'))
)

const graduatedStudents = computed(() => 
  teamData.students.filter(s => s.year.includes('毕业生'))
)
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
        
        <div class="tabs">
          <button 
            :class="{ active: activeTab === 'current' }"
            @click="activeTab = 'current'"
          >
            硕士研究生
          </button>
          <button 
            :class="{ active: activeTab === 'graduated' }"
            @click="activeTab = 'graduated'"
          >
            毕业学生
          </button>
        </div>
        
        <div v-if="activeTab === 'current'" class="student-grid">
          <component 
            v-for="student in currentStudents" 
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
        
        <div v-else-if="activeTab === 'graduated'" class="student-grid">
          <component 
            v-for="student in graduatedStudents" 
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
        
        <div v-if="activeTab === 'graduated' && graduatedStudents.length === 0" class="empty-state">
          <p>暂无毕业学生信息</p>
        </div>
      </div>
    </div>
  </div>
</template>
