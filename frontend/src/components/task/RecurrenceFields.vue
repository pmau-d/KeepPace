<template>
  <div>
    <label
      :for="`${idPrefix}-recurrence`"
      class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
    >
      Répétition
    </label>
    <BaseSelect
      :id="`${idPrefix}-recurrence`"
      :model-value="recurrence"
      :options="RECURRENCE_OPTIONS"
      block
      @update:model-value="$emit('update:recurrence', $event)"
    />
    <div v-if="recurrence" class="flex items-center gap-2 mt-2 text-xs text-slate-500 dark:text-slate-400">
      <label :for="`${idPrefix}-interval`">Intervalle</label>
      <input
        :id="`${idPrefix}-interval`"
        :value="interval"
        type="number"
        min="1"
        max="365"
        inputmode="numeric"
        class="w-16 text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-indigo-500 text-center"
        @input="onInterval"
      />
      <span aria-live="polite">→ {{ recurrenceLabel(recurrence, interval)?.toLowerCase() }}</span>
    </div>
    <p v-if="recurrence" class="text-xs text-slate-400 mt-1">
      Terminer la tâche crée automatiquement la suivante.
    </p>
  </div>
</template>

<script setup lang="ts">
import BaseSelect from '../ui/BaseSelect.vue'
import { RECURRENCE_OPTIONS } from '../../utils/options'
import { recurrenceLabel } from '../../utils/labels'
import type { Recurrence } from '../../types/api'

withDefaults(defineProps<{ recurrence: Recurrence | ''; interval: number; idPrefix?: string }>(), {
  idPrefix: 'task',
})
const emit = defineEmits<{
  'update:recurrence': [value: Recurrence | '']
  'update:interval': [value: number]
}>()

function onInterval(event: Event) {
  const value = Math.round(Number((event.target as HTMLInputElement).value))
  if (Number.isFinite(value) && value >= 1 && value <= 365) emit('update:interval', value)
}
</script>
