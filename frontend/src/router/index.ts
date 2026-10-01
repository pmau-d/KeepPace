import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/AuthView.vue'), meta: { guest: true } },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/AuthView.vue'),
    meta: { guest: true },
    props: { mode: 'register' },
  },
  { path: '/', name: 'tasks', component: () => import('../views/TasksView.vue') },
  { path: '/tasks/:id', name: 'task', component: () => import('../views/TasksView.vue'), props: true },
  { path: '/relances', name: 'follow-up', component: () => import('../views/FollowUpView.vue') },
  { path: '/planning', name: 'planning', component: () => import('../views/PlanningView.vue') },
  { path: '/tableau', name: 'board', component: () => import('../views/BoardView.vue') },
  { path: '/archives', name: 'archives', component: () => import('../views/ArchivesView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export function createAppRouter(history = createWebHistory()) {
  const router = createRouter({ history, routes })

  router.beforeEach(async (to) => {
    const auth = useAuthStore()
    if (!auth.checked) await auth.fetchMe()
    if (to.meta.guest) return auth.isAuthenticated ? { name: 'tasks' } : true
    if (!auth.isAuthenticated)
      return { name: 'login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : {} }
    return true
  })

  return router
}
