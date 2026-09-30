import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  withCredentials: true,
})

// Appelé quand la session expire (branché par le store d'authentification).
let onUnauthorized = () => {}
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url ?? ''
    if (error.response?.status === 401 && !url.startsWith('/auth/')) onUnauthorized()
    return Promise.reject(error)
  },
)

/** Message lisible à partir d'une erreur axios. */
export function errorMessage(error, fallback = 'Une erreur est survenue. Veuillez réessayer.') {
  if (!error?.isAxiosError) return fallback
  if (!error.response) return 'Serveur injoignable. Vérifiez votre connexion.'
  const detail = error.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg.replace(/^Value error, /, '')
  if (error.response.status === 429) return 'Trop de tentatives. Réessayez dans quelques minutes.'
  return fallback
}

// ─── Auth ───────────────────────────────────────────────────────────────────
export const authApi = {
  me: () => api.get('/auth/me'),
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
}

// ─── Companies ──────────────────────────────────────────────────────────────
export const companiesApi = {
  getAll: (params) => api.get('/companies/', { params }),
  create: (data) => api.post('/companies/', data),
  update: (id, data) => api.put(`/companies/${id}`, data),
  archive: (id) => api.delete(`/companies/${id}`),
  restore: (id) => api.post(`/companies/${id}/restore`),
}

// ─── Clients ────────────────────────────────────────────────────────────────
export const clientsApi = {
  getAll: (params) => api.get('/clients/', { params }),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  archive: (id) => api.delete(`/clients/${id}`),
  restore: (id) => api.post(`/clients/${id}/restore`),
}

// ─── Tasks ──────────────────────────────────────────────────────────────────
export const tasksApi = {
  list: (params) => api.get('/tasks/', { params }),
  get: (id) => api.get(`/tasks/${id}`),
  followUp: () => api.get('/tasks/follow-up'),
  exportUrl: (params) => `/api/tasks/export.csv?${new URLSearchParams(params)}`,
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  close: (id) => api.post(`/tasks/${id}/close`),
  reopen: (id) => api.post(`/tasks/${id}/reopen`),
  archive: (id) => api.delete(`/tasks/${id}`),
  restore: (id) => api.post(`/tasks/${id}/restore`),
  getLogs: (id) => api.get(`/tasks/${id}/logs`),
  addComment: (id, content) => api.post(`/tasks/${id}/comments`, { content }),
  deleteComment: (taskId, commentId) => api.delete(`/tasks/${taskId}/comments/${commentId}`),
}
