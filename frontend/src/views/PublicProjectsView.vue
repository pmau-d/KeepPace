<template>
  <div class="min-h-screen bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-100">
    <PublicHeader />
    <main class="max-w-5xl mx-auto px-5 py-10">
      <h1 class="text-3xl font-bold tracking-tight">Projets</h1>
      <p class="mt-2 text-slate-500 dark:text-slate-400">Les projets de développement en cours et livrés.</p>

      <p v-if="error" class="mt-8 text-sm text-red-500" role="alert">{{ error }}</p>
      <p v-else-if="loading" class="mt-8 text-sm text-slate-400">Chargement…</p>
      <p v-else-if="!projects.length" class="mt-8 text-slate-400">Aucun projet public pour l'instant.</p>

      <ul v-else class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <li v-for="project in projects" :key="project.slug">
          <RouterLink
            :to="{ name: 'public-project', params: { slug: project.slug } }"
            class="block h-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-indigo-300 dark:hover:border-indigo-500/50 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
          >
            <div class="flex items-start justify-between gap-2">
              <h2 class="font-semibold leading-snug">{{ project.name }}</h2>
              <ProjectStatusBadge :status="project.status" />
            </div>
            <p
              v-if="project.description"
              class="mt-2 text-sm text-slate-500 dark:text-slate-400 line-clamp-3"
            >
              {{ project.description }}
            </p>
            <PublicProgress class="mt-4" :progress="project.progress" />
          </RouterLink>
        </li>
      </ul>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { errorMessage, publicApi } from '../api/index'
import ProjectStatusBadge from '../components/ProjectStatusBadge.vue'
import PublicHeader from '../components/PublicHeader.vue'
import PublicProgress from '../components/PublicProgress.vue'
import type { PublicProjectCard } from '../types/api'

const projects = ref<PublicProjectCard[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    projects.value = (await publicApi.list()).data
  } catch (e) {
    error.value = errorMessage(e, 'Impossible de charger les projets.')
  } finally {
    loading.value = false
  }
})
</script>
