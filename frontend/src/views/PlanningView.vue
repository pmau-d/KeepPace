<template>
  <header
    class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4 flex flex-wrap items-center gap-4 justify-between shrink-0"
  >
    <div>
      <h1 class="text-lg font-semibold text-slate-800 dark:text-slate-100">Planning</h1>
      <p class="text-sm text-slate-400">Absences des clients et échéances des tâches ouvertes.</p>
    </div>
    <div class="flex items-center gap-2">
      <BaseSelect v-model="weeksValue" :options="WEEK_OPTIONS" aria-label="Durée affichée" />
      <div class="flex items-center rounded-lg bg-slate-100 dark:bg-slate-700">
        <button
          type="button"
          class="p-2 rounded-l-lg text-slate-600 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600"
          aria-label="Période précédente"
          @click="shift(-1)"
        >
          <ChevronLeft class="w-4 h-4" aria-hidden="true" />
        </button>
        <button
          type="button"
          class="px-3 py-2 text-sm text-slate-600 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600"
          @click="goToday"
        >
          Aujourd'hui
        </button>
        <button
          type="button"
          class="p-2 rounded-r-lg text-slate-600 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600"
          aria-label="Période suivante"
          @click="shift(1)"
        >
          <ChevronRight class="w-4 h-4" aria-hidden="true" />
        </button>
      </div>
      <p
        class="text-sm font-medium text-slate-600 dark:text-slate-300 min-w-40 text-right"
        aria-live="polite"
      >
        {{ rangeLabel }}
      </p>
    </div>
  </header>

  <main class="flex-1 overflow-auto p-6">
    <div v-if="loading && !tasks.length" class="flex justify-center items-center h-40">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div
      v-else-if="!clientStore.clients.length"
      class="flex flex-col items-center justify-center h-64 text-slate-400 text-center"
    >
      <CalendarRange class="w-12 h-12 mb-3 opacity-60" aria-hidden="true" />
      <p class="text-lg font-medium">Aucun client pour l'instant</p>
      <p class="text-sm mt-1">Les absences et échéances de vos clients apparaîtront ici.</p>
    </div>

    <div
      v-else
      class="min-w-max bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700"
      role="table"
      :aria-label="`Planning du ${rangeLabel}`"
    >
      <!-- En-tête : un jour par colonne -->
      <div
        role="row"
        class="grid sticky top-0 z-20 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 rounded-t-xl"
        :style="gridStyle"
      >
        <div
          role="columnheader"
          class="sticky left-0 z-10 bg-white dark:bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-end"
        >
          Client
        </div>
        <div
          v-for="day in days"
          :key="day.index"
          role="columnheader"
          :aria-label="formatShortDate(day.date)"
          :class="[
            'py-1.5 text-center leading-tight border-l',
            day.isMonday || day.isFirstOfMonth
              ? 'border-slate-200 dark:border-slate-700'
              : 'border-transparent',
            day.isWeekend && 'bg-slate-50 dark:bg-slate-900/40',
            day.isToday && 'bg-indigo-50 dark:bg-indigo-900/30',
          ]"
        >
          <p class="text-[10px] font-semibold text-slate-500 dark:text-slate-400 h-3">
            {{ day.isFirstOfMonth || day.index === 0 ? monthShort(day.date) : '' }}
          </p>
          <p class="text-[10px] text-slate-400 uppercase">{{ weekdayLetter(day.date) }}</p>
          <p
            :class="[
              'text-xs font-medium',
              day.isToday
                ? 'text-white bg-indigo-600 rounded-full w-6 h-6 mx-auto flex items-center justify-center'
                : 'text-slate-600 dark:text-slate-300',
            ]"
          >
            {{ day.date.getDate() }}
          </p>
        </div>
      </div>

      <template v-for="group in groups" :key="group.companyId">
        <div role="row" class="grid" :style="gridStyle">
          <div
            role="rowheader"
            class="sticky left-0 z-10 bg-slate-50 dark:bg-slate-900/60 px-4 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider"
            :style="{ gridColumn: `1 / span ${weeks * 7 + 1}` }"
          >
            {{ group.name }}
          </div>
        </div>

        <div
          v-for="row in group.rows"
          :key="row.client.id"
          role="row"
          class="grid relative border-b border-slate-100 dark:border-slate-700/60 last:border-b-0 min-h-11"
          :style="gridStyle"
        >
          <div
            role="rowheader"
            class="sticky left-0 z-10 bg-white dark:bg-slate-800 px-4 py-2 flex items-center gap-2 min-w-0 border-r border-slate-100 dark:border-slate-700/60"
            style="grid-row: 1"
          >
            <span
              :class="['w-2 h-2 rounded-full shrink-0', presenceColor(row.client.presence_status)]"
              :title="presenceLabel(row.client.presence_status)"
            ></span>
            <span class="text-sm text-slate-700 dark:text-slate-200 truncate">{{
              fullName(row.client)
            }}</span>
            <span
              v-if="row.overdue"
              class="ml-auto text-[10px] font-medium text-red-600 dark:text-red-400 whitespace-nowrap"
              >{{ row.overdue }} en retard</span
            >
          </div>

          <!-- Fond : week-ends et aujourd'hui -->
          <div
            v-for="day in days"
            :key="day.index"
            role="cell"
            :aria-label="cellLabel(row, day.index)"
            :class="[
              'border-l',
              day.isMonday || day.isFirstOfMonth
                ? 'border-slate-200 dark:border-slate-700'
                : 'border-transparent',
              day.isWeekend && 'bg-slate-50 dark:bg-slate-900/40',
              day.isToday && 'bg-indigo-50/70 dark:bg-indigo-900/20',
            ]"
            :style="{ gridRow: 1, gridColumn: day.index + 2 }"
          ></div>

          <!-- Absence -->
          <div
            v-if="row.bar"
            class="self-center h-6 flex items-center px-2 text-[11px] font-medium text-red-700 dark:text-red-200 bg-red-100 dark:bg-red-900/40 border border-red-200 dark:border-red-800/70 overflow-hidden whitespace-nowrap pointer-events-none"
            :class="[
              row.bar.continuesBefore ? 'rounded-l-none border-l-0' : 'rounded-l-md',
              row.bar.continuesAfter ? 'rounded-r-none border-r-0' : 'rounded-r-md',
              row.bar.openEnded && 'bg-linear-to-r from-red-100 to-transparent dark:from-red-900/40',
            ]"
            :style="{ gridRow: 1, gridColumn: `${row.bar.start + 2} / span ${row.bar.span}` }"
            aria-hidden="true"
          >
            {{ row.bar.openEnded ? 'Absence · retour non daté' : 'Absence' }}
          </div>

          <!-- Échéances -->
          <button
            v-for="marker in row.markers"
            :key="marker.index"
            type="button"
            class="self-center justify-self-center z-[5] flex items-center gap-0.5 px-1 py-0.5 rounded-md bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 shadow-xs hover:border-indigo-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            :style="{ gridRow: 1, gridColumn: marker.index + 2 }"
            :title="marker.tasks.map((t) => t.title).join('\n')"
            :aria-label="`${marker.tasks.length} échéance(s) le ${formatShortDate(days[marker.index]!.date)} : ${marker.tasks.map((t) => t.title).join(', ')}`"
            @click="selectedId = marker.tasks[0]!.id"
          >
            <PriorityFlag :priority="marker.top" />
            <span
              v-if="marker.tasks.length > 1"
              class="text-[10px] font-semibold text-slate-600 dark:text-slate-300"
              >{{ marker.tasks.length }}</span
            >
          </button>
        </div>
      </template>
    </div>

    <p v-if="truncated" class="text-xs text-slate-400 mt-3">
      Seules les {{ TASK_LIMIT }} premières tâches ouvertes (par échéance) sont affichées.
    </p>
  </main>

  <TaskSlideOver v-if="selectedId" :task-id="selectedId" @close="selectedId = null" @changed="load" />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { CalendarRange, ChevronLeft, ChevronRight } from '@lucide/vue'
import { tasksApi } from '../api/index'
import BaseSelect from '../components/ui/BaseSelect.vue'
import PriorityFlag from '../components/PriorityFlag.vue'
import TaskSlideOver from '../components/task/TaskSlideOver.vue'
import { useClientStore } from '../stores/clientStore'
import { addDays, daysBetween, formatShortDate, parseIsoDate, startOfDay, startOfWeek } from '../utils/dates'
import { fullName, presenceColor, presenceLabel } from '../utils/labels'
import { absenceBar, planningDays, type AbsenceBar } from '../utils/planning'
import type { Client, TaskPriority, TaskSummary } from '../types/api'

const TASK_LIMIT = 200
const PRIORITY_RANK: Record<TaskPriority, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 }
const WEEK_OPTIONS = [
  { value: '2', label: '2 semaines' },
  { value: '4', label: '4 semaines' },
  { value: '8', label: '8 semaines' },
]

interface Marker {
  index: number
  tasks: TaskSummary[]
  top: TaskPriority
}

interface PlanningRow {
  client: Client
  bar: AbsenceBar | null
  markers: Marker[]
  overdue: number
}

const clientStore = useClientStore()
const today = startOfDay(new Date())
const from = ref(startOfWeek(today))
const weeksValue = ref<'2' | '4' | '8'>('4')
const weeks = computed(() => Number(weeksValue.value))
const tasks = ref<TaskSummary[]>([])
const truncated = ref(false)
const loading = ref(false)
const selectedId = ref<string | null>(null)

const days = computed(() => planningDays(from.value, weeks.value * 7, today))
const gridStyle = computed(() => ({
  gridTemplateColumns: `minmax(200px, 240px) repeat(${weeks.value * 7}, minmax(${weeks.value > 4 ? 22 : 30}px, 1fr))`,
}))

const rangeLabel = computed(() => {
  const end = addDays(from.value, weeks.value * 7 - 1)
  const short = (d: Date) => d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
  return `${short(from.value)} – ${short(end)} ${end.getFullYear()}`
})

const groups = computed(() => {
  const total = weeks.value * 7
  const byClient = new Map<string, TaskSummary[]>()
  for (const task of tasks.value) {
    const list = byClient.get(task.client_id) ?? []
    list.push(task)
    byClient.set(task.client_id, list)
  }
  const companies = new Map<string, { companyId: string; name: string; rows: PlanningRow[] }>()
  const sorted = [...clientStore.clients].sort((a, b) => fullName(a).localeCompare(fullName(b)))
  for (const client of sorted) {
    const markers = new Map<number, Marker>()
    let overdue = 0
    for (const task of byClient.get(client.id) ?? []) {
      const due = parseIsoDate(task.due_date)
      if (!due) continue
      if (due < today) overdue++
      const index = daysBetween(from.value, due)
      if (index < 0 || index >= total) continue
      const marker = markers.get(index) ?? { index, tasks: [], top: task.priority }
      marker.tasks.push(task)
      if (PRIORITY_RANK[task.priority] < PRIORITY_RANK[marker.top]) marker.top = task.priority
      markers.set(index, marker)
    }
    const group = companies.get(client.company_id) ?? {
      companyId: client.company_id,
      name: client.company.name,
      rows: [],
    }
    group.rows.push({
      client,
      bar: absenceBar(client, from.value, total),
      markers: [...markers.values()],
      overdue,
    })
    companies.set(client.company_id, group)
  }
  return [...companies.values()].sort((a, b) => a.name.localeCompare(b.name))
})

function monthShort(date: Date) {
  return date.toLocaleDateString('fr-FR', { month: 'short' })
}

function weekdayLetter(date: Date) {
  return date.toLocaleDateString('fr-FR', { weekday: 'narrow' })
}

function cellLabel(row: PlanningRow, index: number) {
  const parts = [formatShortDate(days.value[index]!.date)]
  if (row.bar && index >= row.bar.start && index < row.bar.start + row.bar.span) parts.push('absent')
  const marker = row.markers.find((m) => m.index === index)
  if (marker) parts.push(`${marker.tasks.length} échéance(s)`)
  return parts.join(', ')
}

function shift(direction: number) {
  from.value = addDays(from.value, direction * weeks.value * 7)
}

function goToday() {
  from.value = startOfWeek(today)
}

async function load() {
  loading.value = true
  try {
    const { data } = await tasksApi.list({ limit: TASK_LIMIT, offset: 0 })
    tasks.value = data.items
    truncated.value = data.total > data.items.length
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
