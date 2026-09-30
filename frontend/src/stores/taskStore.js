import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tasksApi } from '../api/index.js'

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref([])
  const loading = ref(false)
  const selectedTask = ref(null)

  const filters = ref({
    clientId: null,
    status: null,
    presenceStatus: null,
    showDone: false,
    search: '',
  })

  async function fetchTasks() {
    loading.value = true
    try {
      const params = {}
      if (filters.value.clientId) params.client_id = filters.value.clientId
      if (filters.value.status) params.status = filters.value.status
      if (filters.value.presenceStatus) params.presence_status = filters.value.presenceStatus
      if (filters.value.showDone) params.show_done = true
      if (filters.value.search) params.search = filters.value.search
      const res = await tasksApi.getAll(params)
      tasks.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function createTask(data) {
    const res = await tasksApi.create(data)
    tasks.value.unshift(res.data)
    return res.data
  }

  async function updateTask(id, data) {
    const res = await tasksApi.update(id, data)
    const idx = tasks.value.findIndex((t) => t.id === id)
    if (idx !== -1) {
      if (res.data.status === 'DONE' && !filters.value.showDone) {
        tasks.value.splice(idx, 1)
      } else {
        tasks.value[idx] = res.data
      }
    }
    if (selectedTask.value?.id === id) {
      selectedTask.value = res.data
    }
    return res.data
  }

  async function deleteTask(id) {
    await tasksApi.delete(id)
    tasks.value = tasks.value.filter((t) => t.id !== id)
    if (selectedTask.value?.id === id) selectedTask.value = null
  }

  async function closeTask(id) {
    const res = await tasksApi.close(id)
    const idx = tasks.value.findIndex((t) => t.id === id)
    if (idx !== -1) {
      if (!filters.value.showDone) tasks.value.splice(idx, 1)
      else tasks.value[idx] = res.data
    }
    if (selectedTask.value?.id === id) selectedTask.value = res.data
    return res.data
  }

  async function reopenTask(id) {
    const res = await tasksApi.reopen(id)
    const idx = tasks.value.findIndex((t) => t.id === id)
    if (idx !== -1) tasks.value[idx] = res.data
    if (selectedTask.value?.id === id) selectedTask.value = res.data
    return res.data
  }

  function clearTasks() {
    tasks.value = []
    selectedTask.value = null
  }

  function selectTask(task) {
    selectedTask.value = task
  }

  function closeSlideOver() {
    selectedTask.value = null
  }

  function setFilter(key, value) {
    filters.value[key] = value
    fetchTasks()
  }

  function setClientFilter(clientId) {
    // Toggle: clicking the same client deselects it
    filters.value.clientId = filters.value.clientId === clientId ? null : clientId
    fetchTasks()
  }

  return {
    tasks,
    loading,
    selectedTask,
    filters,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    closeTask,
    reopenTask,
    clearTasks,
    selectTask,
    closeSlideOver,
    setFilter,
    setClientFilter,
  }
})
