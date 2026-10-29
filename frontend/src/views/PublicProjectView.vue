<template>
  <div class="min-h-screen bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-100">
    <PublicHeader />
    <main class="max-w-3xl mx-auto px-5 py-10">
      <RouterLink
        :to="{ name: 'public-projects' }"
        class="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 mb-6"
      >
        <ArrowLeft class="w-4 h-4" aria-hidden="true" />
        Tous les projets
      </RouterLink>

      <p v-if="notFound" class="text-slate-500" role="alert">Ce projet n'existe pas ou n'est pas public.</p>
      <p v-else-if="error" class="text-sm text-red-500" role="alert">{{ error }}</p>
      <p v-else-if="!project" class="text-sm text-slate-400">Chargement…</p>

      <template v-else>
        <div class="flex items-start justify-between gap-3 flex-wrap">
          <h1 class="text-3xl font-bold tracking-tight wrap-break-word">{{ project.name }}</h1>
          <ProjectStatusBadge :status="project.status" />
        </div>
        <p v-if="project.description" class="mt-3 text-slate-600 dark:text-slate-300 whitespace-pre-line">
          {{ project.description }}
        </p>
        <PublicProgress class="mt-6" :progress="project.progress" />

        <section class="mt-10">
          <h2 class="text-lg font-semibold">Réalisé</h2>
          <p v-if="!project.completed_tasks.length" class="mt-3 text-sm text-slate-400">
            Rien à montrer pour l'instant.
          </p>
          <ul v-else class="mt-3 space-y-2">
            <li
              v-for="(task, index) in project.completed_tasks"
              :key="index"
              class="flex items-center gap-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3"
            >
              <Check class="w-4 h-4 text-green-500 shrink-0" aria-hidden="true" />
              <span class="flex-1 min-w-0 wrap-break-word text-sm">{{ task.title }}</span>
              <time class="text-xs text-slate-400 shrink-0" :datetime="task.completed_at">{{
                formatDate(task.completed_at)
              }}</time>
            </li>
          </ul>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, Check } from '@lucide/vue'
import { ref, watch } from 'vue'
import { errorMessage, httpStatus, publicApi } from '../api/index'
import ProjectStatusBadge from '../components/ProjectStatusBadge.vue'
import PublicHeader from '../components/PublicHeader.vue'
import PublicProgress from '../components/PublicProgress.vue'
import { formatDate } from '../utils/labels'
import type { PublicProject } from '../types/api'

const props = defineProps<{ slug: string }>()

const project = ref<PublicProject | null>(null)
const notFound = ref(false)
const error = ref('')

async function load() {
  project.value = null
  notFound.value = false
  error.value = ''
  try {
    project.value = (await publicApi.get(props.slug)).data
  } catch (e) {
    if (httpStatus(e) === 404) notFound.value = true
    else error.value = errorMessage(e, 'Impossible de charger le projet.')
  }
}

watch(() => props.slug, load, { immediate: true })
</script>
