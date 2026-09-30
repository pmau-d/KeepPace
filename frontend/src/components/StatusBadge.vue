<template>
  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap', colorClass]">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: String })

const config = {
  TODO: { label: 'À faire', color: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300' },
  IN_PROGRESS: { label: 'En cours', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' },
  BLOCKED: { label: 'En attente', color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300' },
  DONE: { label: 'Terminé', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' },
}

const label = computed(() => config[props.status]?.label ?? props.status)
const colorClass = computed(() => config[props.status]?.color ?? 'bg-gray-100 text-gray-600')
</script>

