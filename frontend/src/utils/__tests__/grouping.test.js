import { describe, expect, it } from 'vitest'
import { dayLabel, groupTasksByDay } from '../grouping.js'

const today = new Date('2026-09-30T10:00:00')

describe('dayLabel', () => {
  it('nomme les jours proches', () => {
    expect(dayLabel('2026-09-30', today)).toBe("Aujourd'hui")
    expect(dayLabel('2026-10-01', today)).toBe('Demain')
    expect(dayLabel(null, today)).toBe('Sans échéance')
    expect(dayLabel('2026-10-03', today)).toMatch(/^Samedi 03 octobre$/)
  })
})

describe('groupTasksByDay', () => {
  it("regroupe les retards en tête et garde l'ordre de l'API", () => {
    const tasks = [
      { id: 'a', due_date: '2026-09-20' },
      { id: 'b', due_date: '2026-09-28' },
      { id: 'c', due_date: '2026-09-30' },
      { id: 'd', due_date: '2026-09-30' },
      { id: 'e', due_date: null },
    ]
    const groups = groupTasksByDay(tasks, today)
    expect(groups.map((g) => [g.label, g.tasks.map((t) => t.id)])).toEqual([
      ['En retard', ['a', 'b']],
      ["Aujourd'hui", ['c', 'd']],
      ['Sans échéance', ['e']],
    ])
    expect(groups[0].overdue).toBe(true)
  })
})
