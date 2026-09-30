import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../api/index', () => ({
  tasksApi: {
    list: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
  },
}))

import { tasksApi } from '../../api/index'
import { useTaskStore } from '../taskStore'
import { makeTask, response } from '../../test/factories'
import type { TaskPage, TaskSummary } from '../../types/api'

const task = (id: string, extra: Partial<TaskSummary> = {}) => makeTask({ id, ...extra })
const page = (items: TaskSummary[], total: number) =>
  response<TaskPage>({ items, total, limit: 50, offset: 0 }) as never

describe('taskStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('envoie les filtres et pagine', async () => {
    const store = useTaskStore()
    vi.mocked(tasksApi.list).mockResolvedValueOnce(page([task('a'), task('b')], 3))
    store.filters.search = '  contrat '
    store.filters.showDone = true
    await store.fetchTasks()
    expect(tasksApi.list).toHaveBeenCalledWith({ search: 'contrat', show_done: true, limit: 50, offset: 0 })
    expect(store.hasMore).toBe(true)

    vi.mocked(tasksApi.list).mockResolvedValueOnce(page([task('b'), task('c')], 3))
    await store.loadMore()
    expect(tasksApi.list).toHaveBeenLastCalledWith(expect.objectContaining({ offset: 2 }))
    expect(store.tasks.map((t) => t.id)).toEqual(['a', 'b', 'c'])
    expect(store.hasMore).toBe(false)
  })

  it('ignore une réponse arrivée après une recherche plus récente', async () => {
    const store = useTaskStore()
    let resolveSlow: (value: unknown) => void = () => {}
    vi.mocked(tasksApi.list)
      .mockReturnValueOnce(new Promise((resolve) => (resolveSlow = resolve)) as never)
      .mockResolvedValueOnce(page([task('fresh')], 1))
    const slow = store.fetchTasks()
    await store.fetchTasks()
    resolveSlow(page([task('stale')], 1))
    await slow
    expect(store.tasks.map((t) => t.id)).toEqual(['fresh'])
  })

  it('retire une tâche terminée ou archivée de la liste', async () => {
    const store = useTaskStore()
    store.tasks = [task('a'), task('b')]
    store.total = 2
    vi.mocked(tasksApi.update).mockResolvedValueOnce(
      response({ ...task('a', { status: 'DONE' }), comments: [] }) as never,
    )
    await store.updateTask('a', { status: 'DONE' })
    expect(store.tasks.map((t) => t.id)).toEqual(['b'])

    vi.mocked(tasksApi.archive).mockResolvedValueOnce({} as never)
    await store.archiveTask('b')
    expect(store.tasks).toEqual([])
    expect(store.total).toBe(0)
  })
})
