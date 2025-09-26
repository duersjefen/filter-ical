import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Mobile detection composable
 * Detects mobile devices and provides reactive screen size information
 */
export function useMobileDetection() {
  const isMobile = ref(false)
  const screenWidth = ref(0)

  const updateScreenInfo = () => {
    screenWidth.value = window.innerWidth
    // Consider mobile if screen width is less than 768px (Tailwind's md breakpoint)
    isMobile.value = screenWidth.value < 768
  }

  onMounted(() => {
    updateScreenInfo()
    window.addEventListener('resize', updateScreenInfo)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateScreenInfo)
  })

  return {
    isMobile,
    screenWidth
  }
}