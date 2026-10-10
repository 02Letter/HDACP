<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import YearPicker from '@/components/YearPicker.vue'
import projectsData from '@/data/projects.json'

const route = useRoute()
const router = useRouter()
const projectYears = project => {
  const years = project.period.match(/\d{4}/g)?.map(Number) || []
  if (!years.length) return []
  return Array.from({ length: (years[1] || years[0]) - years[0] + 1 }, (_, i) => years[0] + i)
}
const years = [...new Set(projectsData.projects.flatMap(projectYears))].sort((a, b) => b - a)
const selectedYear = computed(() => years.includes(Number(route.query.year)) ? Number(route.query.year) : years[0])
const projects = computed(() => projectsData.projects.filter(project => projectYears(project).includes(selectedYear.value)))
const yearOptions = years.map(year => ({ value: String(year), count: projectsData.projects.filter(p => projectYears(p).includes(year)).length }))
const selectYear = year => router.replace({ query: { ...route.query, year } })
</script>

<template>
  <div class="projects-page">
    <div class="container">
      <div class="section-title" v-reveal>
        <h1>科研项目</h1>
      </div>
      
      <YearPicker :options="yearOptions" :model-value="String(selectedYear)" @update:model-value="selectYear" label="选择项目执行年份" unit="项" />
      <div class="project-year-summary" aria-live="polite"><h2>{{ selectedYear }} 年</h2><p>{{ projects.length }} 项项目 · 跨年项目按执行期间筛选</p></div>
      <div class="projects-table-wrap">
        <table class="projects-table">
          <thead>
            <tr>
              <th class="col-period">时间</th>
              <th class="col-title">项目名称</th>
              <th class="col-funding">资助基金</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="project in projects" :key="project.id">
              <td class="col-period">{{ project.period }}</td>
              <td class="col-title">{{ project.title }}</td>
              <td class="col-funding">
                <span class="funding-badge" :class="getFundingClass(project.funding)">
                  {{ project.funding }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    getFundingClass(funding) {
      if (funding.includes('国家自然科学基金')) return 'national'
      if (funding.includes('国家重点实验室')) return 'key-lab'
      if (funding.includes('青海省')) return 'provincial'
      if (funding.includes('横向')) return 'horizontal'
      return 'other'
    }
  }
}
</script>

<style scoped>
.project-year-summary { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 12px; margin: 28px 0 22px; }
.project-year-summary h2 { margin: 0; font-size: 1.55rem; }
.project-year-summary p { margin: 0; font-size: .9rem; color: var(--text-muted); }
</style>
