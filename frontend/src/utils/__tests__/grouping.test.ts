import { describe, expect, it } from 'vitest'
import { dayLabel, groupTasksByDay } from '../grouping'
import { makeTask } from '../../test/factories'

const today = new Date('2026-09-30T10:00:00')

describe('dayLabel', () => {
  it('nomme les jours proches', () => {
    expect(dayLabel('2026-09-30', today)).toBe("Aujourd'hui")
    expect(dayLabel('2026-10-01', today)).toBe('Demain')
    expect(dayLabel(null, today)).toBe('Sans échéance')
    expect(dayLabel('2026-10-03', today)).toBe('Samedi 3 octobre')
    expect(dayLabel('2026-12-24', today)).toBe('Jeudi 24 décembre')
    expect(dayLabel('2027-01-04', today)).toBe('Lundi 4 janvier 2027')
  })
})

describe('groupTasksByDay', () => {
  it("regroupe les retards en tête et garde l'ordre de l'API", () => {
    const tasks = [
      makeTask({ id: 'a', due_date: '2026-09-20' }),
      makeTask({ id: 'b', due_date: '2026-09-28' }),
      makeTask({ id: 'c', due_date: '2026-09-30' }),
      makeTask({ id: 'd', due_date: '2026-09-30' }),
      makeTask({ id: 'e', due_date: null }),
    ]
    const groups = groupTasksByDay(tasks, today)
    expect(groups.map((g) => [g.label, g.tasks.map((t) => t.id)])).toEqual([
      ['En retard', ['a', 'b']],
      ["Aujourd'hui", ['c', 'd']],
      ['Sans échéance', ['e']],
    ])
    expect(groups[0]?.overdue).toBe(true)
  })
})
