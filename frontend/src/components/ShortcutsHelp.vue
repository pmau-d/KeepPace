<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[75] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
      @keydown.esc.prevent="open = false"
    >
      <div class="absolute inset-0 bg-black/40 backdrop-blur-xs" @click="open = false"></div>
      <div
        ref="panel"
        tabindex="-1"
        class="relative w-full max-w-md bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-6 focus:outline-none"
      >
        <div class="flex items-center justify-between mb-4">
          <h2 id="shortcuts-title" class="text-base font-semibold text-slate-800 dark:text-slate-100">
            Raccourcis clavier
          </h2>
          <button
            type="button"
            class="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
            aria-label="Fermer"
            @click="open = false"
          >
            <X class="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
        <dl class="space-y-2 text-sm">
          <div v-for="row in rows" :key="row.label" class="flex items-center justify-between gap-4">
            <dt class="text-slate-600 dark:text-slate-300">{{ row.label }}</dt>
            <dd class="flex items-center gap-1">
              <template v-for="(key, i) in row.keys" :key="i">
                <span v-if="i" class="text-xs text-slate-400">puis</span>
                <kbd
                  class="text-xs min-w-6 text-center text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600 rounded-sm px-1.5 py-0.5 bg-slate-50 dark:bg-slate-700"
                  >{{ key }}</kbd
                >
              </template>
            </dd>
          </div>
        </dl>
        <p class="text-xs text-slate-400 mt-4">
          Les raccourcis à une lettre sont désactivés pendant la saisie dans un champ.
        </p>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { X } from '@lucide/vue'
import type { Command } from '../commands/index'

const props = defineProps<{ commands: Command[] }>()
const open = defineModel<boolean>('open', { required: true })
const panel = ref<HTMLElement | null>(null)

const isMac = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.platform)
const rows = computed(() => [
  { label: 'Palette de commandes', keys: [isMac ? '⌘ K' : 'Ctrl K'] },
  ...props.commands.filter((c) => c.hint).map((c) => ({ label: c.label, keys: c.hint! })),
  { label: 'Fermer un panneau ou une fenêtre', keys: ['Échap'] },
])

watch(open, async (value) => {
  if (!value) return
  await nextTick()
  panel.value?.focus()
})
</script>
