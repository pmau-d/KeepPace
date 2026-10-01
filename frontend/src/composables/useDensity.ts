import { computed, ref } from 'vue'

const STORAGE_KEY = 'keepPaceCompact'

function initial(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  } catch {
    return false
  }
}

const compact = ref(initial())

/** Mode compact de la liste : lignes plus serrées, sans description. Mémorisé par navigateur. */
export function useDensity() {
  function toggle() {
    compact.value = !compact.value
    try {
      localStorage.setItem(STORAGE_KEY, String(compact.value))
    } catch {
      // Stockage indisponible (navigation privée) : réglage non mémorisé.
    }
  }
  return { compact: computed(() => compact.value), toggle }
}
