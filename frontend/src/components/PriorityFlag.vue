<template>
  <span
    class="inline-flex items-center justify-center shrink-0"
    role="img"
    :aria-label="label"
    :title="label"
    :data-priority="priority"
  >
    <Flag :class="['w-3.5 h-3.5', styles[priority]]" :fill="priority === 'HIGH' ? 'currentColor' : 'none'" />
  </span>
</template>

<script setup lang="ts">
// Un drapeau, pas une pastille : les pastilles de couleur sont réservées à la
// présence des clients. Un commentaire en tête du template ferait du composant
// un fragment et les attributs passés par le parent seraient perdus.
import { computed } from 'vue'
import { Flag } from '@lucide/vue'
import { PRIORITY_LABELS } from '../utils/labels'
import type { TaskPriority } from '../types/api'

const props = defineProps<{ priority: TaskPriority }>()

const styles: Record<TaskPriority, string> = {
  HIGH: 'text-red-500',
  MEDIUM: 'text-amber-500',
  LOW: 'text-slate-300 dark:text-slate-600',
}

const label = computed(() => `Priorité ${PRIORITY_LABELS[props.priority].toLowerCase()}`)
</script>
