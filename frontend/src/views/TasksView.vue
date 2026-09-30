<template>
  <TopBar @open-create="creating = { prefill: null }" />
  <TaskList @open-task="openTask" />

  <TaskSlideOver
    v-if="id"
    :task-id="id"
    @close="closeTask"
    @duplicate="(task) => (creating = { prefill: task })"
    @changed="taskStore.fetchTasks()"
  />

  <CreateTaskModal v-if="creating" :prefill="creating.prefill" @close="creating = null" />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '../components/TopBar.vue'
import TaskList from '../components/TaskList.vue'
import TaskSlideOver from '../components/task/TaskSlideOver.vue'
import CreateTaskModal from '../components/CreateTaskModal.vue'
import { useTaskStore } from '../stores/taskStore'
import type { TaskSummary } from '../types/api'

// `id` vient de l'URL /tasks/:id : chaque tâche a un lien partageable.
withDefaults(defineProps<{ id?: string | null }>(), { id: null })

const router = useRouter()
const taskStore = useTaskStore()
// null : fenêtre fermée ; prefill null : nouvelle tâche ; prefill : duplication
const creating = ref<{ prefill: TaskSummary | null } | null>(null)

function openTask(taskId: string) {
  router.push({ name: 'task', params: { id: taskId } })
}

function closeTask() {
  router.push({ name: 'tasks' })
}

onMounted(() => taskStore.fetchTasks())
</script>
