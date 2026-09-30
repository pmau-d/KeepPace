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
        <input
          :id="`${idPrefix}-start`"
          :value="start"
          type="date"
          :max="end || undefined"
          :class="inputClass"
          @input="$emit('update:start', $event.target.value)"
        />
      </div>
      <div>
        <label :for="`${idPrefix}-end`" class="block text-xs text-slate-500 dark:text-slate-400 mb-1"
          >Au</label
        >
        <input
          :id="`${idPrefix}-end`"
          :value="end"
          type="date"
          :min="start || undefined"
          :class="inputClass"
          @input="$emit('update:end', $event.target.value)"
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

<script setup>
defineProps({
  start: { type: String, default: '' },
  end: { type: String, default: '' },
  idPrefix: { type: String, default: 'absence' },
})
const emit = defineEmits(['update:start', 'update:end'])

const inputClass =
  'w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500'

function clear() {
  emit('update:start', '')
  emit('update:end', '')
}
</script>
