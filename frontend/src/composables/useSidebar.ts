import { ref } from 'vue'

// Tiroir de navigation sur petit écran (la barre latérale est fixe à partir de lg).
const open = ref(false)

export function useSidebar() {
  return {
    open,
    show: () => (open.value = true),
    close: () => (open.value = false),
  }
}
