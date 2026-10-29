<template>
  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap', colorClass]">
    {{ PROJECT_STATUS_LABELS[status] ?? status }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PROJECT_STATUS_LABELS } from '../utils/labels'
import type { ProjectStatus } from '../types/api'

const props = defineProps<{ status: ProjectStatus }>()

const colors: Record<ProjectStatus, string> = {
  IDEA: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300',
  ACTIVE: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  PAUSED: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
  DELIVERED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
}

const colorClass = computed(() => colors[props.status] ?? 'bg-gray-100 text-gray-600')
</script>
