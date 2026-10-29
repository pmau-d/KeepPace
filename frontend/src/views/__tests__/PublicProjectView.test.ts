import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('../../api/index', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../../api/index')>()),
  publicApi: { list: vi.fn(), get: vi.fn() },
}))

import { publicApi } from '../../api/index'
import PublicProjectView from '../PublicProjectView.vue'
import PublicProjectsView from '../PublicProjectsView.vue'
import { response } from '../../test/factories'
import type { PublicProject } from '../../types/api'

const project: PublicProject = {
  name: 'Site vitrine',
  slug: 'site-vitrine',
  description: 'Refonte du site',
  status: 'ACTIVE',
  progress: 40,
  completed_tasks: [{ title: 'Page accueil', completed_at: '2026-10-01T09:00:00Z' }],
}

function mountView(component: typeof PublicProjectView | typeof PublicProjectsView, props = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'tasks', component: { template: '<div />' } },
      { path: '/login', name: 'login', component: { template: '<div />' } },
      { path: '/projets', name: 'public-projects', component: { template: '<div />' } },
      { path: '/projets/:slug', name: 'public-project', component: { template: '<div />' } },
    ],
  })
  return mount(component, { props, global: { plugins: [router] } })
}

describe('vitrine publique', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('affiche un projet public : avancement en pourcentage et tâches terminées', async () => {
    vi.mocked(publicApi.get).mockResolvedValueOnce(response(project) as never)
    const wrapper = mountView(PublicProjectView, { slug: 'site-vitrine' })
    await flushPromises()
    expect(publicApi.get).toHaveBeenCalledWith('site-vitrine')
    expect(wrapper.find('h1').text()).toBe('Site vitrine')
    expect(wrapper.text()).toContain('Refonte du site')
    expect(wrapper.text()).toContain('40 %')
    expect(wrapper.text()).toContain('Page accueil')
    // Pas de nombre de tâches, qui révélerait ce qui n'est pas montré
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('40')
    // (une date « 01/10/2026 » n'est pas un compteur « 4/10 »)
    expect(wrapper.text()).not.toMatch(/(?<![\d/])\d+\/\d+(?![\d/])/)
  })

  it("dit que le projet n'existe pas ou n'est pas public sur un 404", async () => {
    vi.mocked(publicApi.get).mockRejectedValueOnce({ isAxiosError: true, response: { status: 404 } })
    const wrapper = mountView(PublicProjectView, { slug: 'prive' })
    await flushPromises()
    expect(wrapper.find('[role="alert"]').text()).toContain("n'existe pas ou n'est pas public")
  })

  it('liste les projets publics avec un lien vers chacun', async () => {
    vi.mocked(publicApi.list).mockResolvedValueOnce(response([project]) as never)
    const wrapper = mountView(PublicProjectsView)
    await flushPromises()
    const link = wrapper.find('a[href="/projets/site-vitrine"]')
    expect(link.exists()).toBe(true)
    expect(link.text()).toContain('Site vitrine')
  })

  it("annonce l'absence de projet public", async () => {
    vi.mocked(publicApi.list).mockResolvedValueOnce(response([]) as never)
    const wrapper = mountView(PublicProjectsView)
    await flushPromises()
    expect(wrapper.text()).toContain('Aucun projet public')
  })
})
