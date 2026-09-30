<template>
  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap', colorClass]">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ priority: String })

const config = {
  HIGH: { label: '🔴 Haute', color: 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400' },
  MEDIUM: { label: '🟡 Moyenne', color: 'bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400' },
  LOW: { label: '🟢 Basse', color: 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400' },
}

const label = computed(() => config[props.priority]?.label ?? props.priority)
const colorClass = computed(() => config[props.priority]?.color ?? 'bg-gray-100 text-gray-600')
</script>

