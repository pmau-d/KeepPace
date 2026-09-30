<template>
  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap', colorClass]">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PRIORITY_LABELS } from '../utils/labels'
import type { TaskPriority } from '../types/api'

const props = defineProps<{ priority: TaskPriority }>()

const colors: Record<TaskPriority, string> = {
  HIGH: 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400',
  MEDIUM: 'bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400',
  LOW: 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400',
}

const label = computed(() =>
  PRIORITY_LABELS[props.priority]
    ? `Priorité ${PRIORITY_LABELS[props.priority].toLowerCase()}`
    : props.priority,
)
const colorClass = computed(() => colors[props.priority] ?? 'bg-gray-100 text-gray-600')
</script>
