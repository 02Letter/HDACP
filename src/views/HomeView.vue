<script setup>
import { RouterLink } from 'vue-router'
import MemberAvatar from '@/components/MemberAvatar.vue'
import HeroAmbient from '@/components/HeroAmbient.vue'
import newsData from '@/data/news.json'
import researchData from '@/data/research.json'
import papersData from '@/data/publications.json'
import teamData from '@/data/team.json'

const baseUrl = import.meta.env.BASE_URL
const teachers = teamData.teachers
const latestNews = [...newsData.news].sort((a, b) => Number(b.date) - Number(a.date)).slice(0, 5)
const latestPapers = [...papersData].sort((a, b) => Number(b.year) - Number(a.year))
  .flatMap(group => group.items.map(paper => ({ ...paper, year: group.year }))).slice(0, 5)
const paperTitle = content => content.replace(/<[^>]*>/g, '').replace(/^\[.*?\]\s*/, '')
const paperVenue = content => content.match(/^\[(.*?)\]/)?.[1] || ''
const newsLink = link => /^https?:\/\//.test(link) ? link : baseUrl + link
</script>

<template>
  <div class="home-view">
    <section class="lab-hero" aria-labelledby="lab-title">
      <HeroAmbient />
      <div class="hero-content container">
        <h1 id="lab-title">HDACP Lab</h1>
        <p class="hero-lead"><strong>青海大学高性能与云计算研究所</strong>致力于<span>高性能计算</span>、<span>云计算与大数据</span>及<span>人工智能</span>等前沿技术的研究与应用。</p>
        <p class="hero-description">探索高效计算，连接智能未来。<br class="mobile-break" />以理论创新与工程实践推动科研发展。</p>
        <div class="hero-actions"><RouterLink to="/research">了解我们的研究 <span aria-hidden="true">→</span></RouterLink><RouterLink to="/contact" class="hero-secondary">加入我们</RouterLink></div>
      </div>
    </section>

    <section class="home-section" aria-labelledby="research-heading">
      <div class="container">
        <div class="home-heading" v-reveal><h2 id="research-heading">研究方向</h2><p>面向高效、智能与可持续的计算系统</p></div>
        <div class="research-summary">
          <article v-for="(direction, index) in researchData.directions" :key="direction.id" v-reveal="index % 2">
            <h3><RouterLink :to="'/research/' + direction.id">{{ direction.name }}</RouterLink></h3>
            <p>{{ direction.description }}</p>
          </article>
        </div>
        <div class="section-action" v-reveal><RouterLink to="/research" class="btn btn-primary">查看研究方向详情</RouterLink></div>
      </div>
    </section>

    <section class="home-section section-muted" aria-labelledby="team-heading">
      <div class="container">
        <div class="home-heading" v-reveal><h2 id="team-heading">团队成员</h2><p>师资队伍</p></div>
        <p class="section-intro">汇聚多领域科研力量，注重理论与实践结合，培养高素质的计算机专业人才。</p>
        <div class="home-team-grid">
          <article v-for="(teacher, index) in teachers" :key="teacher.id" class="home-person" v-reveal="index % 4">
            <RouterLink :to="'/teacher/' + teacher.id" :aria-label="'查看' + teacher.name + '的个人主页'"><MemberAvatar :src="baseUrl + 'people/teacher/' + teacher.photo" :name="teacher.name" /></RouterLink>
            <h3><RouterLink :to="'/teacher/' + teacher.id">{{ teacher.name }}</RouterLink></h3>
            <p class="person-role">{{ teacher.title }}</p>
            <p v-if="teacher.research" class="person-research">{{ teacher.research }}</p>
            <a v-if="teacher.email" :href="'mailto:' + teacher.email" class="person-contact" :aria-label="'联系' + teacher.name"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 6 9 7 9-7" /></svg></a>
          </article>
        </div>
        <div class="section-action" v-reveal><RouterLink to="/team" class="text-link">认识完整团队 <span aria-hidden="true">→</span></RouterLink></div>
      </div>
    </section>

    <section class="home-section" aria-labelledby="papers-heading">
      <div class="container">
        <div class="home-heading" v-reveal><h2 id="papers-heading">最新论文</h2><p>我们的近期研究成果</p></div>
        <div class="home-publications">
          <article v-for="(paper, index) in latestPapers" :key="paper.year + '-' + index" class="citation" v-reveal>
            <div class="citation-main"><span class="citation-year">{{ paper.year }}</span><a v-if="paper.link" :href="paper.link" target="_blank" rel="noopener noreferrer">{{ paperTitle(paper.content) }}</a><span v-else>{{ paperTitle(paper.content) }}</span><span v-if="paperVenue(paper.content)" class="venue-tag">{{ paperVenue(paper.content) }}</span></div>
            <a v-if="paper.link" :href="paper.link" target="_blank" rel="noopener noreferrer" class="publication-source">源文档 <span aria-hidden="true">↗</span></a>
          </article>
        </div>
        <div class="section-action" v-reveal><RouterLink to="/papers" class="text-link">查看全部论文 <span aria-hidden="true">→</span></RouterLink></div>
      </div>
    </section>

    <section class="home-section section-muted" aria-labelledby="news-heading">
      <div class="container">
        <div class="home-heading" v-reveal><h2 id="news-heading">最新动态</h2><p>实验室新闻与学术交流</p></div>
        <div class="home-news">
          <article v-for="item in latestNews" :key="item.id" class="home-news-item" v-reveal>
            <time>{{ item.date }}</time><div><h3><a v-if="item.link" :href="newsLink(item.link)" target="_blank" rel="noopener noreferrer">{{ item.title }}</a><span v-else>{{ item.title }}</span></h3><a v-if="item.link" :href="newsLink(item.link)" target="_blank" rel="noopener noreferrer" class="text-link">阅读全文 <span aria-hidden="true">→</span></a></div>
          </article>
        </div>
        <div class="section-action" v-reveal><RouterLink to="/news" class="text-link">查看全部动态 <span aria-hidden="true">→</span></RouterLink></div>
      </div>
    </section>
  </div>
</template>
