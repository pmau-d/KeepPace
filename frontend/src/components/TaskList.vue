<template>
  <main class="flex-1 overflow-y-auto p-6">
    <!-- Loading spinner -->
    <div v-if="taskStore.loading" class="flex justify-center items-center h-40">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="taskStore.tasks.length === 0"
      class="flex flex-col items-center justify-center h-64 text-slate-400 dark:text-slate-500"
    >
      <svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1"
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
        />
      </svg>
      <p class="text-lg font-medium">Aucune tâche</p>
      <p class="text-sm mt-1">Cliquez sur « Nouvelle tâche » pour commencer !</p>
    </div>

    <!-- Agile backlog list -->
    <div v-else class="space-y-6">
      <!-- Day section -->
      <div v-for="(group, dayKey) in groupedByDay" :key="dayKey" class="space-y-1">
        <!-- Day header -->
        <div
          class="flex items-center gap-3 px-4 py-2 sticky top-0 bg-slate-50/50 dark:bg-slate-900/30 backdrop-blur-xs z-10"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
          <h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 tracking-wide">{{ dayKey }}</h3>
          <div class="flex-1 h-px bg-slate-200 dark:bg-slate-700"></div>
          <span class="text-xs text-slate-400 dark:text-slate-500 font-medium"
            >{{ group?.length || 0 }} tâche{{ (group?.length || 0) > 1 ? 's' : '' }}</span
          >
        </div>

        <!-- Tasks for this day -->
        <TaskCard
          v-for="task in group || []"
          :key="task.id"
          :task="task"
          @click="taskStore.selectTask(task)"
        />
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useTaskStore } from '../stores/taskStore.js'
import TaskCard from './TaskCard.vue'

const taskStore = useTaskStore()

const priorityRank = { HIGH: 1, MEDIUM: 2, LOW: 3 }
const today = new Date()
today.setHours(0, 0, 0, 0)

/** Sort: priority HIGH→LOW, then due_date closest to today (nulls last) */
const sortedTasks = computed(() =>
  [...taskStore.tasks].sort((a, b) => {
    const pDiff = (priorityRank[a.priority] ?? 9) - (priorityRank[b.priority] ?? 9)
    if (pDiff !== 0) return pDiff
    if (a.due_date && b.due_date) return new Date(a.due_date) - new Date(b.due_date)
    if (a.due_date) return -1
    if (b.due_date) return 1
    return 0
  }),
)

/** Group tasks by day with smart labels (Aujourd'hui, Demain, etc.) */
const groupedByDay = computed(() => {
  const groups = new Map()
  const dayOrder = []

  sortedTasks.value.forEach((task) => {
    let dayLabel, dayDate

    if (!task.due_date) {
      dayLabel = 'Sans échéance'
      dayDate = new Date(9999, 11, 31)
    } else {
      const dueDate = new Date(task.due_date)
      dueDate.setHours(0, 0, 0, 0)
      const diff = Math.floor((dueDate - today) / (1000 * 60 * 60 * 24))

      if (diff === 0) {
        dayLabel = "📌 Aujourd'hui"
      } else if (diff === 1) {
        dayLabel = '⏭️ Demain'
      } else if (diff > 1 && diff <= 7) {
        dayLabel = new Date(dueDate).toLocaleDateString('fr-FR', {
          weekday: 'long',
          day: '2-digit',
          month: 'long',
        })
        dayLabel = dayLabel.charAt(0).toUpperCase() + dayLabel.slice(1)
      } else if (diff > 7) {
        dayLabel = new Date(dueDate).toLocaleDateString('fr-FR', {
          day: '2-digit',
          month: 'long',
          year: 'numeric',
        })
      } else {
        dayLabel =
          '⚠️ Retard — ' + new Date(dueDate).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long' })
      }
      dayDate = dueDate
    }

    if (!groups.has(dayLabel)) {
      groups.set(dayLabel, [])
      dayOrder.push({ label: dayLabel, date: dayDate })
    }
    groups.get(dayLabel).push(task)
  })

  // Sort day order
  dayOrder.sort((a, b) => a.date - b.date)

  // Convert to plain object for Vue reactivity
  const result = {}
  dayOrder.forEach(({ label }) => {
    result[label] = groups.get(label)
  })

  return result
})
</script>
