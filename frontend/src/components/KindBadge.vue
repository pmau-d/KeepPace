<template>
  <span :class="['inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium', colorClass]">
    <component :is="icon" class="w-3 h-3" aria-hidden="true" />
    {{ KIND_LABELS[kind] ?? kind }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Bug, CircleCheck, Sparkles } from '@lucide/vue'
import { KIND_LABELS } from '../utils/labels'
import type { TaskKind } from '../types/api'

const props = defineProps<{ kind: TaskKind }>()

const icons = { TASK: CircleCheck, BUG: Bug, IMPROVEMENT: Sparkles }
const colors: Record<TaskKind, string> = {
  TASK: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
  BUG: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  IMPROVEMENT: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
}

const icon = computed(() => icons[props.kind] ?? CircleCheck)
const colorClass = computed(() => colors[props.kind] ?? colors.TASK)
</script>
