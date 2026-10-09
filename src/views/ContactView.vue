<script setup>
const contactInfo = {
  address: {
    province: '青海省西宁市宁大路251号',
    building: '青海大学计算机技术与应用系111实验室'
  },
  links: [
    { name: '青海大学', url: 'https://www.qhu.edu.cn/' },
    { name: '青海大学计算机技术与应用系', url: 'https://cs.qhu.edu.cn/' },
    { name: '中国计算机学会', url: 'https://www.ccf.org.cn/' }
  ]
}

const teachers = [
  { name: '王晓英', email: 'wxy_cta@qhu.edu.cn' },
  { name: '黄建强', email: 'hjqxaly@163.com' },
  { name: '贾金芳', email: 'qhu_jf@163.com' },
  { name: '张国晶', email: 'Zhanggj@qhu.edu.cn' },
  { name: '吴利', email: 'wuli_qhu@163.com' },
  { name: '边浩东', email: 'hpc_bhd@163.com' },
  { name: '白小军', email: 'xiaojunbai2023@163.com'},
  { name: '王哲诚', email: 'zhecheng.wang@qhu.edu.cn'}

]
</script>

<template>
  <div class="contact-page">
    <div class="container">
      <div class="section-title" v-reveal>
        <h1>联系我们</h1>
      </div>
      
      <div class="contact-grid">
        <!-- Address Card -->
        <div class="contact-card address-card">
          <div class="card-icon">📍</div>
          <h4>实验室地址</h4>
          <p>{{ contactInfo.address.province }}</p>
          <p>{{ contactInfo.address.building }}</p>
        </div>
        
        <!-- QR Code Card -->
        <div class="contact-card qrcode-card">
          <div class="card-icon">📱</div>
          <h4>关注我们</h4>
          <p>扫描二维码关注青海大学计算机系公众号</p>
          <div class="qrcode-wrap">
            <img src="@/assets/images/qrcode.jpg" alt="公众号二维码" />
          </div>
        </div>
        
        <!-- Links Card -->
        <div class="contact-card links-card">
          <div class="card-icon">🔗</div>
          <h4>常用链接</h4>
          <ul class="links-list">
            <li v-for="link in contactInfo.links" :key="link.url">
              <a :href="link.url" target="_blank" rel="noopener noreferrer">
                {{ link.name }}
                <span class="arrow">→</span>
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Recruitment & Contact Table Section -->
      <div class="recruitment-section">
        <div class="row">
          <div class="col-lg-12">
            <div class="recruitment-content">
              <h4>我们组正在寻找积极进取的学生从事前沿研究项目。</h4>
              <p>非常欢迎各本科生和研究生与我们联系，可以在 <strong>科研团队</strong> 中查找 <span class="highlight">各位老师主页</span> 进一步了解信息。</p>
              <p>下面为我们组各位优秀教师的联系方式，欢迎各大学子根据兴趣联系相应老师，HDACP欢迎你们！</p>
            </div>
            
            <div class="table-responsive">
              <table class="contact-table">
                <thead>
                  <tr>
                    <th>老师</th>
                    <th>联系邮箱</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="teacher in teachers" :key="teacher.name">
                    <td>{{ teacher.name }}</td>
                    <td>{{ teacher.email }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Map Placeholder -->
      <div class="map-section">
        <div class="section-title" v-reveal>
          <h3>地理位置</h3>
        </div>
        <div class="map-placeholder">
          <div class="map-content">
            <span class="map-icon">🗺️</span>
            <p>青海大学 · 计算机技术与应用系</p>
            <p class="map-address">青海省西宁市宁大路251号</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

