<template>
  <header
    class="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4 shrink-0"
  >
    <h1 class="text-lg font-semibold text-slate-800 dark:text-slate-100">Archives</h1>
    <p class="text-sm text-slate-400">
      Rien n'est jamais effacé : restaurez un élément pour le remettre dans vos listes, avec son historique.
    </p>
  </header>

  <main class="flex-1 overflow-y-auto p-6 space-y-8">
    <div v-if="loading" class="flex justify-center items-center h-40">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else>
      <section v-for="section in sections" :key="section.key">
        <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
          {{ section.title }} <span class="text-slate-400 font-normal">· {{ section.items.length }}</span>
        </h2>
        <p v-if="!section.items.length" class="text-sm text-slate-400">Aucun élément archivé.</p>
        <ul
          v-else
          class="divide-y divide-slate-100 dark:divide-slate-700 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700"
        >
          <li v-for="item in section.items" :key="item.id" class="flex items-center gap-3 px-4 py-3">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">
                {{ section.title_of(item) }}
              </p>
              <p class="text-xs text-slate-400 truncate">
                {{ section.subtitle_of(item) }}
                <template v-if="item.archived_at">
                  · archivé le {{ formatDateTime(item.archived_at) }}</template
                >
              </p>
            </div>
            <button
              :disabled="restoring === item.id"
              class="text-sm px-3 py-1.5 rounded-lg border border-indigo-200 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 disabled:opacity-50"
              @click="restore(section, item)"
            >
              Restaurer
            </button>
          </li>
        </ul>
      </section>
    </template>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { clientsApi, companiesApi, tasksApi } from '../api/index'
import { useClientStore } from '../stores/clientStore'
import { useToastStore } from '../stores/toast'
import { formatDateTime, fullName } from '../utils/labels'
import type { Client, Company, TaskSummary } from '../types/api'

interface Archived {
  id: string
  archived_at: string | null
}

interface Section<T extends Archived = Archived> {
  key: string
  title: string
  items: T[]
  title_of: (item: T) => string
  subtitle_of: (item: T) => string
  restore: (item: T) => Promise<unknown>
}

/** Garde le typage précis de chaque section tout en les listant ensemble. */
function defineSection<T extends Archived>(value: Section<T>): Section {
  return value as unknown as Section
}

const clientStore = useClientStore()
const toast = useToastStore()

const tasks = ref<TaskSummary[]>([])
const clients = ref<Client[]>([])
const companies = ref<Company[]>([])
const loading = ref(true)
const restoring = ref<string | null>(null)

const sections = computed<Section[]>(() => [
  defineSection<Company>({
    key: 'companies',
    title: 'Entreprises',
    items: companies.value,
    title_of: (c) => c.name,
    subtitle_of: () => 'Restaure aussi les clients et tâches archivés avec elle',
    restore: (c) => companiesApi.restore(c.id),
  }),
  defineSection<Client>({
    key: 'clients',
    title: 'Clients',
    items: clients.value,
    title_of: (c) => fullName(c),
    subtitle_of: (c) => c.company.name,
    restore: (c) => clientsApi.restore(c.id),
  }),
  defineSection<TaskSummary>({
    key: 'tasks',
    title: 'Tâches',
    items: tasks.value,
    title_of: (t) => t.title,
    subtitle_of: (t) => `${fullName(t.client)} · ${t.client.company.name}`,
    restore: (t) => tasksApi.restore(t.id),
  }),
])

async function load() {
  loading.value = true
  try {
    const [t, cl, co] = await Promise.all([
      tasksApi.list({ archived: true, show_done: true, limit: 200 }),
      clientsApi.getAll({ archived: true }),
      companiesApi.getAll({ archived: true }),
    ])
    tasks.value = t.data.items
    clients.value = cl.data
    companies.value = co.data
  } finally {
    loading.value = false
  }
}

async function restore(target: Section, item: Archived) {
  restoring.value = item.id
  try {
    await target.restore(item)
    toast.success(`« ${target.title_of(item)} » restauré.`)
    await Promise.all([load(), clientStore.fetchAll()])
  } catch (error) {
    // 409 : le parent (client ou entreprise) est lui-même archivé
    toast.error(error, 'Restauration impossible.')
  } finally {
    restoring.value = null
  }
}

onMounted(load)
</script>
