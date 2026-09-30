import { defineStore } from 'pinia'
import { ref } from 'vue'
import { errorMessage } from '../api/index.js'

let nextId = 1

export const useToastStore = defineStore('toasts', () => {
  const toasts = ref([])

  function dismiss(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  /**
   * @param {{ type?: 'success'|'error'|'info', message: string, action?: { label: string, run: Function }, timeout?: number }} toast
   */
  function push({ type = 'info', message, action = null, timeout = action ? 8000 : 4000 }) {
    const id = nextId++
    toasts.value.push({ id, type, message, action })
    if (timeout > 0) setTimeout(() => dismiss(id), timeout)
    return id
  }

  const success = (message, options = {}) => push({ ...options, type: 'success', message })
  const info = (message, options = {}) => push({ ...options, type: 'info', message })
  /** Accepte une erreur axios ou un message. */
  const error = (errorOrMessage, fallback) =>
    push({
      type: 'error',
      message: typeof errorOrMessage === 'string' ? errorOrMessage : errorMessage(errorOrMessage, fallback),
      timeout: 6000,
    })

  async function runAction(toast) {
    dismiss(toast.id)
    await toast.action?.run()
  }

  return { toasts, push, success, info, error, dismiss, runAction }
})
