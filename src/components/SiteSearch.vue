<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import research from '@/data/research.json'
import team from '@/data/team.json'
import { papersData as publications, newsData as news } from '@/data/content.js'
import projects from '@/data/projects.json'

const opened = defineModel({ type: Boolean, default: false })
const dialog = ref(null)
const input = ref(null)
const query = ref('')
const router = useRouter()
const entries = [
  ...research.directions.map(item => ({ title: item.name, text: item.description, type: '研究方向', path: '/research/' + item.id })),
  ...team.teachers.map(item => ({ title: item.name, text: item.title + ' ' + (item.research || ''), type: '教师', path: '/teacher/' + item.id })),
  ...publications.flatMap(group => group.items.map(item => ({ title: item.displayTitle, text: [group.year, item.content, item.displayVenue, ...(item.authors || [])].join(' '), type: '论文', path: '/papers' }))),
  ...news.news.map(item => ({ title: item.title, text: [item.date, ...(item.members || [])].join(' '), type: '动态', path: '/news' })),
  ...projects.projects.map(item => ({ title: item.title, text: item.period + ' ' + item.funding, type: '项目', path: '/projects' }))
]
const results = computed(() => {
  const term = query.value.trim().toLocaleLowerCase()
  return term ? entries.filter(item => (item.title + ' ' + item.text).toLocaleLowerCase().includes(term)).slice(0, 30) : []
})
watch(opened, async value => {
  await nextTick()
  if (value) { query.value = ''; dialog.value.showModal(); input.value.focus() }
  else if (dialog.value.open) dialog.value.close()
})
const select = path => { opened.value = false; router.push(path) }
</script>

<template>
  <dialog ref="dialog" class="search-dialog" aria-labelledby="search-title" @close="opened = false" @cancel="opened = false" @click="event => { if (event.target === dialog) opened = false }">
    <div class="search-heading"><h2 id="search-title">搜索 HDACP</h2><button aria-label="关闭搜索" @click="opened = false">×</button></div>
    <label class="sr-only" for="site-search">搜索研究方向、成员、论文与动态</label>
    <input id="site-search" ref="input" v-model="query" type="search" placeholder="搜索研究方向、成员、论文与动态…" />
    <p v-if="!query.trim()" class="search-hint">输入关键词，查找实验室的研究与成果。</p>
    <p v-else-if="!results.length" class="search-hint" role="status">没有找到相关内容，请尝试其他关键词。</p>
    <ul v-else class="search-results" aria-label="搜索结果"><li v-for="(item, index) in results" :key="index"><button @click="select(item.path)"><small>{{ item.type }}</small><span>{{ item.title }}</span></button></li></ul>
  </dialog>
</template>
