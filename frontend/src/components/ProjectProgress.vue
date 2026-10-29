<template>
  <div class="flex items-center gap-3">
    <div
      class="flex-1 h-2 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden"
      role="progressbar"
      :aria-valuenow="progress"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`Avancement : ${done} tâche(s) terminée(s) sur ${total}`"
    >
      <div
        :class="[
          'h-full rounded-full transition-all duration-500',
          progress === 100 ? 'bg-green-500' : 'bg-indigo-500',
        ]"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
    <span class="text-xs tabular-nums text-slate-500 dark:text-slate-400 whitespace-nowrap">
      {{ total ? `${done}/${total}` : 'Aucune tâche' }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ progress: number; done: number; total: number }>()
</script>
