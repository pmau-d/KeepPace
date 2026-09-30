<template>
  <header
    class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-5 py-3 flex items-center gap-3 flex-wrap flex-shrink-0"
  >
    <!-- Global search -->
    <div class="relative flex-1 min-w-48">
      <svg
        class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <input
        v-model="searchQuery"
        @input="handleSearch"
        type="text"
        placeholder="Rechercher une tâche..."
        class="w-full pl-9 pr-3 py-2 text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg focus:ring-2 focus:ring-indigo-500 placeholder-slate-400 transition"
      />
    </div>

    <!-- Status filter -->
    <select
      v-model="statusFilter"
      @change="handleStatusFilter"
      class="text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 cursor-pointer"
    >
      <option value="">Tous les statuts</option>
      <option value="TODO">À faire</option>
      <option value="IN_PROGRESS">En cours</option>
      <option value="BLOCKED">En attente Client</option>
    </select>

    <!-- Presence status filter -->
    <select
      v-model="presenceFilter"
      @change="handlePresenceFilter"
      class="text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 cursor-pointer"
    >
      <option value="">Toutes les présences</option>
      <option value="PRESENT">🟢 Présent</option>
      <option value="RECENTLY_BACK">🔵 Rentré récemment</option>
      <option value="SOON_BACK">🟡 Bientôt de retour</option>
      <option value="ABSENT">🔴 Absent</option>
    </select>

    <!-- Show done toggle -->
    <label class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 cursor-pointer select-none">
      <button
        type="button"
        @click="toggleShowDone"
        :class="[
          'relative w-10 h-5 rounded-full transition-colors flex-shrink-0',
          taskStore.filters.showDone ? 'bg-indigo-500' : 'bg-slate-300 dark:bg-slate-600',
        ]"
        role="switch"
        :aria-checked="taskStore.filters.showDone"
      >
        <span
          :class="[
            'absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200',
            taskStore.filters.showDone ? 'translate-x-5' : 'translate-x-0.5',
          ]"
        ></span>
      </button>
      <span>Tâches terminées</span>
    </label>

    <!-- Dark mode toggle -->
    <button
      @click="$emit('toggle-dark')"
      class="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
      :title="isDark ? 'Mode clair' : 'Mode sombre'"
    >
      <!-- Sun -->
      <svg v-if="isDark" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>
      <!-- Moon -->
      <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        />
      </svg>
    </button>

    <!-- New task button -->
    <button
      @click="$emit('open-create')"
      class="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium text-sm px-4 py-2 rounded-lg transition-colors shadow-sm"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
      </svg>
      Nouvelle tâche
    </button>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useTaskStore } from '../stores/taskStore.js'

defineProps({ isDark: Boolean })
defineEmits(['toggle-dark', 'open-create'])

const taskStore = useTaskStore()

const searchQuery = ref(taskStore.filters.search)
const statusFilter = ref(taskStore.filters.status || '')
const presenceFilter = ref(taskStore.filters.presenceStatus || '')

let searchTimeout = null

function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    taskStore.setFilter('search', searchQuery.value)
  }, 350)
}

function handleStatusFilter() {
  taskStore.setFilter('status', statusFilter.value || null)
}

function handlePresenceFilter() {
  taskStore.setFilter('presenceStatus', presenceFilter.value || null)
}

function toggleShowDone() {
  taskStore.setFilter('showDone', !taskStore.filters.showDone)
}
</script>



