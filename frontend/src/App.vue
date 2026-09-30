<template>
  <div :class="isDark ? 'dark' : ''">
    <div class="flex h-screen bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-100 overflow-hidden">

      <!-- Sidebar -->
      <Sidebar />

      <!-- Main area -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <TopBar :is-dark="isDark" @toggle-dark="toggleDark" @open-create="showCreateModal = true" />
        <TaskList />
      </div>

      <!-- Slide-over panel -->
      <TaskSlideOver v-if="taskStore.selectedTask" @close="taskStore.closeSlideOver()" @duplicate="openDuplicate" />

      <!-- Create task modal -->
      <CreateTaskModal v-if="showCreateModal" @close="showCreateModal = false" />

      <!-- Duplicate task modal -->
      <CreateTaskModal v-if="duplicateSource" :prefill="duplicateSource" @close="duplicateSource = null" />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTaskStore } from './stores/taskStore.js'
import { useClientStore } from './stores/clientStore.js'
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
import TaskList from './components/TaskList.vue'
import TaskSlideOver from './components/TaskSlideOver.vue'
import CreateTaskModal from './components/CreateTaskModal.vue'

const taskStore = useTaskStore()
const clientStore = useClientStore()

const isDark = ref(localStorage.getItem('keepPaceDark') === 'true')
const showCreateModal = ref(false)
const duplicateSource = ref(null)

function openDuplicate(task) {
  duplicateSource.value = task
}

function toggleDark() {
  isDark.value = !isDark.value
  localStorage.setItem('keepPaceDark', String(isDark.value))
}

onMounted(async () => {
  await Promise.all([
    clientStore.fetchClients(),
    clientStore.fetchCompanies(),
    taskStore.fetchTasks(),
  ])
})
</script>

