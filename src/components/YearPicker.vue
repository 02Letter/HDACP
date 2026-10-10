<script setup>
defineProps({ options: { type: Array, required: true }, label: { type: String, default: '选择年份' }, unit: { type: String, default: '项' } })
const selected = defineModel({ type: String })
</script>

<template>
  <div class="year-picker" role="group" :aria-label="label">
    <button v-for="option in options" :key="option.value" type="button" class="year-option"
      :class="{ active: selected === String(option.value) }" :aria-pressed="selected === String(option.value)"
      @click="selected = String(option.value)">
      <span>{{ option.label || option.value }}</span><span class="year-count">{{ option.count }} {{ unit }}</span>
    </button>
  </div>
</template>

<style scoped>
.year-picker { display: flex; flex-wrap: wrap; gap: 10px; padding-bottom: 28px; border-bottom: 1px solid var(--border-color); }
.year-option { display: flex; align-items: center; gap: 10px; padding: 10px 16px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-light, #f8fafc); color: var(--text-secondary); font: inherit; font-size: .95rem; cursor: pointer; transition: background 160ms ease, border-color 160ms ease, color 160ms ease; }
.year-option:hover { border-color: var(--primary-color); color: var(--primary-color); }
.year-option.active { background: var(--primary-color); border-color: var(--primary-color); color: #fff; }
.year-option:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 3px; }
.year-count { font-size: .75rem; opacity: .75; white-space: nowrap; }
@media (max-width: 600px) {
  .year-picker { gap: 8px; padding-bottom: 20px; }
  .year-option { flex: 1 0 calc(33.333% - 8px); justify-content: center; gap: 8px; padding: 10px 8px; }
}
@media (prefers-reduced-motion: reduce) { .year-option { transition: none; } }
</style>
