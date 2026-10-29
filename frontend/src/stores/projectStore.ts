import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectsApi } from '../api/index'
import type { Project, ProjectPayload } from '../types/api'

const byName = (a: Project, b: Project) => a.name.localeCompare(b.name)

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const loading = ref(false)

  async function fetchProjects() {
    loading.value = true
    try {
      projects.value = (await projectsApi.getAll()).data
    } finally {
      loading.value = false
    }
  }

  async function createProject(data: ProjectPayload & { name: string }) {
    const project = (await projectsApi.create(data)).data
    projects.value = [...projects.value, project].sort(byName)
    return project
  }

  async function updateProject(id: string, data: ProjectPayload) {
    const project = (await projectsApi.update(id, data)).data
    replace(project)
    return project
  }

  /** Recharge un projet : son avancement change quand ses tâches évoluent. */
  async function refreshProject(id: string) {
    replace((await projectsApi.get(id)).data)
  }

  async function archiveProject(id: string) {
    await projectsApi.archive(id)
    projects.value = projects.value.filter((p) => p.id !== id)
  }

  async function restoreProject(id: string) {
    const project = (await projectsApi.restore(id)).data
    projects.value = [...projects.value.filter((p) => p.id !== id), project].sort(byName)
  }

  function replace(project: Project) {
    const idx = projects.value.findIndex((p) => p.id === project.id)
    if (idx === -1) projects.value = [...projects.value, project].sort(byName)
    else projects.value[idx] = project
  }

  return {
    projects,
    loading,
    fetchProjects,
    createProject,
    updateProject,
    refreshProject,
    archiveProject,
    restoreProject,
  }
})
