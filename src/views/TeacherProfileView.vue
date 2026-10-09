<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import teamData from '@/data/team.json'
import MemberAvatar from '@/components/MemberAvatar.vue'

const route = useRoute()

const teacher = computed(() => {
  return teamData.teachers.find(t => t.id === route.params.id) || null
})

const baseUrl = import.meta.env.BASE_URL
</script>

<template>
  <div class="profile-page">
    <div class="container">
      <!-- Back Button -->
      <div class="back-nav">
        <RouterLink to="/team" class="back-btn">← 返回科研团队</RouterLink>
      </div>
      
      <div v-if="teacher" class="profile-content">
        <!-- Profile Header -->
        <div class="profile-header">
          <MemberAvatar class="profile-photo" :src="`${baseUrl}people/teacher/${teacher.photo}`" :name="teacher.name" />
          <div class="profile-info">
            <h1 class="profile-name">{{ teacher.name }}</h1>
            <p class="profile-title">{{ teacher.title }}</p>
            <p v-if="teacher.education" class="profile-edu">
              <span class="icon">🎓</span> {{ teacher.education }}
            </p>
            <p v-if="teacher.email" class="profile-email">
              <span class="icon">📧</span> {{ teacher.email }}
            </p>
          </div>
        </div>
        
        <!-- Details Sections -->
        <div class="profile-details">
          <!-- Academic Title -->
          <section v-if="teacher.academicTitle" class="detail-section">
            <h3>学术职称</h3>
            <p>{{ teacher.academicTitle }}</p>
          </section>
          
          <!-- Academic Service -->
          <section v-if="teacher.academicService?.length" class="detail-section">
            <h3>学术兼职</h3>
            <ul>
              <li v-for="(service, idx) in teacher.academicService" :key="idx">{{ service }}</li>
            </ul>
          </section>
          
          <!-- Research Direction -->
          <section v-if="teacher.research" class="detail-section">
            <h3>主要研究方向</h3>
            <p>{{ teacher.research }}</p>
          </section>
          
          <!-- Bio -->
          <section v-if="teacher.bio" class="detail-section">
            <h3>个人简介</h3>
            <div class="teacher-bio">
              <template v-if="Array.isArray(teacher.bio)">
                <p v-for="(para, idx) in teacher.bio" :key="idx">{{ para }}</p>
              </template>
              <p v-else>{{ teacher.bio }}</p>
            </div>
          </section>
          
          <!-- Awards -->
          <section v-if="teacher.awards?.length" class="detail-section">
            <h3>获奖情况</h3>
            <ul class="awards-list">
              <li v-for="(award, idx) in teacher.awards" :key="idx">
                <span class="award-icon">🏆</span>
                {{ award }}
              </li>
            </ul>
          </section>
          
          <!-- Projects -->
          <section v-if="teacher.projects?.length" class="detail-section">
            <h3>主持的人才及科研项目</h3>
            <div class="projects-list">
              <div v-for="(project, idx) in teacher.projects" :key="idx" class="project-item">
                <div class="project-header">
                  <span class="project-type">{{ project.name }}</span>
                  <span v-if="project.period" class="project-period">{{ project.period }}</span>
                </div>
                <p class="project-title">{{ project.title }}</p>
                <div class="project-meta">
                  <span class="project-role">{{ project.role }}</span>
                  <span v-if="project.funding" class="project-funding">{{ project.funding }}</span>
                </div>
              </div>
            </div>
          </section>

          <!-- Tech Achievements -->
          <section v-if="teacher.achievements?.length" class="detail-section">
            <h3>科技成果登记</h3>
            <ul class="achievements-list">
              <li v-for="(item, idx) in teacher.achievements" :key="idx" class="achievement-item">
                <p class="achievement-title">{{ item.name }}</p>
                <p class="achievement-desc">{{ item.desc }}</p>
              </li>
            </ul>
          </section>

          <!-- Patents -->
          <section v-if="teacher.patents?.length" class="detail-section">
            <h3>知识产权（专利/软著）</h3>
            <ul class="patents-list">
              <li v-for="(item, idx) in teacher.patents" :key="idx">{{ item }}</li>
            </ul>
          </section>

          <!-- Publications -->
          <section v-if="teacher.papers?.length" class="detail-section">
            <h3>学术论文</h3>
            <template v-if="teacher.papers[0]?.items">
              <!-- Grouped Papers -->
              <div v-for="(group, gIdx) in teacher.papers" :key="gIdx" class="paper-group">
                <h4 class="paper-year">{{ group.year }}</h4>
                <ul class="papers-list">
                  <li v-for="(paper, pIdx) in group.items" :key="pIdx" class="paper-item">
                    {{ paper }}
                  </li>
                </ul>
              </div>
            </template>
            <ul v-else class="papers-list">
              <!-- Flat List (Legacy support) -->
              <li v-for="(paper, idx) in teacher.papers" :key="idx" class="paper-item">
                {{ paper }}
              </li>
            </ul>
          </section>
        </div>
      </div>
      
      <!-- Not Found -->
      <div v-else class="not-found">
        <p>未找到该教师信息</p>
        <RouterLink to="/team" class="back-btn">返回科研团队</RouterLink>
      </div>
    </div>
  </div>
</template>
