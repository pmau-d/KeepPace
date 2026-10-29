import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('../../api/index', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../../api/index')>()),
  tasksApi: { followUp: vi.fn(), list: vi.fn() },
  projectTasksApi: { list: vi.fn() },
  projectsApi: { getAll: vi.fn() },
}))
// Le panneau de détail a ses propres tests : ici on vérifie seulement qu'il s'ouvre.
vi.mock('../../components/task/TaskSlideOver.vue', () => ({
  default: { props: ['taskId'], template: '<aside data-testid="slide-over">{{ taskId }}</aside>' },
}))

import { projectTasksApi, projectsApi, tasksApi } from '../../api/index'
import HomeView from '../HomeView.vue'
import { useAuthStore } from '../../stores/auth'
import { makeProject, makeProjectTask, makeTask, makeUser, response } from '../../test/factories'
import type { FollowUpItem, Project, ProjectTask, TaskSummary } from '../../types/api'

const stub = { template: '<div />' }

async function mountHome() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: ['home', 'tasks', 'follow-up', 'projects', 'project'].map((name) => ({
      path: name === 'home' ? '/' : `/${name}${name === 'project' ? '/:id' : ''}`,
      name,
      component: stub,
    })),
  })
  const wrapper = mount(HomeView, { global: { plugins: [router] } })
  await flushPromises()
  return wrapper
}

interface Mocked {
  follow: FollowUpItem[]
  tasks: TaskSummary[]
  total: number
  bugs: ProjectTask[]
  projects: Project[]
}

function mockApis(overrides: Partial<Mocked> = {}) {
  const tasks = overrides.tasks ?? [makeTask({ id: 'next' })]
  const { follow = [], total = tasks.length, bugs = [], projects = [] } = overrides
  vi.mocked(tasksApi.followUp).mockResolvedValue(response(follow) as never)
  vi.mocked(tasksApi.list).mockResolvedValue(response({ items: tasks, total, limit: 5, offset: 0 }) as never)
  vi.mocked(projectTasksApi.list).mockResolvedValue(response(bugs) as never)
  vi.mocked(projectsApi.getAll).mockResolvedValue(response(projects) as never)
}

describe('HomeView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    useAuthStore().user = makeUser({ username: 'pierre-yves', full_name: 'Pierre-Yves Durand' })
  })

  it('salue par le prénom, ou à défaut par le pseudo', async () => {
    mockApis()
    expect((await mountHome()).find('h1').text()).toBe('Bonjour Pierre-Yves')
    useAuthStore().user = makeUser({ username: 'pierre-yves', full_name: null })
    expect((await mountHome()).find('h1').text()).toBe('Bonjour pierre-yves')
  })

  it('résume la journée en quatre chiffres', async () => {
    mockApis({
      follow: [{ ...makeTask({ id: 'f1' }), follow_up_reason: 'OVERDUE' }],
      tasks: [makeTask({ id: 'a' }), makeTask({ id: 'b' })],
      total: 12,
      bugs: [makeProjectTask({ id: 'b1', kind: 'BUG' }), makeProjectTask({ id: 'b2', kind: 'BUG' })],
      projects: [makeProject({ id: 'p1', status: 'ACTIVE' }), makeProject({ id: 'p2', status: 'PAUSED' })],
    })
    const wrapper = await mountHome()
    const tiles = Object.fromEntries(
      wrapper.findAll('ul.grid > li').map((li) => [li.find('span').text(), li.findAll('span')[1]!.text()]),
    )
    expect(tiles).toEqual({
      'À relancer': '1',
      'Tâches ouvertes': '12',
      'Bugs ouverts': '2',
      'Projets actifs': '1',
    })
  })

  it('ne montre que les projets en cours, avec leur avancement', async () => {
    mockApis({
      projects: [
        makeProject({
          id: 'p1',
          name: 'Actif',
          status: 'ACTIVE',
          progress: 50,
          tasks_done: 1,
          tasks_total: 2,
        }),
        makeProject({ id: 'p2', name: 'Livré', status: 'DELIVERED' }),
      ],
    })
    const section = (await mountHome()).find('[aria-labelledby="home-projects"]')
    expect(section.text()).toContain('Actif')
    expect(section.text()).not.toContain('Livré')
    expect(section.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('50')
  })

  it("indique le motif d'une relance", async () => {
    mockApis({ follow: [{ ...makeTask({ id: 'f1', title: 'Relancer Acme' }), follow_up_reason: 'OVERDUE' }] })
    const section = (await mountHome()).find('[aria-labelledby="home-follow-up"]')
    expect(section.text()).toContain('Relancer Acme')
    expect(section.text()).toContain('Échéance dépassée')
  })

  it('nomme le projet de chaque bug ouvert', async () => {
    mockApis({
      bugs: [makeProjectTask({ id: 'b1', kind: 'BUG', title: 'Crash iPhone', project_id: 'p1' })],
      projects: [makeProject({ id: 'p1', name: 'Application mobile' })],
    })
    const section = (await mountHome()).find('[aria-labelledby="home-bugs"]')
    expect(section.text()).toContain('Crash iPhone')
    expect(section.text()).toContain('Application mobile')
  })

  it('limite chaque bloc à cinq lignes, le reste est à un clic', async () => {
    const follow = Array.from({ length: 8 }, (_, i) => ({
      ...makeTask({ id: `f${i}`, title: `Relance ${i}` }),
      follow_up_reason: 'OVERDUE' as const,
    }))
    mockApis({ follow })
    const wrapper = await mountHome()
    expect(wrapper.find('[aria-labelledby="home-follow-up"]').findAll('li')).toHaveLength(5)
    // … mais le chiffre du jour compte tout
    expect(wrapper.find('ul.grid > li span:nth-of-type(2)').text()).toBe('8')
  })

  it('ne répète pas dans « Prochaines tâches » ce qui est déjà dans « À relancer »', async () => {
    const late = makeTask({ id: 'late', title: 'Compte rendu' })
    mockApis({
      follow: [{ ...late, follow_up_reason: 'OVERDUE' }],
      tasks: [late, makeTask({ id: 'other', title: 'Valider le devis' })],
    })
    const next = (await mountHome()).find('[aria-labelledby="home-next"]')
    expect(next.text()).toContain('Valider le devis')
    expect(next.text()).not.toContain('Compte rendu')
  })

  it('affiche un message dans chaque bloc vide', async () => {
    mockApis({ tasks: [] })
    const text = (await mountHome()).text()
    for (const message of [
      "Rien à relancer aujourd'hui.",
      'Aucune tâche ouverte.',
      'Aucun projet en cours.',
      'Aucun bug ouvert.',
    ])
      expect(text).toContain(message)
  })

  it('ouvre le détail de la tâche sans quitter la page', async () => {
    mockApis({ tasks: [makeTask({ id: 'next', title: 'Préparer la démo' })] })
    const wrapper = await mountHome()
    expect(wrapper.find('[data-testid="slide-over"]').exists()).toBe(false)
    await wrapper.find('[aria-labelledby="home-next"] button').trigger('click')
    expect(wrapper.find('[data-testid="slide-over"]').text()).toBe('next')
  })

  it("signale l'échec du chargement", async () => {
    mockApis()
    vi.mocked(tasksApi.followUp).mockRejectedValue(new Error('réseau'))
    expect((await mountHome()).find('[role="alert"]').text()).toContain("Impossible de charger l'accueil")
  })
})
