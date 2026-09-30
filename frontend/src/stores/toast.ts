import { defineStore } from 'pinia'
import { ref } from 'vue'
import { errorMessage } from '../api/index'

export type ToastType = 'success' | 'error' | 'info'

export interface ToastAction {
  label: string
  run: () => unknown
}

export interface Toast {
  id: number
  type: ToastType
  message: string
  action: ToastAction | null
}

interface PushOptions {
  type?: ToastType
  message: string
  action?: ToastAction | null
  timeout?: number
}

type ToastOptions = Omit<PushOptions, 'type' | 'message'>

let nextId = 1

export const useToastStore = defineStore('toasts', () => {
  const toasts = ref<Toast[]>([])

  function dismiss(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function push({ type = 'info', message, action = null, timeout = action ? 8000 : 4000 }: PushOptions) {
    const id = nextId++
    toasts.value.push({ id, type, message, action })
    if (timeout > 0) setTimeout(() => dismiss(id), timeout)
    return id
  }

  const success = (message: string, options: ToastOptions = {}) =>
    push({ ...options, type: 'success', message })
  const info = (message: string, options: ToastOptions = {}) => push({ ...options, type: 'info', message })
  /** Accepte une erreur axios ou un message. */
  const error = (errorOrMessage: unknown, fallback?: string) =>
    push({
      type: 'error',
      message: typeof errorOrMessage === 'string' ? errorOrMessage : errorMessage(errorOrMessage, fallback),
      timeout: 6000,
    })

  async function runAction(toast: Toast) {
    dismiss(toast.id)
    await toast.action?.run()
  }

  return { toasts, push, success, info, error, dismiss, runAction }
})
