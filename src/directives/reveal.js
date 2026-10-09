// One observer for the entire site; elements stop being observed after entry.
const pending = new Set()
let observer
let motionPreference

function reveal(element) {
  element.classList.remove('reveal-pending')
  element.classList.add('reveal-visible')
  observer?.unobserve(element)
  pending.delete(element)
}

function initialize() {
  if (motionPreference) return
  motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
  motionPreference.addEventListener('change', event => {
    if (event.matches) [...pending].forEach(reveal)
  })
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) reveal(entry.target)
      })
    }, { rootMargin: '0px 0px -24px 0px', threshold: 0 })
  }
}

export default {
  mounted(element, binding) {
    initialize()
    if (!observer || motionPreference.matches) return
    element.classList.add('reveal-item', 'reveal-pending')
    element.style.setProperty('--reveal-delay', `${Math.min(Number(binding.value) || 0, 4) * 65}ms`)
    // Keyboard navigation should never land in invisible content.
    element.addEventListener('focusin', () => reveal(element), { once: true })
    pending.add(element)
    observer.observe(element)
  },
  unmounted(element) {
    observer?.unobserve(element)
    pending.delete(element)
  }
}
