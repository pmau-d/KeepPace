<template>
  <header
    class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4 flex flex-wrap items-center gap-4 justify-between shrink-0"
  >
    <div>
      <h1 class="text-lg font-semibold text-slate-800 dark:text-slate-100">Tableau</h1>
      <p class="text-sm text-slate-400">
        Glissez une tâche d'une colonne à l'autre pour changer son statut (ou ← → au clavier).
      </p>
    </div>
    <button
      type="button"
      :disabled="loading"
      class="text-sm px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 disabled:opacity-50"
      @click="load"
    >
      Actualiser
    </button>
  </header>

  <main class="flex-1 overflow-x-auto overflow-y-hidden p-6">
    <div class="flex gap-4 h-full">
      <section
        v-for="column in columns"
        :key="column.status"
        :aria-labelledby="`column-${column.status}`"
        :class="[
          'flex-1 min-w-64 max-w-sm flex flex-col rounded-xl border transition-colors',
          dropTarget === column.status
            ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-300 dark:border-indigo-700'
            : 'bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700',
        ]"
        @dragover.prevent="dropTarget = column.status"
        @dragleave="onDragLeave($event, column.status)"
        @drop.prevent="onDrop(column.status)"
      >
        <h2
          :id="`column-${column.status}`"
          class="flex items-center gap-2 px-4 py-3 text-sm font-semibold text-slate-700 dark:text-slate-200"
        >
          <StatusBadge :status="column.status" />
          <span class="text-slate-400 font-normal">{{ column.tasks.length }}</span>
          <span v-if="column.status === 'DONE'" class="text-xs text-slate-400 font-normal ml-auto">
            {{ DONE_DAYS }} derniers jours
          </span>
        </h2>

        <ul class="flex-1 overflow-y-auto px-3 pb-3 space-y-2" role="list">
          <li
            v-for="task in column.tasks"
            :key="task.id"
            :draggable="!moving"
            :data-task-id="task.id"
            tabindex="0"
            :aria-label="`${task.title}, ${fullName(task.client)}. Entrée pour ouvrir, flèches gauche et droite pour changer de colonne.`"
            :class="[
              'group p-3 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xs cursor-grab active:cursor-grabbing focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 hover:border-slate-300 dark:hover:border-slate-600',
              dragging === task.id && 'opacity-40',
            ]"
            @dragstart="onDragStart($event, task)"
            @dragend="onDragEnd"
            @click="selectedId = task.id"
            @keydown.enter.prevent="selectedId = task.id"
            @keydown.left.prevent="moveBy(task, -1)"
            @keydown.right.prevent="moveBy(task, 1)"
          >
            <div class="flex items-start gap-2">
              <PriorityFlag :priority="task.priority" class="mt-0.5" />
              <p
                :class="[
                  'text-sm font-medium leading-snug flex-1',
                  task.status === 'DONE'
                    ? 'line-through text-slate-400'
                    : 'text-slate-800 dark:text-slate-100',
                ]"
              >
                {{ task.title }}
              </p>
            </div>
            <p v-if="task.sub_status" class="mt-1.5 ml-5.5">
              <span
                class="text-[10px] px-1.5 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 font-medium"
                >{{ task.sub_status }}</span
              >
            </p>
            <div
              class="flex items-center gap-1.5 mt-2 ml-5.5 text-xs text-slate-500 dark:text-slate-400 min-w-0"
            >
              <span
                :class="['w-2 h-2 rounded-full shrink-0', presenceColor(task.client.presence_status)]"
              ></span>
              <span class="truncate">{{ fullName(task.client) }}</span>
              <span
                v-if="task.due_date"
                :class="['ml-auto whitespace-nowrap', isOverdue(task) && 'text-red-500 font-medium']"
              >
                {{ dueLabel(task) }}
              </span>
            </div>
          </li>
          <li
            v-if="!column.tasks.length"
            class="text-xs text-slate-400 text-center py-6 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg"
          >
            Déposez une tâche ici
          </li>
        </ul>
      </section>
    </div>
    <p class="sr-only" aria-live="polite">{{ announcement }}</p>
  </main>

  <TaskSlideOver v-if="selectedId" :task-id="selectedId" @close="selectedId = null" @changed="load" />
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { tasksApi } from '../api/index'
import PriorityFlag from '../components/PriorityFlag.vue'
import StatusBadge from '../components/StatusBadge.vue'
import TaskSlideOver from '../components/task/TaskSlideOver.vue'
import { useToastStore } from '../stores/toast'
import { formatCompactDate, parseIsoDate, startOfDay } from '../utils/dates'
import { STATUS_LABELS, fullName, presenceColor } from '../utils/labels'
import { BOARD_STATUSES, boardColumns, DONE_DAYS, moveTask } from '../utils/board'
import type { TaskStatus, TaskSummary } from '../types/api'

const toast = useToastStore()
const tasks = ref<TaskSummary[]>([])
const loading = ref(false)
const moving = ref(false)
const dragging = ref<string | null>(null)
const dropTarget = ref<TaskStatus | null>(null)
const selectedId = ref<string | null>(null)
const announcement = ref('')

const columns = computed(() => boardColumns(tasks.value, new Date()))

function dueLabel(task: TaskSummary) {
  const due = parseIsoDate(task.due_date)
  return due ? formatCompactDate(due) : ''
}

function isOverdue(task: TaskSummary) {
  const due = parseIsoDate(task.due_date)
  return task.status !== 'DONE' && due !== null && due < startOfDay(new Date())
}

function onDragStart(event: DragEvent, task: TaskSummary) {
  dragging.value = task.id
  event.dataTransfer?.setData('text/plain', task.id)
  if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move'
}

function onDragEnd() {
  dragging.value = null
  dropTarget.value = null
}

function onDragLeave(event: DragEvent, status: TaskStatus) {
  // Survoler une carte de la colonne déclenche dragleave : on ne réagit qu'en sortant de la colonne.
  const section = event.currentTarget as HTMLElement
  if (!section.contains(event.relatedTarget as Node | null) && dropTarget.value === status)
    dropTarget.value = null
}

async function onDrop(status: TaskStatus) {
  const task = tasks.value.find((t) => t.id === dragging.value)
  onDragEnd()
  if (task) await move(task, status)
}

async function moveBy(task: TaskSummary, step: number) {
  const target = BOARD_STATUSES[BOARD_STATUSES.indexOf(task.status) + step]
  if (!target) return
  await move(task, target)
  // La carte a changé de colonne : on lui rend le focus pour enchaîner au clavier.
  await nextTick()
  document.querySelector<HTMLElement>(`[data-task-id="${task.id}"]`)?.focus()
}

async function move(task: TaskSummary, status: TaskStatus) {
  if (task.status === status || moving.value) return
  const previous = task.status
  moving.value = true
  // Mise à jour optimiste : la carte change de colonne tout de suite.
  task.status = status
  try {
    const updated = await moveTask(task.id, previous, status)
    Object.assign(task, updated)
    announcement.value = `« ${task.title} » déplacée dans ${STATUS_LABELS[status]}.`
    // Terminer une tâche récurrente crée la suivante : on recharge pour l'afficher.
    if (status === 'DONE' && task.recurrence) await load()
  } catch (error) {
    task.status = previous
    toast.error(error, 'Impossible de changer le statut.')
  } finally {
    moving.value = false
  }
}

async function load() {
  loading.value = true
  try {
    const { data } = await tasksApi.list({ show_done: true, limit: 200, offset: 0 })
    tasks.value = data.items
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
