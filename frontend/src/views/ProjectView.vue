<template>
  <main class="flex-1 overflow-y-auto">
    <div class="max-w-4xl mx-auto px-5 py-6">
      <RouterLink
        :to="{ name: 'projects' }"
        class="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 mb-4"
      >
        <ArrowLeft class="w-4 h-4" aria-hidden="true" />
        Tous les projets
      </RouterLink>

      <p v-if="notFound" class="text-slate-500" role="alert">Ce projet n'existe pas ou a été archivé.</p>
      <p v-else-if="loadError" class="text-sm text-red-500" role="alert">{{ loadError }}</p>
      <p v-else-if="!project" class="text-sm text-slate-400">Chargement…</p>

      <template v-else>
        <!-- En-tête -->
        <header
          class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-xs"
        >
          <div class="flex items-start justify-between gap-3 flex-wrap">
            <div class="min-w-0">
              <h1 class="text-xl font-bold text-slate-800 dark:text-slate-100 wrap-break-word">
                {{ project.name }}
              </h1>
              <p v-if="project.description" class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                {{ project.description }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <label for="project-status" class="sr-only">État du projet</label>
              <BaseSelect
                id="project-status"
                :model-value="project.status"
                :options="STATUS_OPTIONS"
                @update:model-value="changeStatus"
              />
              <button
                type="button"
                class="p-2 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                aria-label="Archiver le projet"
                title="Archiver le projet"
                @click="archiveProject"
              >
                <Archive class="w-4 h-4" aria-hidden="true" />
              </button>
            </div>
          </div>
          <div class="mt-4 flex items-center gap-3 flex-wrap text-sm text-slate-600 dark:text-slate-300">
            <button
              id="project-public"
              type="button"
              role="switch"
              :aria-checked="project.is_public"
              :disabled="publishing"
              :class="[
                'relative w-10 h-5 rounded-full transition-colors shrink-0 disabled:opacity-50',
                project.is_public ? 'bg-indigo-500' : 'bg-slate-300 dark:bg-slate-600',
              ]"
              @click="togglePublic"
            >
              <span
                :class="[
                  'absolute left-0 top-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform duration-200',
                  project.is_public ? 'translate-x-5' : 'translate-x-0.5',
                ]"
              ></span>
            </button>
            <label for="project-public" class="cursor-pointer">Visible publiquement</label>
            <RouterLink
              v-if="project.is_public"
              :to="{ name: 'public-project', params: { slug: project.slug } }"
              class="inline-flex items-center gap-1 text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              <ExternalLink class="w-3.5 h-3.5" aria-hidden="true" />
              Voir la vitrine
            </RouterLink>
            <span v-else class="text-xs text-slate-400">
              Privé : seuls vous le voyez. Public : nom, description, état, avancement et tâches terminées.
            </span>
          </div>
          <ProjectProgress
            class="mt-4"
            :progress="project.progress"
            :done="project.tasks_done"
            :total="project.tasks_total"
          />
        </header>

        <!-- Onglets par type -->
        <div class="mt-6 flex gap-1 border-b border-slate-200 dark:border-slate-700" role="tablist">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            type="button"
            role="tab"
            :aria-selected="activeTab === tab.value"
            :class="[
              'px-3 py-2 text-sm font-medium -mb-px border-b-2 transition-colors flex items-center gap-1.5',
              activeTab === tab.value
                ? 'border-indigo-500 text-indigo-700 dark:text-indigo-300'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200',
            ]"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
            <span
              v-if="tab.count"
              class="text-xs rounded-full px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-300"
              >{{ tab.count }}</span
            >
          </button>
        </div>

        <!-- Ajout rapide -->
        <form class="mt-4 space-y-3" @submit.prevent="addTask">
          <div class="flex gap-2 flex-wrap">
            <label for="new-ptask-title" class="sr-only">Titre</label>
            <input
              id="new-ptask-title"
              v-model="draft.title"
              type="text"
              maxlength="200"
              :placeholder="placeholder"
              class="flex-1 min-w-48 text-sm bg-white dark:bg-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 placeholder-slate-400"
            />
            <label for="new-ptask-kind" class="sr-only">Type</label>
            <BaseSelect id="new-ptask-kind" v-model="draft.kind" :options="KIND_OPTIONS" />
            <button
              type="button"
              class="px-3 py-2 text-sm rounded-lg text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600"
              :aria-expanded="showOptions"
              @click="showOptions = !showOptions"
            >
              Options
            </button>
            <button
              type="submit"
              :disabled="adding || !draft.title.trim()"
              class="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white transition-colors"
            >
              Ajouter
            </button>
          </div>

          <div
            v-if="showOptions"
            class="grid gap-3 sm:grid-cols-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4"
          >
            <div>
              <label
                for="new-ptask-due"
                class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
                >Échéance</label
              >
              <DatePicker id="new-ptask-due" v-model="draft.due_date" placeholder="Sans échéance" />
            </div>
            <div>
              <label
                for="new-ptask-priority"
                class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1"
                >Priorité</label
              >
              <BaseSelect
                id="new-ptask-priority"
                v-model="draft.priority"
                :options="PRIORITY_OPTIONS"
                block
              />
            </div>
            <RecurrenceFields
              v-model:recurrence="draft.recurrence"
              v-model:interval="draft.recurrence_interval"
              id-prefix="new-ptask"
            />
          </div>
        </form>

        <!-- Liste -->
        <p v-if="tasksError" class="mt-4 text-sm text-red-500" role="alert">{{ tasksError }}</p>
        <div
          v-else-if="!visibleOpen.length && !visibleDone.length"
          class="mt-6 text-center py-12 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 text-sm text-slate-400"
        >
          Rien ici pour l'instant.
        </div>

        <ul v-if="visibleOpen.length" class="mt-4 space-y-2">
          <ProjectTaskRow
            v-for="task in visibleOpen"
            :key="task.id"
            :task="task"
            @toggle="toggleTask"
            @archive="archiveTask"
          />
        </ul>

        <section v-if="visibleDone.length" class="mt-6">
          <button
            type="button"
            class="flex items-center gap-1.5 text-sm font-medium text-slate-500 dark:text-slate-400 mb-2"
            :aria-expanded="showDone"
            @click="showDone = !showDone"
          >
            <ChevronRight
              :class="['w-4 h-4 transition-transform', showDone && 'rotate-90']"
              aria-hidden="true"
            />
            Terminées ({{ visibleDone.length }})
          </button>
          <ul v-if="showDone" class="space-y-2">
            <ProjectTaskRow
              v-for="task in visibleDone"
              :key="task.id"
              :task="task"
              @toggle="toggleTask"
              @archive="archiveTask"
            />
          </ul>
        </section>
      </template>
    </div>
  </main>
</template>

<script setup lang="ts">
import { Archive, ArrowLeft, ChevronRight, ExternalLink } from '@lucide/vue'
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { errorMessage, httpStatus, projectTasksApi, projectsApi } from '../api/index'
import ProjectProgress from '../components/ProjectProgress.vue'
import ProjectTaskRow from '../components/ProjectTaskRow.vue'
import RecurrenceFields from '../components/task/RecurrenceFields.vue'
import BaseSelect from '../components/ui/BaseSelect.vue'
import DatePicker from '../components/ui/DatePicker.vue'
import { confirm } from '../composables/useConfirm'
import { useProjectStore } from '../stores/projectStore'
import { useToastStore } from '../stores/toast'
import { KIND_LABELS, PROJECT_STATUS_LABELS } from '../utils/labels'
import { PRIORITY_OPTIONS } from '../utils/options'
import type {
  Project,
  ProjectStatus,
  ProjectTask,
  ProjectTaskCreatePayload,
  Recurrence,
  TaskKind,
  TaskPriority,
} from '../types/api'

const props = defineProps<{ id: string }>()

const router = useRouter()
const projectStore = useProjectStore()
const toast = useToastStore()

type Tab = TaskKind | 'ALL'

const project = ref<Project | null>(null)
const tasks = ref<ProjectTask[]>([])
const notFound = ref(false)
const loadError = ref('')
const tasksError = ref('')
const activeTab = ref<Tab>('ALL')
const showDone = ref(false)
const showOptions = ref(false)
const adding = ref(false)
const publishing = ref(false)

const STATUS_OPTIONS = (Object.keys(PROJECT_STATUS_LABELS) as ProjectStatus[]).map((value) => ({
  value,
  label: PROJECT_STATUS_LABELS[value],
}))
const KIND_OPTIONS = (Object.keys(KIND_LABELS) as TaskKind[]).map((value) => ({
  value,
  label: KIND_LABELS[value],
}))

const draft = reactive<{
  title: string
  kind: TaskKind
  due_date: string
  priority: TaskPriority
  recurrence: Recurrence | ''
  recurrence_interval: number
}>({ title: '', kind: 'TASK', due_date: '', priority: 'MEDIUM', recurrence: '', recurrence_interval: 1 })

const open = computed(() => tasks.value.filter((t) => t.status !== 'DONE'))
const tabs = computed(() => [
  { value: 'ALL' as Tab, label: 'Tout', count: open.value.length },
  ...KIND_OPTIONS.map(({ value, label }) => ({
    value: value as Tab,
    label: value === 'TASK' ? 'Tâches' : `${label}s`,
    count: open.value.filter((t) => t.kind === value).length,
  })),
])
const inTab = (task: ProjectTask) => activeTab.value === 'ALL' || task.kind === activeTab.value
const visibleOpen = computed(() => open.value.filter(inTab))
const visibleDone = computed(() => tasks.value.filter((t) => t.status === 'DONE').filter(inTab))

const placeholder = computed(
  () =>
    ({
      ALL: 'Ajouter une tâche, un bug ou un retour…',
      TASK: 'Ajouter une tâche…',
      BUG: 'Décrire un bug à corriger…',
      IMPROVEMENT: 'Noter une amélioration…',
    })[activeTab.value],
)

// Le type du formulaire suit l'onglet : un bug saisi dans « Bugs » est un bug.
watch(activeTab, (tab) => {
  if (tab !== 'ALL') draft.kind = tab
})

async function load() {
  notFound.value = false
  loadError.value = ''
  tasksError.value = ''
  project.value = null
  try {
    project.value = (await projectsApi.get(props.id)).data
  } catch (e) {
    if (httpStatus(e) === 404) notFound.value = true
    else loadError.value = errorMessage(e, 'Impossible de charger le projet.')
    return
  }
  await loadTasks()
}

async function loadTasks() {
  try {
    tasks.value = (await projectTasksApi.list({ project_id: props.id, show_done: true })).data
  } catch (e) {
    tasksError.value = errorMessage(e, 'Impossible de charger les tâches.')
  }
}

/** Les tâches ont changé : recharge la liste (une récurrence en crée une) et l'avancement. */
async function refresh() {
  await Promise.all([loadTasks(), projectStore.refreshProject(props.id)])
  project.value = projectStore.projects.find((p) => p.id === props.id) ?? project.value
}

watch(() => props.id, load, { immediate: true })

async function addTask() {
  const title = draft.title.trim()
  if (!title) return
  const payload: ProjectTaskCreatePayload = {
    project_id: props.id,
    title,
    kind: draft.kind,
    priority: draft.priority,
    ...(draft.due_date ? { due_date: draft.due_date } : {}),
    ...(draft.recurrence
      ? { recurrence: draft.recurrence, recurrence_interval: draft.recurrence_interval }
      : {}),
  }
  adding.value = true
  try {
    await projectTasksApi.create(payload)
    Object.assign(draft, { title: '', due_date: '', recurrence: '', recurrence_interval: 1 })
    await refresh()
  } catch (e) {
    toast.error(e, "Impossible d'ajouter la tâche.")
  } finally {
    adding.value = false
  }
}

async function toggleTask(task: ProjectTask) {
  try {
    await (task.status === 'DONE' ? projectTasksApi.reopen(task.id) : projectTasksApi.close(task.id))
    await refresh()
  } catch (e) {
    toast.error(e, 'Impossible de modifier la tâche.')
  }
}

async function archiveTask(task: ProjectTask) {
  const ok = await confirm({
    title: `Archiver « ${task.title} » ?`,
    message: 'Elle disparaît de la liste et de l’avancement du projet.',
    confirmLabel: 'Archiver',
    danger: true,
  })
  if (!ok) return
  try {
    await projectTasksApi.archive(task.id)
    await refresh()
  } catch (e) {
    toast.error(e, "Impossible d'archiver la tâche.")
  }
}

async function changeStatus(status: ProjectStatus) {
  try {
    project.value = await projectStore.updateProject(props.id, { status })
  } catch (e) {
    toast.error(e, 'Impossible de modifier le projet.')
  }
}

async function togglePublic() {
  if (!project.value) return
  publishing.value = true
  try {
    project.value = await projectStore.updateProject(props.id, { is_public: !project.value.is_public })
  } catch (e) {
    toast.error(e, 'Impossible de modifier la visibilité du projet.')
  } finally {
    publishing.value = false
  }
}

async function archiveProject() {
  if (!project.value) return
  const { id, name } = project.value
  const ok = await confirm({
    title: `Archiver le projet « ${name} » ?`,
    message: 'Le projet et ses tâches sont archivés. Vous pourrez le restaurer juste après.',
    confirmLabel: 'Archiver',
    danger: true,
  })
  if (!ok) return
  try {
    await projectStore.archiveProject(id)
  } catch (e) {
    toast.error(e, "Impossible d'archiver le projet.")
    return
  }
  void router.push({ name: 'projects' })
  toast.success(`${name} archivé.`, {
    action: { label: 'Annuler', run: () => projectStore.restoreProject(id) },
  })
}
</script>
