<template>
  <main class="flex-1 overflow-y-auto p-6">
    <div v-if="taskStore.loading && !taskStore.tasks.length" class="flex justify-center items-center h-40">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div
      v-else-if="!taskStore.tasks.length"
      class="flex flex-col items-center justify-center h-64 text-slate-400 dark:text-slate-500 text-center"
    >
      <ClipboardList class="w-16 h-16 mb-4 opacity-50" aria-hidden="true" />
      <template v-if="hasFilters">
        <p class="text-lg font-medium">Aucune tâche ne correspond à ces filtres</p>
        <p class="text-sm mt-1">Modifiez la recherche ou les filtres pour élargir les résultats.</p>
      </template>
      <template v-else>
        <p class="text-lg font-medium">Aucune tâche</p>
        <p class="text-sm mt-1">Cliquez sur « Nouvelle tâche » pour commencer.</p>
      </template>
    </div>

    <div v-else :class="['space-y-6 transition-opacity', taskStore.loading && 'opacity-60']">
      <p class="text-xs text-slate-400 px-1">
        {{ taskStore.total }} tâche{{ taskStore.total > 1 ? 's' : '' }}
        <span v-if="taskStore.tasks.length < taskStore.total">· {{ taskStore.tasks.length }} affichées</span>
      </p>

      <section v-for="group in groups" :key="group.key" class="space-y-1" :aria-label="group.label">
        <div
          class="flex items-center gap-3 px-4 py-2 sticky top-0 bg-slate-100/80 dark:bg-slate-900/80 backdrop-blur-xs z-10"
        >
          <span :class="['w-1.5 h-1.5 rounded-full', group.overdue ? 'bg-red-500' : 'bg-indigo-400']"></span>
          <h3
            :class="[
              'text-sm font-semibold tracking-wide',
              group.overdue ? 'text-red-600 dark:text-red-400' : 'text-slate-700 dark:text-slate-300',
            ]"
          >
            {{ group.label }}
          </h3>
          <div class="flex-1 h-px bg-slate-200 dark:bg-slate-700"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 font-medium">
            {{ group.tasks.length }} tâche{{ group.tasks.length > 1 ? 's' : '' }}
          </span>
        </div>

        <TaskCard
          v-for="task in group.tasks"
          :key="task.id"
          :task="task"
          @open="$emit('open-task', task.id)"
        />
      </section>

      <div v-if="taskStore.hasMore" class="flex justify-center pt-2">
        <button
          :disabled="taskStore.loadingMore"
          class="text-sm px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-800 disabled:opacity-50"
          @click="taskStore.loadMore()"
        >
          {{
            taskStore.loadingMore
              ? 'Chargement…'
              : `Afficher plus (${taskStore.total - taskStore.tasks.length} restantes)`
          }}
        </button>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ClipboardList } from 'lucide-vue-next'
import { computed } from 'vue'
import { useTaskStore } from '../stores/taskStore'
import { groupTasksByDay } from '../utils/grouping'
import TaskCard from './TaskCard.vue'

defineEmits<{ 'open-task': [taskId: string] }>()

const taskStore = useTaskStore()

const groups = computed(() => groupTasksByDay(taskStore.tasks))
const hasFilters = computed(() => {
  const f = taskStore.filters
  return Boolean(f.search || f.status || f.presenceStatus || f.clientId)
})
</script>
