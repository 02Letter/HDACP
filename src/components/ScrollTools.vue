<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const progress = ref(null)
const showTop = ref(false)
let frame = 0
let resizeObserver

function update() {
  frame = 0
  const scrollable = document.documentElement.scrollHeight - window.innerHeight
  const ratio = scrollable > 0 ? Math.min(1, Math.max(0, window.scrollY / scrollable)) : 0
  progress.value?.style.setProperty('--scroll-progress', ratio)
  showTop.value = window.scrollY > 600
}
function scheduleUpdate() {
  if (!frame) frame = window.requestAnimationFrame(update)
}
function backToTop() {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: reduced ? 'instant' : 'smooth' })
  // Restore a useful keyboard focus without interrupting the scroll.
  document.querySelector('.site-brand')?.focus({ preventScroll: true })
}
onMounted(() => {
  update()
  window.addEventListener('scroll', scheduleUpdate, { passive: true })
  window.addEventListener('resize', scheduleUpdate)
  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(scheduleUpdate)
    resizeObserver.observe(document.body)
  }
})
onUnmounted(() => {
  window.removeEventListener('scroll', scheduleUpdate)
  window.removeEventListener('resize', scheduleUpdate)
  window.cancelAnimationFrame(frame)
  resizeObserver?.disconnect()
})
</script>

<template>
  <div ref="progress" class="reading-progress" aria-hidden="true"></div>
  <Transition name="scroll-tool">
    <button v-if="showTop" class="back-to-top" aria-label="回到顶部" @click="backToTop">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 12 6-6 6 6M12 6v14" /></svg>
    </button>
  </Transition>
</template>
