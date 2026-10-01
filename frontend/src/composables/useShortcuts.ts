import { onBeforeUnmount, onMounted } from 'vue'

export interface Shortcut {
  /** Touches dans l'ordre : ['g', 't'] pour « g puis t ». */
  keys: string[]
  /** Accepte Ctrl ou ⌘ (palette). */
  mod?: boolean
  run: () => void
}

/** Champ de saisie actif : les raccourcis à une lettre ne doivent pas s'y déclencher. */
export function isTyping(target: EventTarget | null): boolean {
  const el = target as HTMLElement | null
  if (!el) return false
  return el.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName)
}

/** Une boîte de dialogue est ouverte : on la laisse gérer le clavier. */
function dialogOpen(): boolean {
  return Boolean(document.querySelector('[aria-modal="true"]'))
}

const SEQUENCE_DELAY = 1200

export function useShortcuts(shortcuts: () => Shortcut[]) {
  let pending: string | null = null
  let timer: ReturnType<typeof setTimeout> | undefined

  function onKeydown(event: KeyboardEvent) {
    if (event.defaultPrevented || event.altKey) return
    const key = event.key.toLowerCase()
    const mod = event.ctrlKey || event.metaKey
    const list = shortcuts()

    if (mod) {
      const match = list.find((s) => s.mod && s.keys[0] === key)
      if (match) {
        event.preventDefault()
        match.run()
      }
      return
    }
    if (isTyping(event.target) || dialogOpen()) return

    if (pending) {
      const match = list.find(
        (s) => !s.mod && s.keys.length === 2 && s.keys[0] === pending && s.keys[1] === key,
      )
      pending = null
      clearTimeout(timer)
      if (match) {
        event.preventDefault()
        match.run()
        return
      }
    }
    if (list.some((s) => !s.mod && s.keys.length === 2 && s.keys[0] === key)) {
      pending = key
      timer = setTimeout(() => (pending = null), SEQUENCE_DELAY)
      return
    }
    const single = list.find((s) => !s.mod && s.keys.length === 1 && s.keys[0] === event.key)
    if (single) {
      event.preventDefault()
      single.run()
    }
  }

  onMounted(() => window.addEventListener('keydown', onKeydown))
  onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKeydown)
    clearTimeout(timer)
  })
}
