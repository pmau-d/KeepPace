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

    <!-- Réponse automatique collée : les dates sont reconnues dans le texte -->
    <button
      v-if="!pasting"
      type="button"
      class="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
      @click="pasting = true"
    >
      <ClipboardPaste class="w-3.5 h-3.5" aria-hidden="true" /> Coller une réponse automatique
    </button>
    <div v-else class="space-y-2">
      <label :for="`${idPrefix}-message`" class="block text-xs text-slate-500 dark:text-slate-400">
        Message d'absence reçu
      </label>
      <textarea
        :id="`${idPrefix}-message`"
        v-model="message"
        rows="3"
        class="w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 resize-none placeholder-slate-400"
        placeholder="Ex. : Je suis absente du 3 au 17 octobre, de retour le 20…"
      ></textarea>
      <div class="flex items-center gap-3">
        <button
          type="button"
          :disabled="!message.trim()"
          class="text-xs font-medium px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white"
          @click="detect"
        >
          Reconnaître les dates
        </button>
        <p
          v-if="feedback"
          :class="['text-xs', found ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400']"
          role="status"
        >
          {{ feedback }}
        </p>
      </div>
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ClipboardPaste } from '@lucide/vue'
import DatePicker from './ui/DatePicker.vue'
import { formatCompactDate, parseIsoDate } from '../utils/dates'
import { detectAbsence } from '../utils/outOfOffice'
withDefaults(defineProps<{ start?: string; end?: string; idPrefix?: string }>(), {
  start: '',
  end: '',
  idPrefix: 'absence',
})
const emit = defineEmits<{ 'update:start': [value: string]; 'update:end': [value: string] }>()

const pasting = ref(false)
const message = ref('')
const feedback = ref('')
const found = ref(false)

function detect() {
  const absence = detectAbsence(message.value)
  found.value = absence !== null
  if (!absence) {
    feedback.value = 'Aucune date reconnue : saisissez-les ci-dessus.'
    return
  }
  emit('update:start', absence.start ?? '')
  emit('update:end', absence.end ?? '')
  const end = absence.end ? formatCompactDate(parseIsoDate(absence.end)!) : 'date inconnue'
  feedback.value = absence.start
    ? `Absence du ${formatCompactDate(parseIsoDate(absence.start)!)} au ${end}`
    : `Absence jusqu'au ${end} inclus.`
}

function clear() {
  emit('update:start', '')
  emit('update:end', '')
}
</script>
