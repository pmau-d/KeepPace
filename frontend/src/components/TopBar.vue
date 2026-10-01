<template>
  <header
    class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-5 py-3 flex items-center gap-3 flex-wrap shrink-0"
  >
    <!-- Recherche -->
    <div class="relative flex-1 min-w-48">
      <label for="task-search" class="sr-only">Rechercher une tâche</label>
      <Search
        class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none"
        aria-hidden="true"
      />
      <input
        id="task-search"
        v-model="searchQuery"
        type="search"
        placeholder="Rechercher (titre, description, commentaires)…"
        class="w-full pl-9 pr-3 py-2 text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg focus:ring-2 focus:ring-indigo-500 placeholder-slate-400 transition"
        @input="handleSearch"
      />
    </div>

    <label for="status-filter" class="sr-only">Statut</label>
    <BaseSelect
      id="status-filter"
      v-model="statusFilter"
      :options="[{ value: '', label: 'Tous les statuts' }, ...STATUS_OPTIONS]"
      @change="taskStore.setFilter('status', statusFilter || null)"
    />

    <label for="presence-filter" class="sr-only">Présence du client</label>
    <BaseSelect
      id="presence-filter"
      v-model="presenceFilter"
      :options="[{ value: '', label: 'Toutes les présences' }, ...PRESENCE_OPTIONS]"
      @change="taskStore.setFilter('presenceStatus', presenceFilter || null)"
    />

    <div class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 select-none">
      <button
        id="show-done"
        type="button"
        role="switch"
        :aria-checked="taskStore.filters.showDone"
        :class="[
          'relative w-10 h-5 rounded-full transition-colors shrink-0',
          taskStore.filters.showDone ? 'bg-indigo-500' : 'bg-slate-300 dark:bg-slate-600',
        ]"
        @click="taskStore.setFilter('showDone', !taskStore.filters.showDone)"
      >
        <span
          :class="[
            'absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform duration-200',
            taskStore.filters.showDone ? 'translate-x-5' : 'translate-x-0.5',
          ]"
        ></span>
      </button>
      <label for="show-done" class="cursor-pointer">Terminées</label>
    </div>

    <!-- Export CSV des tâches filtrées -->
    <a
      :href="exportUrl"
      download
      class="flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
      title="Exporter les tâches affichées (CSV, compatible Excel)"
    >
      <Download class="w-4 h-4" aria-hidden="true" />
      CSV
    </a>

    <button
      class="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors shadow-xs"
      @click="$emit('open-create')"
    >
      <Plus class="w-4 h-4" aria-hidden="true" />
      Nouvelle tâche
    </button>
  </header>
</template>

<script setup lang="ts">
import { Download, Plus, Search } from 'lucide-vue-next'
import { computed, onBeforeUnmount, ref } from 'vue'
import { tasksApi } from '../api/index'
import { useTaskStore } from '../stores/taskStore'
import BaseSelect from './ui/BaseSelect.vue'
import { PRESENCE_OPTIONS, STATUS_OPTIONS } from '../utils/options'
import type { PresenceStatus, TaskStatus } from '../types/api'

defineEmits<{ 'open-create': [] }>()

const taskStore = useTaskStore()

const searchQuery = ref(taskStore.filters.search)
const statusFilter = ref<TaskStatus | ''>(taskStore.filters.status || '')
const presenceFilter = ref<PresenceStatus | ''>(taskStore.filters.presenceStatus || '')
const exportUrl = computed(() => tasksApi.exportUrl(taskStore.queryParams()))

let searchTimeout: ReturnType<typeof setTimeout> | undefined

function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => taskStore.setFilter('search', searchQuery.value), 300)
}

onBeforeUnmount(() => clearTimeout(searchTimeout))
</script>
