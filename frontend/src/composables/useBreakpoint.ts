import { ref, onMounted, onUnmounted } from 'vue'

export function useBreakpoint() {
  const isMobile = ref(false)
  const isTablet = ref(false)

  function update() {
    isMobile.value = window.innerWidth < 640
    isTablet.value = window.innerWidth < 768
  }

  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })
  onUnmounted(() => window.removeEventListener('resize', update))

  return { isMobile, isTablet }
}
