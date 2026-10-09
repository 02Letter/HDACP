<script setup>
import { ref, watch } from 'vue'
const props = defineProps({ src: { type: String, required: true }, name: { type: String, required: true } })
const failed = ref(false)
watch(() => props.src, () => { failed.value = false })
</script>

<template>
  <span class="member-avatar">
    <img v-if="!failed" :src="src" :alt="name" loading="lazy" @error="failed = true" />
    <span v-else class="avatar-initials" :aria-label="name">{{ name.slice(-2) }}</span>
  </span>
</template>
