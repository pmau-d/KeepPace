<template>
  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap', colorClass]">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { STATUS_LABELS } from '../utils/labels'
import type { TaskStatus } from '../types/api'

// Une valeur inconnue (nouvelle version de l'API) s'affiche telle quelle.
const props = defineProps<{ status: TaskStatus | string }>()

const colors: Record<string, string> = {
  TODO: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
  IN_PROGRESS: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  BLOCKED: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  DONE: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
}

const label = computed(() => STATUS_LABELS[props.status as TaskStatus] ?? props.status)
const colorClass = computed(() => colors[props.status] ?? 'bg-gray-100 text-gray-600')
</script>
