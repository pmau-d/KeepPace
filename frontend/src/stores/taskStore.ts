import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { tasksApi } from '../api/index'
import type {
  PresenceStatus,
  Task,
  TaskCreatePayload,
  TaskQuery,
  TaskStatus,
  TaskSummary,
  TaskUpdatePayload,
} from '../types/api'

export const PAGE_SIZE = 50

export interface TaskFilters {
  clientId: string | null
  status: TaskStatus | null
  presenceStatus: PresenceStatus | null
  showDone: boolean
  search: string
}

function defaultFilters(): TaskFilters {
  return { clientId: null, status: null, presenceStatus: null, showDone: false, search: '' }
}

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<TaskSummary[]>([])
  const total = ref(0)
  const loading = ref(false)
  const loadingMore = ref(false)
  const filters = ref<TaskFilters>(defaultFilters())
  const hasMore = computed(() => tasks.value.length < total.value)
  // Évite qu'une réponse lente écrase le résultat d'une recherche plus récente
  let requestId = 0

  function queryParams(): TaskQuery {
    const f = filters.value
    const params: TaskQuery = {}
    if (f.clientId) params.client_id = f.clientId
    if (f.status) params.status = f.status
    if (f.presenceStatus) params.presence_status = f.presenceStatus
    if (f.showDone) params.show_done = true
    if (f.search.trim()) params.search = f.search.trim()
    return params
  }

  async function fetchTasks() {
    const current = ++requestId
    loading.value = true
    try {
      const { data } = await tasksApi.list({ ...queryParams(), limit: PAGE_SIZE, offset: 0 })
      if (current !== requestId) return
      tasks.value = data.items
      total.value = data.total
    } finally {
      if (current === requestId) loading.value = false
    }
  }

  async function loadMore() {
    if (!hasMore.value || loadingMore.value) return
    loadingMore.value = true
    try {
      const { data } = await tasksApi.list({ ...queryParams(), limit: PAGE_SIZE, offset: tasks.value.length })
      const known = new Set(tasks.value.map((t) => t.id))
      tasks.value.push(...data.items.filter((t) => !known.has(t.id)))
      total.value = data.total
    } finally {
      loadingMore.value = false
    }
  }

  /** Met à jour la tâche dans la liste, ou l'en retire si elle ne correspond plus aux filtres. */
  function syncInList(task: TaskSummary) {
    const idx = tasks.value.findIndex((t) => t.id === task.id)
    if (idx === -1) return
    if (task.status === 'DONE' && !filters.value.showDone) {
      tasks.value.splice(idx, 1)
      total.value -= 1
    } else {
      tasks.value[idx] = task
    }
  }

  async function fetchTask(id: string): Promise<Task> {
    return (await tasksApi.get(id)).data
  }

  async function createTask(data: TaskCreatePayload) {
    const task = (await tasksApi.create(data)).data
    // Recharger pour respecter le tri et les filtres serveur
    await fetchTasks()
    return task
  }

  async function updateTask(id: string, data: TaskUpdatePayload) {
    const task = (await tasksApi.update(id, data)).data
    syncInList(task)
    return task
  }

  async function closeTask(id: string) {
    const task = (await tasksApi.close(id)).data
    syncInList(task)
    return task
  }

  async function reopenTask(id: string) {
    const task = (await tasksApi.reopen(id)).data
    syncInList(task)
    return task
  }

  /** « Relancer dans N jours » : la liste est rechargée, la tâche change de groupe. */
  async function snoozeTask(id: string, days: number, comment?: string) {
    const task = (await tasksApi.snooze(id, days, comment)).data
    await fetchTasks()
    return task
  }

  async function archiveTask(id: string) {
    await tasksApi.archive(id)
    const before = tasks.value.length
    tasks.value = tasks.value.filter((t) => t.id !== id)
    total.value -= before - tasks.value.length
  }

  async function restoreTask(id: string) {
    const task = (await tasksApi.restore(id)).data
    await fetchTasks()
    return task
  }

  function setFilter<K extends keyof TaskFilters>(key: K, value: TaskFilters[K]) {
    filters.value[key] = value
    return fetchTasks()
  }

  function setClientFilter(clientId: string | null) {
    filters.value.clientId = filters.value.clientId === clientId ? null : clientId
    return fetchTasks()
  }

  function reset() {
    tasks.value = []
    total.value = 0
    filters.value = defaultFilters()
  }

  return {
    tasks,
    total,
    loading,
    loadingMore,
    filters,
    hasMore,
    queryParams,
    fetchTasks,
    loadMore,
    fetchTask,
    createTask,
    updateTask,
    closeTask,
    reopenTask,
    snoozeTask,
    archiveTask,
    restoreTask,
    setFilter,
    setClientFilter,
    reset,
  }
})
