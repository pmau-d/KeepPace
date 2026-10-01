<template>
  <fieldset class="space-y-2">
    <legend class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
      Absence <span class="text-slate-400 font-normal text-xs">(optionnel)</span>
    </legend>
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label :for="`${idPrefix}-start`" class="block text-xs text-slate-500 dark:text-slate-400 mb-1"
          >Du</label
        >
        <DatePicker
          :id="`${idPrefix}-start`"
          :model-value="start"
          :max="end || undefined"
          placeholder="Déjà commencée"
          @update:model-value="$emit('update:start', $event)"
        />
      </div>
      <div>
        <label :for="`${idPrefix}-end`" class="block text-xs text-slate-500 dark:text-slate-400 mb-1"
          >Au</label
        >
        <DatePicker
          :id="`${idPrefix}-end`"
          :model-value="end"
          :min="start || undefined"
          placeholder="Retour non daté"
          @update:model-value="$emit('update:end', $event)"
        />
      </div>
    </div>
    <p class="text-xs text-slate-400">
      Début vide : absence déjà commencée. Fin vide : date de retour inconnue.
      <button
        v-if="start || end"
        type="button"
        class="ml-1 text-slate-500 hover:text-red-500 underline"
        @click="clear"
      >
        Aucune absence
      </button>
    </p>
  </fieldset>
</template>

<script setup lang="ts">
import DatePicker from './ui/DatePicker.vue'
withDefaults(defineProps<{ start?: string; end?: string; idPrefix?: string }>(), {
  start: '',
  end: '',
  idPrefix: 'absence',
})
const emit = defineEmits<{ 'update:start': [value: string]; 'update:end': [value: string] }>()

function clear() {
  emit('update:start', '')
  emit('update:end', '')
}
</script>
