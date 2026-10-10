<script setup>
import courseData from '@/data/courses.json'
const courses = courseData.courses
</script>

<template>
  <div class="teaching-page">
    <div class="container">
      <div class="section-title" v-reveal><h1>教学</h1><p>课程信息与教学安排</p></div>
      <div class="course-table-wrap">
        <table class="course-table">
          <caption class="sr-only">团队开设课程</caption>
          <thead><tr><th scope="col">课程编号</th><th scope="col">课程名称</th><th scope="col">任课老师</th><th scope="col">开设学期</th><th scope="col">课程资料</th></tr></thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id || course.code + course.semester">
              <td>{{ course.code }}</td><td>{{ course.name }}</td><td>{{ Array.isArray(course.teachers) ? course.teachers.join('、') : course.teacher }}</td><td>{{ course.semester }}</td>
              <td><a v-if="course.link" :href="course.link" target="_blank" rel="noopener noreferrer">查看资料 ↗</a><span v-else>—</span></td>
            </tr>
            <tr v-if="!courses.length"><td colspan="5" class="empty-courses">课程信息即将更新</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.course-table-wrap { overflow-x: auto; }
.course-table { width: 100%; border-collapse: collapse; min-width: 640px; }
.course-table th, .course-table td { text-align: left; padding: 18px 20px; border-bottom: 1px solid var(--border-color); }
.course-table th { background: var(--bg-light); color: var(--primary-dark); font-weight: 600; white-space: nowrap; }
.course-table .empty-courses { text-align: center; padding: 72px 20px; color: var(--text-muted); }
</style>
