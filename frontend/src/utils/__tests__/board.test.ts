import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../../api/index', () => ({
  tasksApi: { close: vi.fn(), reopen: vi.fn(), update: vi.fn() },
}))

import { tasksApi } from '../../api/index'
import { boardColumns, moveTask } from '../board'
import { makeTask, response } from '../../test/factories'

describe('tableau', () => {
  beforeEach(() => vi.clearAllMocks())

  it('répartit les tâches par statut et ne garde que les terminées récentes', () => {
    const today = new Date('2026-10-01T10:00:00')
    const columns = boardColumns(
      [
        makeTask({ id: 'a', status: 'TODO' }),
        makeTask({ id: 'b', status: 'BLOCKED' }),
        makeTask({ id: 'old', status: 'DONE', updated_at: '2026-08-01T09:00:00Z' }),
        makeTask({ id: 'd1', status: 'DONE', updated_at: '2026-09-28T09:00:00Z' }),
        makeTask({ id: 'd2', status: 'DONE', updated_at: '2026-09-30T09:00:00Z' }),
      ],
      today,
    )
    expect(columns.map((c) => [c.status, c.tasks.map((t) => t.id)])).toEqual([
      ['TODO', ['a']],
      ['IN_PROGRESS', []],
      ['BLOCKED', ['b']],
      ['DONE', ['d2', 'd1']],
    ])
  })

  it('termine via /close et sort de « Terminé » via /reopen', async () => {
    vi.mocked(tasksApi.close).mockResolvedValue(response({}) as never)
    vi.mocked(tasksApi.reopen).mockResolvedValue(response({}) as never)
    vi.mocked(tasksApi.update).mockResolvedValue(response({}) as never)

    await moveTask('t', 'TODO', 'DONE')
    expect(tasksApi.close).toHaveBeenCalledWith('t')

    await moveTask('t', 'DONE', 'TODO')
    expect(tasksApi.reopen).toHaveBeenCalledTimes(1)
    expect(tasksApi.update).not.toHaveBeenCalled()

    await moveTask('t', 'DONE', 'BLOCKED')
    expect(tasksApi.reopen).toHaveBeenCalledTimes(2)
    expect(tasksApi.update).toHaveBeenCalledWith('t', { status: 'BLOCKED' })

    await moveTask('t', 'TODO', 'IN_PROGRESS')
    expect(tasksApi.update).toHaveBeenLastCalledWith('t', { status: 'IN_PROGRESS' })
  })
})
