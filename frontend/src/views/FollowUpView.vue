<template>
  <header
    class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4 flex items-center justify-between shrink-0"
  >
    <div>
      <h1 class="text-lg font-semibold text-slate-800 dark:text-slate-100">À relancer aujourd'hui</h1>
      <p class="text-sm text-slate-400">
        Tâches ouvertes dont le client est joignable, les plus urgentes d'abord.
      </p>
    </div>
    <button
      :disabled="loading"
      class="text-sm px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 disabled:opacity-50"
      @click="load"
    >
      Actualiser
    </button>
  </header>

  <main class="flex-1 overflow-y-auto p-6">
    <div v-if="loading && !items.length" class="flex justify-center items-center h-40">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div
      v-else-if="!items.length"
      class="flex flex-col items-center justify-center h-64 text-slate-400 text-center"
    >
      <p class="text-4xl mb-3">🎉</p>
      <p class="text-lg font-medium">Rien à relancer aujourd'hui</p>
      <p class="text-sm mt-1">Aucune échéance dépassée ni client à recontacter.</p>
    </div>

    <div v-else class="space-y-6">
      <section v-for="group in groups" :key="group.reason" class="space-y-1">
        <h2 :class="['text-sm font-semibold px-4 py-2', FOLLOW_UP_REASONS[group.reason].color]">
          {{ FOLLOW_UP_REASONS[group.reason].label }}
          <span class="text-slate-400 font-normal">· {{ group.tasks.length }}</span>
        </h2>
        <TaskCard v-for="task in group.tasks" :key="task.id" :task="task" @open="selectedId = task.id" />
      </section>
    </div>
  </main>

  <TaskSlideOver v-if="selectedId" :task-id="selectedId" @close="selectedId = null" @changed="load" />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { tasksApi } from '../api/index'
import TaskCard from '../components/TaskCard.vue'
import TaskSlideOver from '../components/task/TaskSlideOver.vue'
import { FOLLOW_UP_REASONS } from '../utils/labels'
import type { FollowUpItem, FollowUpReason } from '../types/api'

const items = ref<FollowUpItem[]>([])
const loading = ref(false)
const selectedId = ref<string | null>(null)

// L'API renvoie les tâches déjà triées par urgence : on garde cet ordre.
const groups = computed(() => {
  const byReason = new Map<FollowUpReason, FollowUpItem[]>()
  for (const task of items.value) {
    const group = byReason.get(task.follow_up_reason) ?? []
    group.push(task)
    byReason.set(task.follow_up_reason, group)
  }
  return [...byReason].map(([reason, tasks]) => ({ reason, tasks }))
})

async function load() {
  loading.value = true
  try {
    items.value = (await tasksApi.followUp()).data
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
