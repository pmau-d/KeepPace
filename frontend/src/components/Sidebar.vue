<template>
  <aside
    :class="[
      'w-64 shrink-0 h-screen bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex-col',
      drawer ? 'relative flex shadow-2xl' : 'hidden lg:flex',
    ]"
    :aria-label="drawer ? 'Menu' : undefined"
  >
    <!-- Logo -->
    <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
      <div
        class="w-9 h-9 bg-linear-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center shadow-sm"
      >
        <span class="text-white font-bold text-sm">KP</span>
      </div>
      <div class="flex-1">
        <p class="font-bold text-base text-slate-800 dark:text-white leading-none">KeepPace</p>
        <p class="text-xs text-slate-400 mt-0.5">Tableau de bord consultant</p>
      </div>
      <button
        v-if="drawer"
        type="button"
        class="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
        aria-label="Fermer le menu"
        @click="$emit('navigate')"
      >
        <X class="w-5 h-5" aria-hidden="true" />
      </button>
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
        @click="onNavigate(item)"
      >
        <component :is="item.icon" class="w-4 h-4 shrink-0" aria-hidden="true" />
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- Clients -->
    <div class="flex-1 overflow-y-auto px-3 pb-4">
      <div class="flex items-center gap-1.5 mt-3 mb-2 px-2">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Clients</p>
        <InfoTooltip label="Légende des pastilles de présence">
          <p class="font-semibold text-slate-700 dark:text-slate-100 mb-2">Présence des clients</p>
          <ul class="space-y-1.5">
            <li v-for="(item, status) in PRESENCE" :key="status" class="flex items-center gap-2">
              <span :class="['w-2 h-2 rounded-full shrink-0', item.color]"></span>
              {{ item.label }}
            </li>
          </ul>
          <p class="mt-2 text-slate-400">Calculée à partir des dates d'absence de chaque client.</p>
        </InfoTooltip>
      </div>

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
              <Archive class="w-3.5 h-3.5" aria-hidden="true" />
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
              <span class="truncate flex-1">{{ fullName(client) }}</span>
              <span
                v-if="client.open_tasks_count"
                class="text-[11px] tabular-nums px-1.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 group-hover/client:hidden"
                :aria-label="`${client.open_tasks_count} tâche(s) ouverte(s)`"
              >
                {{ client.open_tasks_count }}
              </span>
            </button>
            <button
              class="opacity-0 group-hover/client:opacity-100 focus:opacity-100 p-1.5 rounded-sm text-slate-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all shrink-0"
              :aria-label="`Modifier ${fullName(client)}`"
              title="Modifier le client"
              @click="editingClient = client"
            >
              <Pencil class="w-3.5 h-3.5" aria-hidden="true" />
            </button>
            <button
              class="opacity-0 group-hover/client:opacity-100 focus:opacity-100 p-1.5 rounded-sm text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all shrink-0"
              :aria-label="`Archiver ${fullName(client)}`"
              title="Archiver le client"
              @click="handleArchiveClient(client)"
            >
              <Archive class="w-3.5 h-3.5" aria-hidden="true" />
            </button>
          </div>
        </div>

        <div v-if="clientStore.clients.length === 0" class="text-slate-400 text-xs px-2 py-4 text-center">
          <p>Aucun client pour l'instant.</p>
          <p class="mt-1">Créez-en un depuis « Nouvelle tâche ».</p>
        </div>
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
        <component :is="isDark ? Sun : Moon" class="w-4 h-4" aria-hidden="true" />
      </button>
      <button
        class="p-2 rounded-lg text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
        aria-label="Se déconnecter"
        title="Se déconnecter"
        @click="logout"
      >
        <LogOut class="w-4 h-4" aria-hidden="true" />
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

<script setup lang="ts">
import {
  Archive,
  CalendarRange,
  ListTodo,
  LogOut,
  Megaphone,
  Moon,
  Pencil,
  SquareKanban,
  Sun,
  X,
} from '@lucide/vue'
import { computed, ref, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EditClientModal from './EditClientModal.vue'
import InfoTooltip from './ui/InfoTooltip.vue'
import { confirm } from '../composables/useConfirm'
import { useDarkMode } from '../composables/useDarkMode'
import { useAuthStore } from '../stores/auth'
import { useClientStore } from '../stores/clientStore'
import { useTaskStore } from '../stores/taskStore'
import { useToastStore } from '../stores/toast'
import { PRESENCE, fullName, presenceColor, presenceLabel } from '../utils/labels'
import type { Client } from '../types/api'

interface NavItem {
  name: string
  label: string
  icon: Component
  matches: string[]
}

interface CompanyGroup {
  companyId: string
  name: string
  clients: Client[]
}

withDefaults(defineProps<{ drawer?: boolean }>(), { drawer: false })
const emit = defineEmits<{ navigate: [] }>()

const auth = useAuthStore()
const clientStore = useClientStore()
const taskStore = useTaskStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()
const { isDark, toggle: toggleDark } = useDarkMode()

const editingClient = ref<Client | null>(null)

const navigation: NavItem[] = [
  { name: 'tasks', label: 'Toutes les tâches', icon: ListTodo, matches: ['tasks', 'task'] },
  { name: 'board', label: 'Tableau', icon: SquareKanban, matches: ['board'] },
  { name: 'follow-up', label: 'À relancer', icon: Megaphone, matches: ['follow-up'] },
  { name: 'planning', label: 'Planning', icon: CalendarRange, matches: ['planning'] },
  { name: 'archives', label: 'Archives', icon: Archive, matches: ['archives'] },
]

function isActive(item: NavItem) {
  return item.matches.includes(String(route.name)) && !(item.name === 'tasks' && taskStore.filters.clientId)
}

const groupedClients = computed(() => {
  const groups = new Map<string, CompanyGroup>()
  for (const client of clientStore.clients) {
    let group = groups.get(client.company_id)
    if (!group) {
      group = { companyId: client.company_id, name: client.company.name, clients: [] }
      groups.set(client.company_id, group)
    }
    group.clients.push(client)
  }
  for (const group of groups.values()) group.clients.sort((a, b) => fullName(a).localeCompare(fullName(b)))
  return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name))
})

async function selectClient(clientId: string | null) {
  emit('navigate')
  if (route.name !== 'tasks' && route.name !== 'task') await router.push({ name: 'tasks' })
  await taskStore.setClientFilter(clientId)
}

function onNavigate(item: NavItem) {
  if (item.name === 'tasks' && taskStore.filters.clientId) void selectClient(null)
  else emit('navigate')
}

function clearClientFilterIf(clientIds: string[]) {
  if (taskStore.filters.clientId && clientIds.includes(taskStore.filters.clientId))
    taskStore.filters.clientId = null
}

async function handleArchiveClient(client: Client) {
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

async function handleArchiveCompany(group: CompanyGroup) {
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
