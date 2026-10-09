<script setup>
import projectsData from '@/data/projects.json'

const projects = projectsData.projects
</script>

<template>
  <div class="projects-page">
    <div class="container">
      <div class="section-title" v-reveal>
        <h1>科研项目</h1>
      </div>
      
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

