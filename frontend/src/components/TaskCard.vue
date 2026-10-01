<template>
  <div
    role="button"
    tabindex="0"
    :aria-label="`Ouvrir la tâche ${task.title}`"
    :class="[
      'group grid grid-cols-[16px_minmax(0,1fr)_auto] md:grid-cols-[16px_minmax(0,1fr)_minmax(200px,300px)_110px_140px] gap-x-3 gap-y-1 items-center rounded-lg border border-slate-100 dark:border-slate-700/60 bg-white dark:bg-slate-800 cursor-pointer hover:shadow-xs hover:border-slate-300 dark:hover:border-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-all duration-150 select-none relative',
      compact ? 'px-3 py-1.5' : 'px-4 py-3',
      isDone && 'opacity-60',
      !isDone && isUnreachable && 'opacity-80',
    ]"
    @click="$emit('open')"
    @keydown.enter.prevent="$emit('open')"
    @keydown.space.prevent="$emit('open')"
  >
    <!-- Mobile : drapeau, titre, statut, puis le client en dessous. Bureau : une colonne chacun. -->
    <PriorityFlag :priority="task.priority" class="mx-auto col-start-1 row-start-1" />

    <div class="min-w-0 col-start-2 row-start-1">
      <div class="flex items-center gap-2 flex-wrap">
        <span
          :class="[
            'font-semibold text-sm leading-snug',
            isDone ? 'line-through text-slate-400 dark:text-slate-500' : 'text-slate-800 dark:text-slate-100',
          ]"
        >
          {{ task.title }}
        </span>
        <span
          v-if="task.sub_status"
          class="text-[10px] px-1.5 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 font-medium whitespace-nowrap"
        >
          {{ task.sub_status }}
        </span>
        <span
          v-if="task.comments_count"
          class="text-[10px] text-slate-400 flex items-center gap-0.5"
          :title="`${task.comments_count} commentaire(s)`"
        >
          <MessageSquare class="w-3 h-3" aria-hidden="true" /> {{ task.comments_count }}
        </span>
      </div>
      <p
        v-if="task.description && !compact"
        class="text-xs text-slate-400 dark:text-slate-500 truncate mt-0.5"
      >
        {{ task.description }}
      </p>
    </div>

    <div
      class="col-start-2 row-start-2 md:col-start-3 md:row-start-1 min-w-0"
      :title="note ?? presenceLabel(task.client.presence_status)"
    >
      <div class="flex items-center gap-1.5 min-w-0">
        <span :class="['w-2 h-2 rounded-full shrink-0', presenceColor(task.client.presence_status)]"></span>
        <span class="text-xs text-slate-500 dark:text-slate-400 truncate">
          {{ fullName(task.client) }}
          <span class="text-slate-300 dark:text-slate-600 mx-0.5">·</span>
          {{ task.client.company.name }}
        </span>
      </div>
      <!-- Pourquoi la ligne est atténuée : le client n'est pas joignable en ce moment -->
      <p
        v-if="note"
        :class="[
          'text-[11px] mt-0.5 ml-3.5 truncate',
          isUnreachable ? 'text-red-600 dark:text-red-400' : 'text-slate-400 dark:text-slate-500',
        ]"
      >
        {{ note }}
      </p>
    </div>

    <div class="hidden md:block md:col-start-4 md:row-start-1">
      <span
        v-if="task.due_date"
        :class="[
          'text-xs font-medium flex items-center gap-1',
          isOverdue ? 'text-red-500' : 'text-slate-500 dark:text-slate-400',
        ]"
      >
        <Calendar class="w-3 h-3 shrink-0" aria-hidden="true" />
        {{ dueLabel }}
      </span>
      <span v-else class="text-xs text-slate-300 dark:text-slate-600">—</span>
    </div>

    <div
      class="flex items-center justify-end md:justify-start gap-1.5 col-start-3 row-start-1 md:col-start-5"
    >
      <button
        v-if="isDone"
        :disabled="reopening"
        class="text-xs flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-700 hover:bg-blue-100 transition-colors disabled:opacity-50 font-medium whitespace-nowrap"
        @click.stop="handleReopen"
      >
        {{ reopening ? '…' : 'Réouvrir' }}
      </button>
      <StatusBadge v-else :status="task.status" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Calendar, MessageSquare } from '@lucide/vue'
import { computed, ref } from 'vue'
import StatusBadge from './StatusBadge.vue'
import PriorityFlag from './PriorityFlag.vue'
import { useTaskStore } from '../stores/taskStore'
import { useDensity } from '../composables/useDensity'
import { formatCompactDate, parseIsoDate, startOfDay } from '../utils/dates'
import { fullName, presenceColor, presenceLabel, presenceNote } from '../utils/labels'
import type { TaskSummary } from '../types/api'

const props = defineProps<{ task: TaskSummary }>()
defineEmits<{ open: [] }>()

const taskStore = useTaskStore()
const reopening = ref(false)

const isDone = computed(() => props.task.status === 'DONE')
const { compact } = useDensity()
const note = computed(() => presenceNote(props.task.client))
const isUnreachable = computed(() => props.task.client.presence_status === 'ABSENT')
const dueLabel = computed(() => {
  const due = parseIsoDate(props.task.due_date)
  return due ? formatCompactDate(due) : ''
})
const isOverdue = computed(() => {
  const due = parseIsoDate(props.task.due_date)
  return !isDone.value && due !== null && due < startOfDay(new Date())
})

async function handleReopen() {
  reopening.value = true
  try {
    await taskStore.reopenTask(props.task.id)
  } finally {
    reopening.value = false
  }
}
</script>
