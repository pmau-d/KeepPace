<template>
  <div class="flex items-center gap-3">
    <div
      class="flex-1 h-2 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden"
      role="progressbar"
      :aria-valuenow="progress"
      aria-valuemin="0"
      aria-valuemax="100"
      aria-label="Avancement"
    >
      <div
        :class="['h-full rounded-full', progress === 100 ? 'bg-green-500' : 'bg-indigo-500']"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
    <span class="text-xs tabular-nums text-slate-500 dark:text-slate-400">{{ progress }} %</span>
  </div>
</template>

<script setup lang="ts">
// Version publique : le pourcentage seul, sans compte de tâches (qui révélerait le travail non montré).
defineProps<{ progress: number }>()
</script>
