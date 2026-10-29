<template>
  <div>
    <ul v-if="items.length" class="space-y-1" aria-label="Checklist">
      <li
        v-for="item in items"
        :key="item.id"
        class="group flex items-center gap-2.5 rounded-lg px-2 py-1.5 hover:bg-slate-50 dark:hover:bg-slate-700/40"
      >
        <input
          :id="`check-${item.id}`"
          type="checkbox"
          :checked="item.done"
          class="w-4 h-4 rounded-sm accent-indigo-600 cursor-pointer shrink-0"
          @change="$emit('toggle', item)"
        />
        <label
          :for="`check-${item.id}`"
          :class="[
            'flex-1 min-w-0 text-sm break-words cursor-pointer',
            item.done ? 'line-through text-slate-400' : 'text-slate-700 dark:text-slate-200',
          ]"
        >
          {{ item.label }}
        </label>
        <button
          type="button"
          class="p-1 rounded-sm text-slate-300 opacity-0 group-hover:opacity-100 focus:opacity-100 hover:text-red-500 transition"
          :aria-label="`Supprimer la case « ${item.label} »`"
          @click="$emit('remove', item)"
        >
          <X class="w-3.5 h-3.5" aria-hidden="true" />
        </button>
      </li>
    </ul>
    <p v-else class="text-sm text-slate-400 py-2">
      Aucune case. Ajoutez ce qu'il faut vérifier à chaque fois : elles seront décochées à chaque occurrence
      d'une tâche récurrente.
    </p>

    <div
      v-if="canFinish && allDone"
      class="mt-3 flex items-center justify-between gap-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 px-3 py-2"
      role="status"
    >
      <span class="text-sm text-green-700 dark:text-green-300">Tout est coché.</span>
      <button
        type="button"
        class="text-sm font-semibold text-green-700 dark:text-green-300 hover:underline"
        @click="$emit('finish')"
      >
        Terminer la tâche
      </button>
    </div>

    <form class="mt-3 flex gap-2" @submit.prevent="submit">
      <label :for="`${idPrefix}-new-item`" class="sr-only">Nouvelle case</label>
      <input
        :id="`${idPrefix}-new-item`"
        v-model="draft"
        type="text"
        maxlength="200"
        placeholder="Ajouter une case…"
        class="flex-1 min-w-0 text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 placeholder-slate-400"
      />
      <button
        type="submit"
        :disabled="!draft.trim()"
        class="px-3 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white transition-colors"
      >
        Ajouter
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { X } from '@lucide/vue'
import { computed, ref } from 'vue'
import type { ChecklistItem } from '../../types/api'

const props = withDefaults(
  defineProps<{
    items: ChecklistItem[]
    /** Propose « Terminer la tâche » quand tout est coché (la tâche n'est pas déjà terminée). */
    canFinish?: boolean
    idPrefix?: string
  }>(),
  { canFinish: false, idPrefix: 'checklist' },
)
const emit = defineEmits<{
  add: [label: string]
  toggle: [item: ChecklistItem]
  remove: [item: ChecklistItem]
  finish: []
}>()

const draft = ref('')
const allDone = computed(() => props.items.length > 0 && props.items.every((item) => item.done))

function submit() {
  const label = draft.value.trim()
  if (!label) return
  emit('add', label)
  draft.value = ''
}
</script>
