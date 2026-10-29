<template>
  <li
    class="group flex items-center gap-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 shadow-xs"
  >
    <button
      type="button"
      :class="[
        'w-5 h-5 rounded-full border-2 shrink-0 flex items-center justify-center transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
        done
          ? 'bg-green-500 border-green-500 text-white'
          : 'border-slate-300 dark:border-slate-500 hover:border-indigo-500',
      ]"
      :aria-label="done ? `Rouvrir « ${task.title} »` : `Terminer « ${task.title} »`"
      :aria-pressed="done"
      @click="$emit('toggle', task)"
    >
      <Check v-if="done" class="w-3 h-3" aria-hidden="true" />
    </button>

    <div class="flex-1 min-w-0">
      <p
        :class="[
          'text-sm font-medium wrap-break-word',
          done ? 'line-through text-slate-400' : 'text-slate-800 dark:text-slate-100',
        ]"
      >
        {{ task.title }}
      </p>
      <div class="mt-1 flex items-center gap-2 flex-wrap text-xs text-slate-400">
        <KindBadge :kind="task.kind" />
        <StatusBadge
          v-if="task.status === 'IN_PROGRESS' || task.status === 'BLOCKED'"
          :status="task.status"
        />
        <span v-if="task.due_date" :class="overdue && 'text-red-500 font-medium'">
          {{ overdue ? 'En retard · ' : '' }}{{ formatDate(task.due_date) }}
        </span>
        <span v-if="repeat" class="inline-flex items-center gap-1">
          <Repeat class="w-3 h-3" aria-hidden="true" />{{ repeat }}
        </span>
      </div>
    </div>

    <PriorityFlag :priority="task.priority" />

    <button
      type="button"
      class="p-1.5 rounded-lg text-slate-300 opacity-0 group-hover:opacity-100 focus:opacity-100 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
      :aria-label="`Archiver « ${task.title} »`"
      @click="$emit('archive', task)"
    >
      <Archive class="w-4 h-4" aria-hidden="true" />
    </button>
  </li>
</template>

<script setup lang="ts">
import { Archive, Check, Repeat } from '@lucide/vue'
import { computed } from 'vue'
import KindBadge from './KindBadge.vue'
import PriorityFlag from './PriorityFlag.vue'
import StatusBadge from './StatusBadge.vue'
import { toIsoDate } from '../utils/dates'
import { formatDate, recurrenceLabel } from '../utils/labels'
import type { ProjectTask } from '../types/api'

const props = defineProps<{ task: ProjectTask }>()
defineEmits<{ toggle: [task: ProjectTask]; archive: [task: ProjectTask] }>()

const done = computed(() => props.task.status === 'DONE')
// Les dates AAAA-MM-JJ se comparent comme des chaînes.
const overdue = computed(
  () => !done.value && !!props.task.due_date && props.task.due_date < toIsoDate(new Date()),
)
const repeat = computed(() => recurrenceLabel(props.task.recurrence, props.task.recurrence_interval))
</script>
