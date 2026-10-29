<template>
  <li
    class="group bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-xs"
  >
    <div class="flex items-center gap-3 px-4 py-3">
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
          <button
            type="button"
            :class="[
              'inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
              checklistComplete
                ? 'text-green-600 dark:text-green-400'
                : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700',
            ]"
            :aria-expanded="open"
            :aria-label="`Checklist de « ${task.title} »`"
            @click="open = !open"
          >
            <ListChecks class="w-3 h-3" aria-hidden="true" />
            {{ task.checklist.length ? `${checklistDone}/${task.checklist.length}` : 'Checklist' }}
          </button>
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
    </div>

    <div v-if="open" class="border-t border-slate-100 dark:border-slate-700 px-4 py-3">
      <ChecklistEditor
        :items="task.checklist"
        :can-finish="!done"
        :id-prefix="`ptask-${task.id}`"
        @add="add"
        @toggle="toggle"
        @remove="remove"
        @finish="$emit('toggle', task)"
      />
    </div>
  </li>
</template>

<script setup lang="ts">
import { Archive, Check, ListChecks, Repeat } from '@lucide/vue'
import { computed, ref } from 'vue'
import { projectTasksApi } from '../api/index'
import { useToastStore } from '../stores/toast'
import { toIsoDate } from '../utils/dates'
import { formatDate, recurrenceLabel } from '../utils/labels'
import KindBadge from './KindBadge.vue'
import PriorityFlag from './PriorityFlag.vue'
import StatusBadge from './StatusBadge.vue'
import ChecklistEditor from './task/ChecklistEditor.vue'
import type { ChecklistItem, ProjectTask } from '../types/api'

const props = defineProps<{ task: ProjectTask }>()
// `changed` : une case a changé, le parent recharge la liste (le comptage reste exact).
const emit = defineEmits<{ toggle: [task: ProjectTask]; archive: [task: ProjectTask]; changed: [] }>()

const toast = useToastStore()
const open = ref(false)

const done = computed(() => props.task.status === 'DONE')
// Les dates AAAA-MM-JJ se comparent comme des chaînes.
const overdue = computed(
  () => !done.value && !!props.task.due_date && props.task.due_date < toIsoDate(new Date()),
)
const repeat = computed(() => recurrenceLabel(props.task.recurrence, props.task.recurrence_interval))
const checklistDone = computed(() => props.task.checklist.filter((item) => item.done).length)
const checklistComplete = computed(
  () => props.task.checklist.length > 0 && checklistDone.value === props.task.checklist.length,
)

async function run(action: () => Promise<unknown>, failure: string) {
  try {
    await action()
    emit('changed')
  } catch (e) {
    toast.error(e, failure)
  }
}

const add = (label: string) =>
  run(() => projectTasksApi.addChecklistItem(props.task.id, label), "Impossible d'ajouter la case.")
const toggle = (item: ChecklistItem) =>
  run(
    () => projectTasksApi.updateChecklistItem(props.task.id, item.id, { done: !item.done }),
    'Impossible de modifier la case.',
  )
const remove = (item: ChecklistItem) =>
  run(() => projectTasksApi.deleteChecklistItem(props.task.id, item.id), 'Impossible de supprimer la case.')
</script>
