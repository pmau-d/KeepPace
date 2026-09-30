<template>
  <Teleport to="body">
    <div
      v-if="state.open"
      class="fixed inset-0 z-[70] flex items-center justify-center p-4"
      role="alertdialog"
      aria-modal="true"
      :aria-labelledby="titleId"
      @keydown.esc="cancel"
    >
      <div class="absolute inset-0 bg-black/40 backdrop-blur-xs" @click="cancel"></div>
      <div class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-4">
        <h2 :id="titleId" class="text-base font-semibold text-slate-800 dark:text-slate-100">
          {{ state.title }}
        </h2>
        <p v-if="state.message" class="text-sm text-slate-500 dark:text-slate-400 whitespace-pre-line">
          {{ state.message }}
        </p>
        <div class="flex justify-end gap-2 pt-2">
          <button
            ref="cancelButton"
            class="px-4 py-2 text-sm rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
            @click="cancel"
          >
            Annuler
          </button>
          <button
            :class="[
              'px-4 py-2 text-sm rounded-lg font-medium text-white',
              state.danger ? 'bg-red-600 hover:bg-red-500' : 'bg-indigo-600 hover:bg-indigo-500',
            ]"
            @click="accept"
          >
            {{ state.confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { useConfirmDialog } from '../composables/useConfirm.js'

const { state, accept, cancel } = useConfirmDialog()
const cancelButton = ref(null)
const titleId = 'confirm-dialog-title'

// Focus sur « Annuler » : une validation par Entrée ne détruit rien par erreur.
watch(
  () => state.open,
  async (open) => {
    if (open) {
      await nextTick()
      cancelButton.value?.focus()
    }
  },
)
</script>
