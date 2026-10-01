import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import Sidebar from '../Sidebar.vue'
import { useClientStore } from '../../stores/clientStore'
import { makeClient, makeCompany } from '../../test/factories'

vi.mock('../../api/index', () => ({ tasksApi: { list: vi.fn() } }))

function mountSidebar(props: Record<string, unknown> = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: ['tasks', 'task', 'follow-up', 'archives'].map((name) => ({
      path: `/${name}`,
      name,
      component: { template: '<div />' },
    })),
  })
  return mount(Sidebar, { props, global: { plugins: [router] }, attachTo: document.body })
}

describe('Sidebar', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const clients = useClientStore()
    clients.clients = [
      makeClient({ id: 'a', first_name: 'Camille', open_tasks_count: 3 }),
      makeClient({
        id: 'b',
        first_name: 'Hugo',
        open_tasks_count: 0,
        company: makeCompany({ id: 'c2', name: 'Globex' }),
        company_id: 'c2',
      }),
    ]
  })

  it('affiche le nombre de tâches ouvertes, seulement quand il y en a', () => {
    const wrapper = mountSidebar()
    expect(wrapper.find('[aria-label="3 tâche(s) ouverte(s)"]').exists()).toBe(true)
    expect(wrapper.findAll('[aria-label$="ouverte(s)"]')).toHaveLength(1)
  })

  it("met la légende des présences dans une info-bulle plutôt qu'en permanence", () => {
    const wrapper = mountSidebar()
    expect(wrapper.text()).not.toContain('Rentré récemment')
    expect(wrapper.find('button[aria-label="Légende des pastilles de présence"]').exists()).toBe(true)
  })

  it('en tiroir, propose un bouton de fermeture qui prévient le parent', async () => {
    const wrapper = mountSidebar({ drawer: true })
    await wrapper.find('button[aria-label="Fermer le menu"]').trigger('click')
    expect(wrapper.emitted('navigate')).toHaveLength(1)
  })
})
