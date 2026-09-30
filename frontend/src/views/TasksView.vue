<template>
  <TopBar @open-create="createPrefill = {}" />
  <TaskList @open-task="openTask" />

  <TaskSlideOver
    v-if="id"
    :task-id="id"
    @close="closeTask"
    @duplicate="(task) => (createPrefill = task)"
    @changed="taskStore.fetchTasks()"
  />

  <CreateTaskModal
    v-if="createPrefill"
    :prefill="createPrefill.id ? createPrefill : null"
    @close="createPrefill = null"
  />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '../components/TopBar.vue'
import TaskList from '../components/TaskList.vue'
import TaskSlideOver from '../components/task/TaskSlideOver.vue'
import CreateTaskModal from '../components/CreateTaskModal.vue'
import { useTaskStore } from '../stores/taskStore.js'

// `id` vient de l'URL /tasks/:id : chaque tâche a un lien partageable.
defineProps({ id: { type: String, default: null } })

const router = useRouter()
const taskStore = useTaskStore()
// null : fenêtre fermée ; {} : nouvelle tâche ; tâche : duplication
const createPrefill = ref(null)

function openTask(taskId) {
  router.push({ name: 'task', params: { id: taskId } })
}

function closeTask() {
  router.push({ name: 'tasks' })
}

onMounted(() => taskStore.fetchTasks())
</script>
