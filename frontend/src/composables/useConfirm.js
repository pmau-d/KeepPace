import { reactive, readonly } from 'vue'

// Boîte de confirmation unique, affichée par <ConfirmDialog /> dans App.vue.
const state = reactive({
  open: false,
  title: '',
  message: '',
  confirmLabel: 'Confirmer',
  danger: false,
})
let resolver = null

function settle(answer) {
  state.open = false
  resolver?.(answer)
  resolver = null
}

/**
 * Demande une confirmation et renvoie une promesse résolue à true ou false.
 * @param {{ title: string, message?: string, confirmLabel?: string, danger?: boolean }} options
 */
export function confirm({ title, message = '', confirmLabel = 'Confirmer', danger = false }) {
  resolver?.(false)
  Object.assign(state, { open: true, title, message, confirmLabel, danger })
  return new Promise((resolve) => {
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
