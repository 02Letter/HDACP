<script setup>
import { RouterLink } from 'vue-router'
import visits from '@/data/visits.json'
const links = [
  { name: '青海大学', url: 'https://www.qhu.edu.cn/' },
  { name: '青海大学计算机技术与应用系', url: 'https://cs.qhu.edu.cn/' },
  { name: '中国计算机学会', url: 'https://www.ccf.org.cn/' }
]
</script>

<template>
  <footer class="site-footer">
    <div class="container footer-grid">
      <div class="footer-about"><h2>HDACP</h2><p>绿色算力创新与应用研究团队</p><p class="footer-address">青海省西宁市宁大路251号<br />青海大学计算机技术与应用系111实验室</p><RouterLink to="/contact" class="text-link">联系我们 →</RouterLink></div>
      <div><h3>相关链接</h3><ul><li v-for="link in links" :key="link.url"><a :href="link.url" target="_blank" rel="noopener noreferrer">{{ link.name }} ↗</a></li><li><a href="https://github.com/02Letter/HDACP" target="_blank" rel="noopener noreferrer">GitHub ↗</a></li></ul></div>
      <div class="footer-qr"><img src="@/assets/images/qrcode.jpg" alt="青海大学计算机系公众号二维码" loading="lazy" /><p>关注青海大学计算机系</p></div>
    </div>
    <div class="footer-bottom">© {{ new Date().getFullYear() }} 绿色算力创新与应用研究团队 · HDACP<br /><span class="visit-counter">总访问量：{{ visits.count.toLocaleString('zh-CN') }}</span></div>
  </footer>
</template>
