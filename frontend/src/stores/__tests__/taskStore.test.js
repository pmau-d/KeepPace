import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../api/index.js', () => ({
  tasksApi: {
    list: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
  },
}))

import { tasksApi } from '../../api/index.js'
import { useTaskStore } from '../taskStore.js'

const task = (id, extra = {}) => ({ id, title: id, status: 'TODO', ...extra })

describe('taskStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('envoie les filtres et pagine', async () => {
    const store = useTaskStore()
    tasksApi.list.mockResolvedValueOnce({ data: { items: [task('a'), task('b')], total: 3 } })
    store.filters.search = '  contrat '
    store.filters.showDone = true
    await store.fetchTasks()
    expect(tasksApi.list).toHaveBeenCalledWith({ search: 'contrat', show_done: true, limit: 50, offset: 0 })
    expect(store.hasMore).toBe(true)

    tasksApi.list.mockResolvedValueOnce({ data: { items: [task('b'), task('c')], total: 3 } })
    await store.loadMore()
    expect(tasksApi.list).toHaveBeenLastCalledWith(expect.objectContaining({ offset: 2 }))
    expect(store.tasks.map((t) => t.id)).toEqual(['a', 'b', 'c'])
    expect(store.hasMore).toBe(false)
  })

  it('ignore une réponse arrivée après une recherche plus récente', async () => {
    const store = useTaskStore()
    let resolveSlow
    tasksApi.list
      .mockReturnValueOnce(new Promise((resolve) => (resolveSlow = resolve)))
      .mockResolvedValueOnce({ data: { items: [task('fresh')], total: 1 } })
    const slow = store.fetchTasks()
    await store.fetchTasks()
    resolveSlow({ data: { items: [task('stale')], total: 1 } })
    await slow
    expect(store.tasks.map((t) => t.id)).toEqual(['fresh'])
  })

  it('retire une tâche terminée ou archivée de la liste', async () => {
    const store = useTaskStore()
    store.tasks = [task('a'), task('b')]
    store.total = 2
    tasksApi.update.mockResolvedValueOnce({ data: task('a', { status: 'DONE' }) })
    await store.updateTask('a', { status: 'DONE' })
    expect(store.tasks.map((t) => t.id)).toEqual(['b'])

    tasksApi.archive.mockResolvedValueOnce({})
    await store.archiveTask('b')
    expect(store.tasks).toEqual([])
    expect(store.total).toBe(0)
  })
})
