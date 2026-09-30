import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'keepPaceDark'

function initial() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored !== null) return stored === 'true'
  } catch {
    // Stockage indisponible (navigation privée) : préférence du système.
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

const isDark = ref(initial())

// Classe posée sur <html> : les fenêtres téléportées dans <body> en héritent.
watchEffect(() => {
  document.documentElement.classList.toggle('dark', isDark.value)
})

export function useDarkMode() {
  function toggle() {
    isDark.value = !isDark.value
    try {
      localStorage.setItem(STORAGE_KEY, String(isDark.value))
    } catch {
      // Ignoré : la préférence ne sera simplement pas mémorisée.
    }
  }
  return { isDark, toggle }
}
