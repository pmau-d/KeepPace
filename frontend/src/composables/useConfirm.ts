import { reactive, readonly } from 'vue'

// Boîte de confirmation unique, affichée par <ConfirmDialog /> dans App.vue.

export interface ConfirmOptions {
  title: string
  message?: string
  confirmLabel?: string
  danger?: boolean
}

const state = reactive({
  open: false,
  title: '',
  message: '',
  confirmLabel: 'Confirmer',
  danger: false,
})
let resolver: ((answer: boolean) => void) | null = null

function settle(answer: boolean) {
  state.open = false
  resolver?.(answer)
  resolver = null
}

/** Demande une confirmation et renvoie une promesse résolue à true ou false. */
export function confirm({
  title,
  message = '',
  confirmLabel = 'Confirmer',
  danger = false,
}: ConfirmOptions): Promise<boolean> {
  resolver?.(false)
  Object.assign(state, { open: true, title, message, confirmLabel, danger })
  return new Promise<boolean>((resolve) => {
    resolver = resolve
  })
}

export function useConfirmDialog() {
  return {
    state: readonly(state),
    accept: () => settle(true),
    cancel: () => settle(false),
  }
}
