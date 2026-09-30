<template>
  <!-- En bas au centre : ne masque ni le panneau de tâche (droite) ni le menu du compte (gauche). -->
  <div
    class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[80] flex flex-col items-center gap-2 w-96 max-w-[calc(100vw-2rem)] pointer-events-none"
    aria-live="polite"
  >
    <TransitionGroup name="toast">
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        :role="toast.type === 'error' ? 'alert' : 'status'"
        :class="[
          'pointer-events-auto w-full flex items-start gap-3 rounded-xl px-4 py-3 shadow-lg border text-sm',
          styles[toast.type] ?? styles.info,
        ]"
      >
        <span class="flex-1 leading-snug">{{ toast.message }}</span>
        <button
          v-if="toast.action"
          class="font-semibold underline underline-offset-2 shrink-0"
          @click="toastStore.runAction(toast)"
        >
          {{ toast.action.label }}
        </button>
        <button
          class="opacity-60 hover:opacity-100 shrink-0"
          aria-label="Fermer"
          @click="toastStore.dismiss(toast.id)"
        >
          ✕
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToastStore } from '../stores/toast'

const toastStore = useToastStore()

const styles = {
  success:
    'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950 dark:border-emerald-800 dark:text-emerald-100',
  error: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-950 dark:border-red-800 dark:text-red-100',
  info: 'bg-white border-slate-200 text-slate-700 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-100',
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
