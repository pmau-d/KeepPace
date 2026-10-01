<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-60 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="import-absences-title"
      @keydown.esc="$emit('close')"
    >
      <div class="absolute inset-0 bg-black/50 backdrop-blur-xs" @click="$emit('close')"></div>
      <div
        class="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden"
      >
        <div
          class="flex items-start justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700"
        >
          <div>
            <h2 id="import-absences-title" class="text-base font-semibold text-slate-800 dark:text-slate-100">
              Importer des absences
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">
              Depuis un calendrier exporté (.ics) : congés, absences partagées par vos clients…
            </p>
          </div>
          <button
            type="button"
            class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400"
            aria-label="Fermer"
            @click="$emit('close')"
          >
            <X class="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        <div class="px-6 py-5 space-y-4 overflow-y-auto">
          <label
            class="flex flex-col items-center justify-center gap-2 border-2 border-dashed border-slate-200 dark:border-slate-600 rounded-xl py-6 cursor-pointer hover:border-indigo-400 transition-colors text-sm text-slate-500 dark:text-slate-400 focus-within:ring-2 focus-within:ring-indigo-500"
          >
            <Upload class="w-6 h-6" aria-hidden="true" />
            <span>{{ fileName || 'Choisir un fichier .ics' }}</span>
            <input type="file" accept=".ics,text/calendar" class="sr-only" @change="onFile" />
          </label>

          <p v-if="error" role="alert" class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>

          <template v-if="rows.length">
            <p class="text-xs text-slate-500 dark:text-slate-400">
              {{ rows.length }} événement(s) à venir. Vérifiez le client associé à chacun ; les événements
              passés sont ignorés.
            </p>
            <ul
              class="divide-y divide-slate-100 dark:divide-slate-700 border border-slate-200 dark:border-slate-700 rounded-xl"
            >
              <li
                v-for="(row, index) in rows"
                :key="index"
                class="flex flex-wrap items-center gap-3 px-3 py-2.5"
              >
                <input
                  :id="`import-row-${index}`"
                  v-model="row.selected"
                  type="checkbox"
                  :disabled="!row.clientId"
                  class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:opacity-40"
                />
                <label :for="`import-row-${index}`" class="flex-1 min-w-48">
                  <span class="block text-sm text-slate-700 dark:text-slate-200 truncate">{{
                    row.event.summary || 'Sans titre'
                  }}</span>
                  <span class="block text-xs text-slate-400">{{ period(row.event) }}</span>
                </label>
                <BaseSelect
                  v-model="row.clientId"
                  :options="clientOptions"
                  :aria-label="`Client de l'événement ${row.event.summary}`"
                  class="w-56"
                  @change="row.selected = Boolean(row.clientId)"
                />
              </li>
            </ul>
          </template>
          <p v-else-if="parsed" class="text-sm text-slate-400">Aucun événement à venir dans ce fichier.</p>
        </div>

        <div
          class="flex items-center justify-between gap-3 px-6 py-4 border-t border-slate-200 dark:border-slate-700"
        >
          <p class="text-xs text-slate-400">
            Un client ne garde qu'une période : celle en cours, sinon la plus proche.
          </p>
          <button
            type="button"
            :disabled="!selectedCount || applying"
            class="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-sm px-4 py-2 rounded-lg"
            @click="apply"
          >
            {{ applying ? 'Import…' : `Appliquer (${selectedCount})` }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Upload, X } from '@lucide/vue'
import BaseSelect, { type SelectOption } from './ui/BaseSelect.vue'
import { useClientStore } from '../stores/clientStore'
import { useToastStore } from '../stores/toast'
import { isPast, matchClient, pickPeriod } from '../utils/absenceImport'
import { formatCompactDate, parseIsoDate } from '../utils/dates'
import { parseIcs, type CalendarEvent } from '../utils/ics'
import { fullName } from '../utils/labels'

const emit = defineEmits<{ close: []; imported: [] }>()

interface Row {
  event: CalendarEvent
  clientId: string
  selected: boolean
}

const clientStore = useClientStore()
const toast = useToastStore()
const rows = ref<Row[]>([])
const fileName = ref('')
const parsed = ref(false)
const error = ref('')
const applying = ref(false)

const clientOptions = computed<SelectOption[]>(() => [
  { value: '', label: 'Ignorer' },
  ...clientStore.clients.map((c) => ({ value: c.id, label: `${fullName(c)} · ${c.company.name}` })),
])
const selectedCount = computed(
  () => new Set(rows.value.filter((r) => r.selected).map((r) => r.clientId)).size,
)

function period(event: CalendarEvent) {
  const start = formatCompactDate(parseIsoDate(event.start)!)
  return event.start === event.end ? start : `${start} → ${formatCompactDate(parseIsoDate(event.end)!)}`
}

async function onFile(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  error.value = ''
  fileName.value = file.name
  try {
    const events = parseIcs(await file.text()).filter((e) => !isPast(e))
    rows.value = events.map((e) => {
      const client = matchClient(e, clientStore.clients)
      return { event: e, clientId: client?.id ?? '', selected: Boolean(client) }
    })
    parsed.value = true
  } catch {
    error.value = 'Ce fichier ne peut pas être lu comme un calendrier.'
  }
}

async function apply() {
  const byClient = new Map<string, CalendarEvent[]>()
  for (const row of rows.value.filter((r) => r.selected && r.clientId)) {
    byClient.set(row.clientId, [...(byClient.get(row.clientId) ?? []), row.event])
  }
  applying.value = true
  try {
    for (const [clientId, events] of byClient) {
      const chosen = pickPeriod(events)
      if (!chosen) continue
      await clientStore.updateClient(clientId, {
        absence_start_date: chosen.start,
        absence_end_date: chosen.end,
      })
    }
    toast.success(`${byClient.size} absence(s) importée(s).`)
    emit('imported')
    emit('close')
  } catch (e) {
    toast.error(e, "L'import n'a pas abouti.")
  } finally {
    applying.value = false
  }
}
</script>
