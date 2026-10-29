<template>
  <main class="flex-1 overflow-y-auto">
    <div class="max-w-6xl mx-auto px-5 py-8">
      <header class="mb-6">
        <p class="text-sm text-slate-400">{{ today }}</p>
        <h1 class="text-2xl font-bold tracking-tight text-slate-800 dark:text-slate-100">
          Bonjour {{ firstName }}
        </h1>
      </header>

      <p v-if="error" class="text-sm text-red-500" role="alert">{{ error }}</p>
      <div v-else-if="loading" class="flex justify-center py-24">
        <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <template v-else>
        <!-- Chiffres du jour -->
        <ul class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
          <li v-for="stat in stats" :key="stat.label">
            <RouterLink
              :to="stat.to"
              class="block bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-4 shadow-xs hover:shadow-md hover:border-indigo-300 dark:hover:border-indigo-500/50 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            >
              <span class="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
                <component :is="stat.icon" :class="['w-4 h-4', stat.tone]" aria-hidden="true" />
                {{ stat.label }}
              </span>
              <span class="mt-2 block text-3xl font-bold tabular-nums text-slate-800 dark:text-slate-100">{{
                stat.value
              }}</span>
            </RouterLink>
          </li>
        </ul>

        <div class="grid gap-6 lg:grid-cols-5">
          <div class="lg:col-span-3 space-y-6">
            <section :class="cardClass" aria-labelledby="home-follow-up">
              <div class="flex items-center justify-between px-4 pt-4 pb-2">
                <h2 id="home-follow-up" class="font-semibold text-slate-800 dark:text-slate-100">
                  À relancer aujourd'hui
                </h2>
                <RouterLink :to="{ name: 'follow-up' }" :class="linkClass">Tout voir</RouterLink>
              </div>
              <p v-if="!followUp.length" class="px-4 pb-5 text-sm text-slate-400">
                Rien à relancer aujourd'hui.
              </p>
              <ul v-else class="px-1 pb-2">
                <HomeTaskRow
                  v-for="task in followUp.slice(0, LIMIT)"
                  :key="task.id"
                  :task="task"
                  :note="FOLLOW_UP_REASONS[task.follow_up_reason].label"
                  :note-class="FOLLOW_UP_REASONS[task.follow_up_reason].color"
                  @open="selectedId = task.id"
                />
              </ul>
            </section>

            <section :class="cardClass" aria-labelledby="home-next">
              <div class="flex items-center justify-between px-4 pt-4 pb-2">
                <h2 id="home-next" class="font-semibold text-slate-800 dark:text-slate-100">
                  Prochaines tâches
                </h2>
                <RouterLink :to="{ name: 'tasks' }" :class="linkClass">Toutes les tâches</RouterLink>
              </div>
              <p v-if="!nextTasks.length" class="px-4 pb-5 text-sm text-slate-400">Aucune tâche ouverte.</p>
              <ul v-else class="px-1 pb-2">
                <HomeTaskRow
                  v-for="task in nextTasks"
                  :key="task.id"
                  :task="task"
                  @open="selectedId = task.id"
                />
              </ul>
            </section>
          </div>

          <div class="lg:col-span-2 space-y-6">
            <section :class="cardClass" aria-labelledby="home-projects">
              <div class="flex items-center justify-between px-4 pt-4 pb-2">
                <h2 id="home-projects" class="font-semibold text-slate-800 dark:text-slate-100">
                  Projets actifs
                </h2>
                <RouterLink :to="{ name: 'projects' }" :class="linkClass">Tous les projets</RouterLink>
              </div>
              <p v-if="!activeProjects.length" class="px-4 pb-5 text-sm text-slate-400">
                Aucun projet en cours.
              </p>
              <ul v-else class="px-1 pb-2">
                <li v-for="project in activeProjects" :key="project.id">
                  <RouterLink
                    :to="{ name: 'project', params: { id: project.id } }"
                    class="block rounded-lg px-3 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-700/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
                  >
                    <span class="flex items-center justify-between gap-2">
                      <span class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">{{
                        project.name
                      }}</span>
                      <Globe
                        v-if="project.is_public"
                        class="w-3.5 h-3.5 text-slate-400 shrink-0"
                        aria-label="Public"
                      />
                    </span>
                    <ProjectProgress
                      class="mt-1.5"
                      :progress="project.progress"
                      :done="project.tasks_done"
                      :total="project.tasks_total"
                    />
                  </RouterLink>
                </li>
              </ul>
            </section>

            <section :class="cardClass" aria-labelledby="home-bugs">
              <div class="flex items-center justify-between px-4 pt-4 pb-2">
                <h2 id="home-bugs" class="font-semibold text-slate-800 dark:text-slate-100">Bugs ouverts</h2>
                <span v-if="bugs.length" class="text-xs text-slate-400">{{ bugs.length }}</span>
              </div>
              <p v-if="!bugs.length" class="px-4 pb-5 text-sm text-slate-400">Aucun bug ouvert.</p>
              <ul v-else class="px-1 pb-2">
                <li v-for="bug in bugs.slice(0, LIMIT)" :key="bug.id">
                  <RouterLink
                    :to="{ name: 'project', params: { id: bug.project_id } }"
                    class="flex items-center gap-3 rounded-lg px-3 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-700/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 transition-colors"
                  >
                    <Bug class="w-4 h-4 text-red-500 shrink-0" aria-hidden="true" />
                    <span class="flex-1 min-w-0">
                      <span class="block text-sm text-slate-800 dark:text-slate-100 truncate">{{
                        bug.title
                      }}</span>
                      <span class="block text-xs text-slate-400 truncate">{{
                        projectName(bug.project_id)
                      }}</span>
                    </span>
                    <PriorityFlag :priority="bug.priority" />
                  </RouterLink>
                </li>
              </ul>
            </section>
          </div>
        </div>
      </template>
    </div>

    <TaskSlideOver v-if="selectedId" :task-id="selectedId" @close="selectedId = null" @changed="load" />
  </main>
</template>

<script setup lang="ts">
import { Bug, FolderKanban, Globe, ListTodo, Megaphone } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'
import { errorMessage, projectTasksApi, tasksApi } from '../api/index'
import HomeTaskRow from '../components/HomeTaskRow.vue'
import PriorityFlag from '../components/PriorityFlag.vue'
import ProjectProgress from '../components/ProjectProgress.vue'
import TaskSlideOver from '../components/task/TaskSlideOver.vue'
import { useAuthStore } from '../stores/auth'
import { useProjectStore } from '../stores/projectStore'
import { FOLLOW_UP_REASONS } from '../utils/labels'
import type { FollowUpItem, ProjectTask, TaskSummary } from '../types/api'

// Nombre de lignes montrées par bloc : l'accueil reste un coup d'œil, le reste est à un clic.
const LIMIT = 5

const auth = useAuthStore()
const projectStore = useProjectStore()

const followUp = ref<FollowUpItem[]>([])
const nextTasks = ref<TaskSummary[]>([])
const openTasksTotal = ref(0)
const bugs = ref<ProjectTask[]>([])
const loading = ref(true)
const error = ref('')
const selectedId = ref<string | null>(null)

const cardClass =
  'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-xs'
const linkClass = 'text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline'

// « jeudi 29 octobre » → « Jeudi 29 octobre » (la majuscule seulement au premier mot).
const today = new Date()
  .toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
  .replace(/^./, (c) => c.toUpperCase())
// « Pierre-Yves Durand » → « Pierre-Yves » ; sans nom, le pseudo.
const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || auth.user?.username || '')

const activeProjects = computed(() => projectStore.projects.filter((p) => p.status === 'ACTIVE'))
const projectName = (id: string) => projectStore.projects.find((p) => p.id === id)?.name ?? ''

const stats = computed(() => [
  {
    label: 'À relancer',
    value: followUp.value.length,
    to: { name: 'follow-up' },
    icon: Megaphone,
    tone: 'text-amber-500',
  },
  {
    label: 'Tâches ouvertes',
    value: openTasksTotal.value,
    to: { name: 'tasks' },
    icon: ListTodo,
    tone: 'text-indigo-500',
  },
  {
    label: 'Bugs ouverts',
    value: bugs.value.length,
    to: { name: 'projects' },
    icon: Bug,
    tone: 'text-red-500',
  },
  {
    label: 'Projets actifs',
    value: activeProjects.value.length,
    to: { name: 'projects' },
    icon: FolderKanban,
    tone: 'text-violet-500',
  },
])

async function load() {
  try {
    const [follow, tasks, openBugs] = await Promise.all([
      tasksApi.followUp(),
      // Plus que LIMIT : on retire celles déjà montrées dans « À relancer ».
      tasksApi.list({ limit: LIMIT * 2 }),
      projectTasksApi.list({ kind: 'BUG' }),
      projectStore.fetchProjects(),
    ])
    followUp.value = follow.data
    const alreadyShown = new Set(follow.data.slice(0, LIMIT).map((task) => task.id))
    nextTasks.value = tasks.data.items.filter((task) => !alreadyShown.has(task.id)).slice(0, LIMIT)
    openTasksTotal.value = tasks.data.total
    bugs.value = openBugs.data
    error.value = ''
  } catch (e) {
    error.value = errorMessage(e, "Impossible de charger l'accueil.")
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
