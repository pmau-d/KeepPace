<template>
  <main class="flex-1 overflow-y-auto">
    <div class="max-w-5xl mx-auto px-5 py-6">
      <header class="flex items-center justify-between gap-3 mb-6">
        <div>
          <h1 class="text-xl font-bold text-slate-800 dark:text-slate-100">Projets</h1>
          <p class="text-sm text-slate-500 dark:text-slate-400">
            Vos projets de développement : tâches, bugs et retours au même endroit.
          </p>
        </div>
        <button
          type="button"
          class="inline-flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
          @click="creating = true"
        >
          <Plus class="w-4 h-4" aria-hidden="true" />
          Nouveau projet
        </button>
      </header>

      <p v-if="loadError" class="text-sm text-red-500" role="alert">{{ loadError }}</p>
      <p v-else-if="projectStore.loading && !projects.length" class="text-sm text-slate-400">Chargement…</p>

      <div
        v-else-if="!projects.length"
        class="text-center py-16 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700"
      >
        <FolderKanban class="w-10 h-10 mx-auto text-slate-300 dark:text-slate-600" aria-hidden="true" />
        <p class="mt-3 font-medium text-slate-700 dark:text-slate-200">Aucun projet pour l'instant</p>
        <p class="text-sm text-slate-400 mt-1">Créez-en un pour suivre ses tâches et ses bugs.</p>
      </div>

      <ul v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <li v-for="project in projects" :key="project.id">
          <RouterLink
            :to="{ name: 'project', params: { id: project.id } }"
            class="block h-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-indigo-300 dark:hover:border-indigo-500/50 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
          >
            <div class="flex items-start justify-between gap-2">
              <h2 class="font-semibold text-slate-800 dark:text-slate-100 leading-snug">
                {{ project.name }}
              </h2>
              <ProjectStatusBadge :status="project.status" />
            </div>
            <p
              :class="[
                'mt-2 text-sm line-clamp-2 min-h-10',
                project.description
                  ? 'text-slate-500 dark:text-slate-400'
                  : 'text-slate-300 dark:text-slate-600',
              ]"
            >
              {{ project.description || 'Pas de description' }}
            </p>
            <ProjectProgress
              class="mt-4"
              :progress="project.progress"
              :done="project.tasks_done"
              :total="project.tasks_total"
            />
          </RouterLink>
        </li>
      </ul>
    </div>

    <CreateProjectModal v-if="creating" @close="creating = false" @created="onCreated" />
  </main>
</template>

<script setup lang="ts">
import { FolderKanban, Plus } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { errorMessage } from '../api/index'
import CreateProjectModal from '../components/CreateProjectModal.vue'
import ProjectProgress from '../components/ProjectProgress.vue'
import ProjectStatusBadge from '../components/ProjectStatusBadge.vue'
import { useProjectStore } from '../stores/projectStore'
import type { Project } from '../types/api'

const router = useRouter()
const projectStore = useProjectStore()
const creating = ref(false)
const loadError = ref('')

const projects = computed(() => projectStore.projects)

onMounted(async () => {
  try {
    await projectStore.fetchProjects()
  } catch (e) {
    loadError.value = errorMessage(e, 'Impossible de charger les projets.')
  }
})

function onCreated(project: Project) {
  creating.value = false
  void router.push({ name: 'project', params: { id: project.id } })
}
</script>
