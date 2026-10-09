<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const layer = ref(null)
const playing = ref(false)
let observer

onMounted(() => {
  if (!('IntersectionObserver' in window)) return
  observer = new IntersectionObserver(([entry]) => {
    playing.value = entry.isIntersecting
  })
  observer.observe(layer.value)
})
onUnmounted(() => observer?.disconnect())
</script>

<template>
  <div ref="layer" class="hero-ambient" :class="{ 'is-playing': playing }" aria-hidden="true">
    <div class="ambient-glow glow-one"></div>
    <div class="ambient-glow glow-two"></div>
    <svg class="ambient-network" viewBox="0 0 1600 850" preserveAspectRatio="xMidYMid slice" fill="none">
      <path class="network-signal signal-one" d="M0 140 90 205 35 315 162 360 78 480 230 590 170 720 310 810" />
      <path class="network-signal signal-two" d="M1600 340 1490 430 1340 380 1260 500 1380 600 1200 690 1360 840" />
      <path class="network-signal signal-three" d="M0 780 220 710 570 810 1000 720 1250 810 1600 710" />
      <g class="network-nodes"><circle cx="162" cy="360" r="8" /><circle cx="230" cy="590" r="7" /><circle cx="1380" cy="600" r="8" /><circle cx="1200" cy="690" r="7" /></g>
    </svg>
  </div>
</template>
