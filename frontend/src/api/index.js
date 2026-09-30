import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// ─── Companies ──────────────────────────────────────────────────────────────
export const companiesApi = {
  getAll: () => api.get('/companies/'),
  create: (data) => api.post('/companies/', data),
  update: (id, data) => api.put(`/companies/${id}`, data),
  delete: (id) => api.delete(`/companies/${id}`),
}

// ─── Clients ────────────────────────────────────────────────────────────────
export const clientsApi = {
  getAll: () => api.get('/clients/'),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
}

// ─── Tasks ──────────────────────────────────────────────────────────────────
export const tasksApi = {
  getAll: (params) => api.get('/tasks/', { params }),
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  close: (id) => api.post(`/tasks/${id}/close`),
  reopen: (id) => api.post(`/tasks/${id}/reopen`),
  delete: (id) => api.delete(`/tasks/${id}`),
  getLogs: (id) => api.get(`/tasks/${id}/logs`),
  getComments: (id) => api.get(`/tasks/${id}/comments`),
  addComment: (id, content) => api.post(`/tasks/${id}/comments`, { content }),
  deleteComment: (taskId, commentId) => api.delete(`/tasks/${taskId}/comments/${commentId}`),
}
