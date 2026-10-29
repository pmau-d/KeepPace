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
  { path: '/mes-projets', name: 'projects', component: () => import('../views/ProjectsView.vue') },
  {
    path: '/mes-projets/:id',
    name: 'project',
    component: () => import('../views/ProjectView.vue'),
    props: true,
  },
  // Vitrine : seules pages accessibles sans connexion.
  {
    path: '/projets',
    name: 'public-projects',
    component: () => import('../views/PublicProjectsView.vue'),
    meta: { public: true },
  },
  {
    path: '/projets/:slug',
    name: 'public-project',
    component: () => import('../views/PublicProjectView.vue'),
    meta: { public: true },
    props: true,
  },
  { path: '/archives', name: 'archives', component: () => import('../views/ArchivesView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export function createAppRouter(history = createWebHistory()) {
  const router = createRouter({ history, routes })

  router.beforeEach(async (to) => {
    const auth = useAuthStore()
    if (!auth.checked) await auth.fetchMe()
    if (to.meta.public) return true
    if (to.meta.guest) return auth.isAuthenticated ? { name: 'tasks' } : true
    if (!auth.isAuthenticated)
      return { name: 'login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : {} }
    return true
  })

  return router
}
