<template>
  <li>
    <button
      type="button"
      class="w-full flex items-center gap-3 text-left rounded-lg px-3 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-700/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
      @click="$emit('open')"
    >
      <PriorityFlag :priority="task.priority" />
      <span class="flex-1 min-w-0">
        <span class="block text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{{
          task.title
        }}</span>
        <span class="flex items-center gap-1.5 text-xs text-slate-400 min-w-0">
          <span
            :class="['w-1.5 h-1.5 rounded-full shrink-0', presenceColor(task.client.presence_status)]"
            aria-hidden="true"
          ></span>
          <span class="truncate">{{ fullName(task.client) }} · {{ task.client.company.name }}</span>
        </span>
      </span>
      <span v-if="note" :class="['text-xs font-medium shrink-0 text-right max-w-40', noteClass]">{{
        note
      }}</span>
      <span
        v-else-if="task.due_date"
        :class="['text-xs shrink-0', overdue ? 'text-red-500 font-medium' : 'text-slate-400']"
        >{{ dueLabel }}</span
      >
    </button>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PriorityFlag from './PriorityFlag.vue'
import { formatCompactDate, parseIsoDate, startOfDay } from '../utils/dates'
import { fullName, presenceColor } from '../utils/labels'
import type { TaskSummary } from '../types/api'

const props = defineProps<{ task: TaskSummary; note?: string; noteClass?: string }>()
defineEmits<{ open: [] }>()

const due = computed(() => parseIsoDate(props.task.due_date))
const dueLabel = computed(() => (due.value ? formatCompactDate(due.value) : ''))
const overdue = computed(() => due.value !== null && due.value < startOfDay(new Date()))
</script>
