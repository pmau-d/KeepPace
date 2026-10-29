import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../api/index', () => ({
  projectsApi: { getAll: vi.fn(), get: vi.fn(), create: vi.fn(), update: vi.fn(), archive: vi.fn() },
}))

import { projectsApi } from '../../api/index'
import { useProjectStore } from '../projectStore'
import { makeProject, response } from '../../test/factories'

describe('projectStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('charge les projets', async () => {
    const store = useProjectStore()
    vi.mocked(projectsApi.getAll).mockResolvedValue(response([makeProject({ id: 'a' })]) as never)
    await store.fetchProjects()
    expect(store.projects.map((p) => p.id)).toEqual(['a'])
    expect(store.loading).toBe(false)
  })

  it('ajoute un projet créé, trié par nom', async () => {
    const store = useProjectStore()
    store.projects = [makeProject({ id: 'b', name: 'Zèbre' })]
    vi.mocked(projectsApi.create).mockResolvedValue(
      response(makeProject({ id: 'a', name: 'Alpha' })) as never,
    )
    const created = await store.createProject({ name: 'Alpha' })
    expect(created.id).toBe('a')
    expect(store.projects.map((p) => p.name)).toEqual(['Alpha', 'Zèbre'])
  })

  it("rafraîchit l'avancement d'un seul projet", async () => {
    const store = useProjectStore()
    store.projects = [makeProject({ id: 'a' }), makeProject({ id: 'b' })]
    vi.mocked(projectsApi.get).mockResolvedValue(
      response(makeProject({ id: 'a', tasks_total: 2, tasks_done: 1, progress: 50 })) as never,
    )
    await store.refreshProject('a')
    expect(store.projects[0]?.progress).toBe(50)
    expect(store.projects[1]?.progress).toBe(0)
  })

  it('retire un projet archivé de la liste', async () => {
    const store = useProjectStore()
    store.projects = [makeProject({ id: 'a' }), makeProject({ id: 'b' })]
    vi.mocked(projectsApi.archive).mockResolvedValue(response(undefined) as never)
    await store.archiveProject('a')
    expect(store.projects.map((p) => p.id)).toEqual(['b'])
  })
})
