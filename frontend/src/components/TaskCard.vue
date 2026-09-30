<template>
  <div
    :class="[
      'group grid grid-cols-1 md:grid-cols-[16px_1fr_180px_110px_100px] gap-3 items-center px-4 py-3 rounded-lg border border-slate-100 dark:border-slate-700/60 bg-white dark:bg-slate-800 cursor-pointer hover:shadow-xs hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-150 select-none relative',
      isAbsent ? 'opacity-50' : '',
      isDone ? 'opacity-60' : '',
    ]"
    @click="$emit('click')"
  >
    <!-- Priority strip (colored dot) -->
    <span
      :class="['w-2.5 h-2.5 rounded-full shrink-0 mx-auto', priorityDotClass]"
      :title="priorityLabel"
    ></span>

    <!-- Title + description + sub-status -->
    <div class="min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <span
          :class="[
            'font-semibold text-sm leading-snug',
            isDone ? 'line-through text-slate-400 dark:text-slate-500' : 'text-slate-800 dark:text-slate-100',
          ]"
          >{{ task.title }}</span
        >

        <!-- DONE ribbon -->
        <span
          v-if="isDone"
          class="text-[10px] font-bold px-1.5 py-0.5 rounded-sm bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400"
        >
          FERMÉ
        </span>

        <!-- Sub-status chip -->
        <span
          v-if="task.sub_status"
          class="text-[10px] px-1.5 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 font-medium whitespace-nowrap"
          >{{ task.sub_status }}</span
        >
      </div>

      <!-- Description -->
      <p v-if="task.description" class="text-xs text-slate-400 dark:text-slate-500 truncate mt-0.5">
        {{ task.description }}
      </p>
    </div>

    <!-- Client · Company -->
    <div class="flex items-center gap-1.5 min-w-0">
      <span :class="['w-2 h-2 rounded-full shrink-0', presenceColor]"></span>
      <span class="text-xs text-slate-500 dark:text-slate-400 truncate">
        {{ clientStore.fullName(task.client) }}
        <span class="text-slate-300 dark:text-slate-600 mx-0.5">·</span>
        {{ task.client.company.name }}
      </span>
    </div>

    <!-- Due date -->
    <div>
      <span
        v-if="task.due_date"
        :class="[
          'text-xs font-medium flex items-center gap-1',
          isOverdue ? 'text-red-500' : 'text-slate-500 dark:text-slate-400',
        ]"
      >
        <svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        {{ formatDate(task.due_date) }}
      </span>
      <span v-else class="text-xs text-slate-300 dark:text-slate-600">—</span>
    </div>

    <!-- Status + reopen -->
    <div class="flex items-center gap-1.5">
      <button
        v-if="isDone"
        :disabled="reopening"
        class="text-xs flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-700 hover:bg-blue-100 transition-colors disabled:opacity-50 font-medium whitespace-nowrap"
        @click.stop="handleReopen"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        {{ reopening ? '…' : 'Réouvrir' }}
      </button>
      <StatusBadge v-else :status="task.status" />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import StatusBadge from './StatusBadge.vue'
import { useClientStore } from '../stores/clientStore.js'
import { useTaskStore } from '../stores/taskStore.js'

const props = defineProps({ task: { type: Object, required: true } })
defineEmits(['click'])

const clientStore = useClientStore()
const taskStore = useTaskStore()
const reopening = ref(false)

const isDone = computed(() => props.task.status === 'DONE')
const isAbsent = computed(() => props.task.client.presence_status === 'ABSENT')
const presenceColor = computed(() => clientStore.presenceColor(props.task.client.presence_status))

const isOverdue = computed(() => {
  if (!props.task.due_date || isDone.value) return false
  return new Date(props.task.due_date) < new Date()
})

const priorityDotClass = computed(
  () =>
    ({
      HIGH: 'bg-red-500',
      MEDIUM: 'bg-amber-400',
      LOW: 'bg-green-500',
    })[props.task.priority] ?? 'bg-slate-300',
)

const priorityLabel = computed(
  () =>
    ({
      HIGH: 'Haute priorité',
      MEDIUM: 'Priorité moyenne',
      LOW: 'Basse priorité',
    })[props.task.priority] ?? '',
)

async function handleReopen() {
  reopening.value = true
  try {
    await taskStore.reopenTask(props.task.id)
  } finally {
    reopening.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}
</script>
