<template>
  <aside
    class="w-64 flex-shrink-0 h-screen bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col"
  >
    <!-- Logo -->
    <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
      <div
        class="w-9 h-9 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center shadow"
      >
        <span class="text-white font-bold text-sm">KP</span>
      </div>
      <div>
        <p class="font-bold text-base text-slate-800 dark:text-white leading-none">KeepPace</p>
        <p class="text-xs text-slate-400 mt-0.5">Consultant dashboard</p>
      </div>
    </div>

    <!-- All tasks button -->
    <div class="px-3 pt-3 pb-1">
      <button
        @click="selectClient(null)"
        :class="[
          'w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
          activeClientId === null
            ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700/50',
        ]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 10h16M4 14h16M4 18h16"
          />
        </svg>
        Toutes les tâches
      </button>
    </div>

    <!-- Client list -->
    <div class="flex-1 overflow-y-auto px-3 pb-4">
      <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mt-3 mb-2 px-2">
        Clients
      </p>

      <div v-if="clientStore.loading" class="text-slate-400 text-xs px-2 py-2">
        Chargement...
      </div>

      <div v-else>
          <div v-for="group in groupedClients" :key="group.name" class="mb-3">
            <div class="flex items-center justify-between px-2 mb-1 group/company">
              <p class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider truncate">
                {{ group.name }}
              </p>
              <button
                @click="handleDeleteCompany(group)"
                class="opacity-0 group-hover/company:opacity-100 p-0.5 rounded text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
                title="Supprimer l'entreprise"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
            <div
              v-for="client in group.clients"
              :key="client.id"
              class="group/client flex items-center gap-0.5"
            >
              <button
                @click="selectClient(client.id)"
                :class="[
                  'flex-1 text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2.5 transition-colors',
                  activeClientId === client.id
                    ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50',
                ]"
              >
                <span
                  :class="[
                    'w-2.5 h-2.5 rounded-full flex-shrink-0 ring-2 ring-white dark:ring-slate-800',
                    clientStore.presenceColor(client.presence_status),
                  ]"
                ></span>
                <span class="truncate">{{ clientStore.fullName(client) }}</span>
              </button>
              <!-- Edit button -->
              <button
                @click="editingClient = client"
                class="opacity-0 group-hover/client:opacity-100 p-1.5 rounded text-slate-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all flex-shrink-0"
                title="Modifier le client"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <!-- Delete button -->
              <button
                @click="handleDeleteClient(client)"
                class="opacity-0 group-hover/client:opacity-100 p-1.5 rounded text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all flex-shrink-0"
                title="Supprimer le client"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
        </div>

        <div v-if="clientStore.clients.length === 0" class="text-slate-400 text-xs px-2 py-4 text-center">
          <p>Aucun client enregistré</p>
        </div>
      </div>
    </div>

    <!-- Presence legend -->
    <div class="p-3 border-t border-slate-200 dark:border-slate-700 space-y-1">
      <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Légende</p>
      <div v-for="item in presenceLegend" :key="item.status" class="flex items-center gap-2">
        <span :class="['w-2 h-2 rounded-full flex-shrink-0', item.color]"></span>
        <span class="text-xs text-slate-500 dark:text-slate-400">{{ item.label }}</span>
      </div>
    </div>
  </aside>

  <!-- Edit client modal -->
  <EditClientModal
    v-if="editingClient"
    :client="editingClient"
    @close="editingClient = null"
    @updated="handleClientUpdated"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useClientStore } from '../stores/clientStore.js'
import { useTaskStore } from '../stores/taskStore.js'
import EditClientModal from './EditClientModal.vue'

const clientStore = useClientStore()
const taskStore = useTaskStore()

const activeClientId = ref(null)
const editingClient = ref(null)

const groupedClients = computed(() => {
  const groups = {}
  for (const c of clientStore.clients) {
    const name = c.company.name
    if (!groups[name]) groups[name] = { name, companyId: c.company_id, clients: [] }
    groups[name].clients.push(c)
  }
  return Object.values(groups).sort((a, b) => a.name.localeCompare(b.name))
})

const presenceLegend = [
  { status: 'PRESENT', color: 'bg-green-500', label: 'Présent' },
  { status: 'RECENTLY_BACK', color: 'bg-blue-500', label: 'Rentré récemment' },
  { status: 'SOON_BACK', color: 'bg-yellow-400', label: 'Bientôt de retour' },
  { status: 'ABSENT', color: 'bg-red-500', label: 'Absent' },
]

function selectClient(id) {
  if (activeClientId.value === id) {
    activeClientId.value = null
    taskStore.setClientFilter(null)
  } else {
    activeClientId.value = id
    taskStore.setClientFilter(id)
  }
}

async function handleDeleteClient(client) {
  if (!window.confirm(`Supprimer ${clientStore.fullName(client)} et toutes ses tâches ?`)) return
  if (activeClientId.value === client.id) {
    activeClientId.value = null
    taskStore.setClientFilter(null)
  }
  await clientStore.deleteClient(client.id)
  await taskStore.fetchTasks()
}

async function handleDeleteCompany(group) {
  if (!window.confirm(`Supprimer l'entreprise "${group.name}" et tous ses clients/tâches ?`)) return
  await clientStore.deleteCompany(group.companyId)
  if (group.clients.some(c => c.id === activeClientId.value)) {
    activeClientId.value = null
    taskStore.setClientFilter(null)
  }
  await taskStore.fetchTasks()
}

function handleClientUpdated() {
  editingClient.value = null
  taskStore.fetchTasks()
}
</script>

