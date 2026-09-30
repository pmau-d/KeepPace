<template>
  <aside
    class="w-64 shrink-0 h-screen bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col"
  >
    <!-- Logo -->
    <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
      <div
        class="w-9 h-9 bg-linear-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center shadow-sm"
      >
        <span class="text-white font-bold text-sm">KP</span>
      </div>
      <div>
        <p class="font-bold text-base text-slate-800 dark:text-white leading-none">KeepPace</p>
        <p class="text-xs text-slate-400 mt-0.5">Tableau de bord consultant</p>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="px-3 pt-3 pb-1 space-y-0.5" aria-label="Navigation principale">
      <RouterLink
        v-for="item in navigation"
        :key="item.name"
        :to="{ name: item.name }"
        :class="[
          'w-full px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2',
          isActive(item)
            ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700/50',
        ]"
        @click="item.name === 'tasks' && taskStore.filters.clientId && selectClient(null)"
      >
        <span aria-hidden="true">{{ item.icon }}</span>
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- Clients -->
    <div class="flex-1 overflow-y-auto px-3 pb-4">
      <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mt-3 mb-2 px-2">Clients</p>

      <div v-if="clientStore.loading && !clientStore.clients.length" class="text-slate-400 text-xs px-2 py-2">
        Chargement…
      </div>

      <div v-else>
        <div v-for="group in groupedClients" :key="group.companyId" class="mb-3">
          <div class="flex items-center justify-between px-2 mb-1 group/company">
            <p
              class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider truncate"
            >
              {{ group.name }}
            </p>
            <button
              class="opacity-0 group-hover/company:opacity-100 focus:opacity-100 p-0.5 rounded-sm text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
              :aria-label="`Archiver l'entreprise ${group.name}`"
              title="Archiver l'entreprise"
              @click="handleArchiveCompany(group)"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons.archive" />
              </svg>
            </button>
          </div>
          <div
            v-for="client in group.clients"
            :key="client.id"
            class="group/client flex items-center gap-0.5"
          >
            <button
              :class="[
                'flex-1 min-w-0 text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2.5 transition-colors',
                taskStore.filters.clientId === client.id
                  ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50',
              ]"
              :aria-pressed="taskStore.filters.clientId === client.id"
              :title="presenceLabel(client.presence_status)"
              @click="selectClient(client.id)"
            >
              <span
                :class="[
                  'w-2.5 h-2.5 rounded-full shrink-0 ring-2 ring-white dark:ring-slate-800',
                  presenceColor(client.presence_status),
                ]"
              ></span>
              <span class="truncate">{{ fullName(client) }}</span>
            </button>
            <button
              class="opacity-0 group-hover/client:opacity-100 focus:opacity-100 p-1.5 rounded-sm text-slate-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all shrink-0"
              :aria-label="`Modifier ${fullName(client)}`"
              title="Modifier le client"
              @click="editingClient = client"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons.edit" />
              </svg>
            </button>
            <button
              class="opacity-0 group-hover/client:opacity-100 focus:opacity-100 p-1.5 rounded-sm text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all shrink-0"
              :aria-label="`Archiver ${fullName(client)}`"
              title="Archiver le client"
              @click="handleArchiveClient(client)"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons.archive" />
              </svg>
            </button>
          </div>
        </div>

        <div v-if="clientStore.clients.length === 0" class="text-slate-400 text-xs px-2 py-4 text-center">
          <p>Aucun client pour l'instant.</p>
          <p class="mt-1">Créez-en un depuis « Nouvelle tâche ».</p>
        </div>
      </div>
    </div>

    <!-- Légende -->
    <div class="px-4 py-3 border-t border-slate-200 dark:border-slate-700 space-y-1">
      <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Présence</p>
      <div v-for="(item, status) in PRESENCE" :key="status" class="flex items-center gap-2">
        <span :class="['w-2 h-2 rounded-full shrink-0', item.color]"></span>
        <span class="text-xs text-slate-500 dark:text-slate-400">{{ item.label }}</span>
      </div>
    </div>

    <!-- Compte -->
    <div class="p-3 border-t border-slate-200 dark:border-slate-700 flex items-center gap-2">
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">
          {{ auth.user?.full_name || auth.user?.email }}
        </p>
        <p v-if="auth.user?.full_name" class="text-xs text-slate-400 truncate">{{ auth.user.email }}</p>
      </div>
      <button
        class="p-2 rounded-lg text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
        :aria-label="isDark ? 'Passer en mode clair' : 'Passer en mode sombre'"
        :title="isDark ? 'Mode clair' : 'Mode sombre'"
        @click="toggleDark"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            :d="isDark ? icons.sun : icons.moon"
          />
        </svg>
      </button>
      <button
        class="p-2 rounded-lg text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
        aria-label="Se déconnecter"
        title="Se déconnecter"
        @click="logout"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons.logout" />
        </svg>
      </button>
    </div>
  </aside>

  <EditClientModal
    v-if="editingClient"
    :client="editingClient"
    @close="editingClient = null"
    @updated="handleClientUpdated"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EditClientModal from './EditClientModal.vue'
import { confirm } from '../composables/useConfirm.js'
import { useDarkMode } from '../composables/useDarkMode.js'
import { useAuthStore } from '../stores/auth.js'
import { useClientStore } from '../stores/clientStore.js'
import { useTaskStore } from '../stores/taskStore.js'
import { useToastStore } from '../stores/toast.js'
import { PRESENCE, fullName, presenceColor, presenceLabel } from '../utils/labels.js'

const auth = useAuthStore()
const clientStore = useClientStore()
const taskStore = useTaskStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()
const { isDark, toggle: toggleDark } = useDarkMode()

const editingClient = ref(null)

const navigation = [
  { name: 'tasks', label: 'Toutes les tâches', icon: '☰', matches: ['tasks', 'task'] },
  { name: 'follow-up', label: 'À relancer', icon: '📣', matches: ['follow-up'] },
  { name: 'archives', label: 'Archives', icon: '🗄️', matches: ['archives'] },
]

const icons = {
  archive: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4',
  edit: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
  sun: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 11-8 0 4 4 0 018 0z',
  moon: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z',
  logout: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1',
}

function isActive(item) {
  return item.matches.includes(route.name) && !(item.name === 'tasks' && taskStore.filters.clientId)
}

const groupedClients = computed(() => {
  const groups = new Map()
  for (const client of clientStore.clients) {
    if (!groups.has(client.company_id)) {
      groups.set(client.company_id, { companyId: client.company_id, name: client.company.name, clients: [] })
    }
    groups.get(client.company_id).clients.push(client)
  }
  for (const group of groups.values()) group.clients.sort((a, b) => fullName(a).localeCompare(fullName(b)))
  return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name))
})

async function selectClient(clientId) {
  if (route.name !== 'tasks' && route.name !== 'task') await router.push({ name: 'tasks' })
  await taskStore.setClientFilter(clientId)
}

function clearClientFilterIf(clientIds) {
  if (clientIds.includes(taskStore.filters.clientId)) taskStore.filters.clientId = null
}

async function handleArchiveClient(client) {
  const ok = await confirm({
    title: `Archiver ${fullName(client)} ?`,
    message:
      'Le client et ses tâches ouvertes sont archivés. Vous pourrez les restaurer depuis les Archives.',
    confirmLabel: 'Archiver',
    danger: true,
  })
  if (!ok) return
  await clientStore.archiveClient(client.id)
  clearClientFilterIf([client.id])
  await taskStore.fetchTasks()
  toast.success(`${fullName(client)} archivé.`, {
    action: {
      label: 'Annuler',
      run: async () => {
        await clientStore.restoreClient(client.id)
        await taskStore.fetchTasks()
      },
    },
  })
}

async function handleArchiveCompany(group) {
  const ok = await confirm({
    title: `Archiver l'entreprise « ${group.name} » ?`,
    message: `Ses ${group.clients.length} client(s) et leurs tâches seront archivés, sans perte d'historique.`,
    confirmLabel: 'Archiver',
    danger: true,
  })
  if (!ok) return
  await clientStore.archiveCompany(group.companyId)
  clearClientFilterIf(group.clients.map((c) => c.id))
  await taskStore.fetchTasks()
  toast.success(`Entreprise « ${group.name} » archivée.`, {
    action: {
      label: 'Annuler',
      run: async () => {
        await clientStore.restoreCompany(group.companyId)
        await taskStore.fetchTasks()
      },
    },
  })
}

function handleClientUpdated() {
  editingClient.value = null
  taskStore.fetchTasks()
}

async function logout() {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>
