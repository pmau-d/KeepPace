import axios, { isAxiosError } from 'axios'
import type {
  Client,
  ClientPayload,
  Company,
  Digest,
  FollowUpItem,
  Project,
  ProjectPayload,
  ProjectTask,
  ProjectTaskCreatePayload,
  ProjectTaskUpdatePayload,
  PublicProject,
  PublicProjectCard,
  ChecklistItem,
  TaskKind,
  RegisterPayload,
  Task,
  TaskComment,
  TaskCreatePayload,
  TaskLog,
  TaskPage,
  TaskQuery,
  TaskUpdatePayload,
  User,
} from '../types/api'

export const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  withCredentials: true,
})

// Appelé quand la session expire (branché par le store d'authentification).
let onUnauthorized: () => void = () => {}
export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (isAxiosError(error)) {
      const url = error.config?.url ?? ''
      if (error.response?.status === 401 && !url.startsWith('/auth/')) onUnauthorized()
    }
    return Promise.reject(error)
  },
)

interface ValidationDetail {
  msg?: string
}

/** Statut HTTP d'une erreur axios, ou undefined pour toute autre erreur. */
export function httpStatus(error: unknown): number | undefined {
  return isAxiosError(error) ? error.response?.status : undefined
}

/** Message lisible à partir d'une erreur axios. */
export function errorMessage(
  error: unknown,
  fallback = 'Une erreur est survenue. Veuillez réessayer.',
): string {
  if (!isAxiosError(error)) return fallback
  if (!error.response) return 'Serveur injoignable. Vérifiez votre connexion.'
  const detail: unknown = (error.response.data as { detail?: unknown } | undefined)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const first = detail[0] as ValidationDetail | undefined
    if (first?.msg) return first.msg.replace(/^Value error, /, '')
  }
  if (error.response.status === 429) return 'Trop de tentatives. Réessayez dans quelques minutes.'
  return fallback
}

/** Paramètres de requête sérialisables (les valeurs absentes sont ignorées). */
function toSearchParams(params: TaskQuery): URLSearchParams {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
  }
  return search
}

// ─── Auth ───────────────────────────────────────────────────────────────────
export const authApi = {
  me: () => api.get<User>('/auth/me'),
  login: (data: { username: string; password: string }) => api.post<User>('/auth/login', data),
  register: (data: RegisterPayload) => api.post<User>('/auth/register', data),
  logout: () => api.post<void>('/auth/logout'),
  update: (data: { full_name?: string | null; digest_opt_in?: boolean }) => api.put<User>('/auth/me', data),
}

// ─── Récap quotidien ───────────────────────────────────────────────────────
export const digestApi = {
  get: () => api.get<Digest>('/digest/'),
  sendNow: () => api.post<{ sent_to: string }>('/digest/send'),
}

// ─── Companies ──────────────────────────────────────────────────────────────
export const companiesApi = {
  getAll: (params?: { archived?: boolean }) => api.get<Company[]>('/companies/', { params }),
  create: (data: { name: string }) => api.post<Company>('/companies/', data),
  update: (id: string, data: { name: string }) => api.put<Company>(`/companies/${id}`, data),
  archive: (id: string) => api.delete<void>(`/companies/${id}`),
  restore: (id: string) => api.post<Company>(`/companies/${id}/restore`),
}

// ─── Clients ────────────────────────────────────────────────────────────────
export const clientsApi = {
  getAll: (params?: { archived?: boolean }) => api.get<Client[]>('/clients/', { params }),
  create: (data: ClientPayload) => api.post<Client>('/clients/', data),
  update: (id: string, data: ClientPayload) => api.put<Client>(`/clients/${id}`, data),
  archive: (id: string) => api.delete<void>(`/clients/${id}`),
  restore: (id: string) => api.post<Client>(`/clients/${id}/restore`),
}

// ─── Projets ────────────────────────────────────────────────────────────────
export const projectsApi = {
  getAll: (params?: { archived?: boolean }) => api.get<Project[]>('/projects/', { params }),
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: ProjectPayload & { name: string }) => api.post<Project>('/projects/', data),
  update: (id: string, data: ProjectPayload) => api.put<Project>(`/projects/${id}`, data),
  archive: (id: string) => api.delete<void>(`/projects/${id}`),
  restore: (id: string) => api.post<Project>(`/projects/${id}/restore`),
}

/** Vitrine : appelée sans connexion. */
export const publicApi = {
  list: () => api.get<PublicProjectCard[]>('/public/projects/'),
  get: (slug: string) => api.get<PublicProject>(`/public/projects/${encodeURIComponent(slug)}`),
}

export const projectTasksApi = {
  list: (params: { project_id?: string; kind?: TaskKind; show_done?: boolean }) =>
    api.get<ProjectTask[]>('/project-tasks/', { params }),
  create: (data: ProjectTaskCreatePayload) => api.post<ProjectTask>('/project-tasks/', data),
  update: (id: string, data: ProjectTaskUpdatePayload) => api.put<ProjectTask>(`/project-tasks/${id}`, data),
  close: (id: string) => api.post<ProjectTask>(`/project-tasks/${id}/close`),
  reopen: (id: string) => api.post<ProjectTask>(`/project-tasks/${id}/reopen`),
  archive: (id: string) => api.delete<void>(`/project-tasks/${id}`),
  addChecklistItem: (id: string, label: string) =>
    api.post<ChecklistItem>(`/project-tasks/${id}/checklist`, { label }),
  updateChecklistItem: (id: string, itemId: string, data: { label?: string; done?: boolean }) =>
    api.put<ChecklistItem>(`/project-tasks/${id}/checklist/${itemId}`, data),
  deleteChecklistItem: (id: string, itemId: string) =>
    api.delete<void>(`/project-tasks/${id}/checklist/${itemId}`),
}

// ─── Tasks ──────────────────────────────────────────────────────────────────
export const tasksApi = {
  list: (params: TaskQuery) => api.get<TaskPage>('/tasks/', { params }),
  get: (id: string) => api.get<Task>(`/tasks/${id}`),
  followUp: () => api.get<FollowUpItem[]>('/tasks/follow-up'),
  exportUrl: (params: TaskQuery) => `/api/tasks/export.csv?${toSearchParams(params)}`,
  create: (data: TaskCreatePayload) => api.post<Task>('/tasks/', data),
  update: (id: string, data: TaskUpdatePayload) => api.put<Task>(`/tasks/${id}`, data),
  close: (id: string) => api.post<Task>(`/tasks/${id}/close`),
  reopen: (id: string) => api.post<Task>(`/tasks/${id}/reopen`),
  snooze: (id: string, days: number, comment?: string) =>
    api.post<Task>(`/tasks/${id}/snooze`, { days, comment }),
  archive: (id: string) => api.delete<void>(`/tasks/${id}`),
  restore: (id: string) => api.post<Task>(`/tasks/${id}/restore`),
  getLogs: (id: string) => api.get<TaskLog[]>(`/tasks/${id}/logs`),
  addComment: (id: string, content: string) => api.post<TaskComment>(`/tasks/${id}/comments`, { content }),
  deleteComment: (taskId: string, commentId: string) =>
    api.delete<void>(`/tasks/${taskId}/comments/${commentId}`),
  addChecklistItem: (id: string, label: string) =>
    api.post<ChecklistItem>(`/tasks/${id}/checklist`, { label }),
  updateChecklistItem: (id: string, itemId: string, data: { label?: string; done?: boolean }) =>
    api.put<ChecklistItem>(`/tasks/${id}/checklist/${itemId}`, data),
  deleteChecklistItem: (id: string, itemId: string) => api.delete<void>(`/tasks/${id}/checklist/${itemId}`),
}
