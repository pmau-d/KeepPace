<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex"
      role="dialog"
      aria-modal="true"
      :aria-label="task?.title ?? 'Tâche'"
      @keydown.esc="$emit('close')"
    >
      <div class="flex-1 bg-black/30 backdrop-blur-xs" @click="$emit('close')"></div>

      <div
        ref="panel"
        tabindex="-1"
        class="w-full max-w-lg bg-white dark:bg-slate-800 shadow-2xl flex flex-col h-full border-l border-slate-200 dark:border-slate-700 focus:outline-none slide-in"
      >
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <div
            class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"
          ></div>
        </div>

        <div
          v-else-if="!task"
          class="flex-1 flex flex-col items-center justify-center gap-3 text-slate-400 p-6 text-center"
        >
          <p>Cette tâche est introuvable ou a été archivée.</p>
          <button class="text-sm text-indigo-600 dark:text-indigo-400" @click="$emit('close')">Fermer</button>
        </div>

        <template v-else>
          <!-- En-tête -->
          <div
            class="flex items-start justify-between p-5 border-b border-slate-200 dark:border-slate-700 shrink-0"
          >
            <div class="flex-1 min-w-0 pr-3">
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <StatusBadge :status="task.status" />
                <PriorityBadge :priority="task.priority" />
              </div>
              <h2 class="font-bold text-lg text-slate-800 dark:text-slate-100 leading-snug break-words">
                {{ task.title }}
              </h2>
              <p class="text-sm text-slate-400 mt-0.5 flex items-center gap-1.5">
                <span
                  :class="['w-2 h-2 rounded-full shrink-0', presenceColor(task.client.presence_status)]"
                ></span>
                {{ fullName(task.client) }} · {{ task.client.company.name }}
                <span class="text-xs">({{ presenceLabel(task.client.presence_status).toLowerCase() }})</span>
              </p>
              <div
                v-if="task.sub_status"
                class="mt-1.5 inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 font-medium"
              >
                {{ task.sub_status }}
              </div>
            </div>
            <button
              class="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 shrink-0"
              aria-label="Fermer le panneau"
              @click="$emit('close')"
            >
              <X class="w-5 h-5" aria-hidden="true" />
            </button>
          </div>

          <!-- Onglets -->
          <div class="flex border-b border-slate-200 dark:border-slate-700 shrink-0" role="tablist">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              role="tab"
              :aria-selected="activeTab === tab.id"
              :class="[
                'flex-1 py-2.5 text-sm font-medium transition-colors flex items-center justify-center gap-1.5',
                activeTab === tab.id
                  ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-500'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200',
              ]"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
              <span
                v-if="tab.id === 'comments' && task.comments.length"
                class="text-xs px-1.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 font-semibold"
              >
                {{ task.comments.length }}
              </span>
            </button>
          </div>

          <div class="flex-1 overflow-y-auto" role="tabpanel">
            <TaskEditForm
              v-if="activeTab === 'edit'"
              :task="task"
              @updated="onUpdated"
              @duplicate="$emit('duplicate', task)"
              @archived="onArchived"
            />
            <TaskComments
              v-else-if="activeTab === 'comments'"
              v-model:comments="task.comments"
              :task-id="task.id"
              @changed="historyVersion++"
            />
            <TaskHistory v-else :task-id="task.id" :version="historyVersion" />
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { X } from '@lucide/vue'
import { nextTick, ref, watch } from 'vue'
import StatusBadge from '../StatusBadge.vue'
import PriorityBadge from '../PriorityBadge.vue'
import TaskEditForm from './TaskEditForm.vue'
import TaskComments from './TaskComments.vue'
import TaskHistory from './TaskHistory.vue'
import { useTaskStore } from '../../stores/taskStore'
import { fullName, presenceColor, presenceLabel } from '../../utils/labels'
import { httpStatus } from '../../api/index'
import type { Task, TaskSummary } from '../../types/api'

const props = defineProps<{ taskId: string }>()
const emit = defineEmits<{ close: []; duplicate: [task: Task]; changed: [] }>()

const taskStore = useTaskStore()
const task = ref<Task | null>(null)
const loading = ref(true)
const panel = ref<HTMLElement | null>(null)
type Tab = 'edit' | 'comments' | 'history'
const activeTab = ref<Tab>('edit')
// Incrémenté à chaque modification pour recharger l'historique
const historyVersion = ref(0)

const tabs: { id: Tab; label: string }[] = [
  { id: 'edit', label: 'Modifier' },
  { id: 'comments', label: 'Commentaires' },
  { id: 'history', label: 'Historique' },
]

async function load() {
  loading.value = true
  try {
    task.value = await taskStore.fetchTask(props.taskId)
  } catch (error) {
    if (httpStatus(error) !== 404) throw error
    task.value = null
  } finally {
    loading.value = false
    await nextTick()
    panel.value?.focus()
  }
}

function onUpdated(updated: TaskSummary) {
  if (task.value) task.value = { ...task.value, ...updated }
  historyVersion.value++
  emit('changed')
}

function onArchived() {
  emit('changed')
  emit('close')
}

watch(
  () => props.taskId,
  () => {
    activeTab.value = 'edit'
    load()
  },
  { immediate: true },
)
</script>

<style scoped>
.slide-in {
  animation: slideIn 0.25s ease;
}
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
