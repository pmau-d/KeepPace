<template>
  <div class="p-5">
    <div v-if="loading" class="text-slate-400 text-sm animate-pulse">Chargement…</div>
    <div v-else-if="!logs.length" class="text-slate-400 text-sm py-8 text-center">Aucun historique.</div>
    <ol v-else class="relative pl-5">
      <div
        class="absolute left-[9px] top-1 bottom-1 w-px bg-slate-200 dark:bg-slate-700"
        aria-hidden="true"
      ></div>
      <li v-for="log in logs" :key="log.id" class="relative mb-4 last:mb-0">
        <div
          class="absolute -left-5 top-2 w-3 h-3 rounded-full bg-indigo-500 border-2 border-white dark:border-slate-800 shadow-sm"
        ></div>
        <div class="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-3">
          <p class="text-xs text-slate-400 mb-1.5">{{ formatDateTime(log.created_at) }}</p>
          <p class="text-sm text-slate-700 dark:text-slate-200 leading-snug break-words">
            <span class="font-semibold">{{ fieldLabel(log.field_changed) }}</span>
            <template v-if="formatLogValue(log, 'old')">
              <span class="text-slate-400 line-through mx-1">{{ formatLogValue(log, 'old') }}</span>
            </template>
            <span v-if="formatLogValue(log, 'old') && formatLogValue(log, 'new')" class="text-slate-400"
              >→</span
            >
            <span
              v-if="formatLogValue(log, 'new')"
              class="text-indigo-600 dark:text-indigo-400 font-medium ml-1"
            >
              {{ formatLogValue(log, 'new') }}
            </span>
          </p>
          <p v-if="log.comment" class="text-xs text-slate-500 mt-1.5 italic">{{ log.comment }}</p>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { tasksApi } from '../../api/index.js'
import { fieldLabel, formatDateTime, formatLogValue } from '../../utils/labels.js'

const props = defineProps({
  taskId: { type: String, required: true },
  // Changé par le parent pour forcer un rechargement après une modification
  version: { type: Number, default: 0 },
})

const logs = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    // Plus récent en premier
    logs.value = [...(await tasksApi.getLogs(props.taskId)).data].reverse()
  } finally {
    loading.value = false
  }
}

watch(() => [props.taskId, props.version], load, { immediate: true })
</script>
