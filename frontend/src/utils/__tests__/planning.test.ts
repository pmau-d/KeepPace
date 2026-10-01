import { describe, expect, it } from 'vitest'
import { absenceBar, planningDays } from '../planning'
import { parseIsoDate } from '../dates'

const from = parseIsoDate('2026-10-05')! // lundi
const bar = (start: string | null, end: string | null) =>
  absenceBar({ absence_start_date: start, absence_end_date: end }, from, 14)

describe('planning', () => {
  it('place une absence entièrement visible', () => {
    expect(bar('2026-10-07', '2026-10-09')).toEqual({
      start: 2,
      span: 3,
      continuesBefore: false,
      continuesAfter: false,
      openEnded: false,
    })
  })

  it('tronque une absence qui déborde de la période', () => {
    expect(bar('2026-09-20', '2026-10-06')).toMatchObject({ start: 0, span: 2, continuesBefore: true })
    expect(bar('2026-10-15', '2026-11-30')).toMatchObject({ start: 10, span: 4, continuesAfter: true })
  })

  it('gère les absences sans début ou sans fin', () => {
    expect(bar(null, '2026-10-06')).toMatchObject({ start: 0, span: 2, continuesBefore: true })
    expect(bar('2026-10-12', null)).toMatchObject({
      start: 7,
      span: 7,
      openEnded: true,
      continuesAfter: true,
    })
  })

  it('ignore ce qui ne touche pas la période', () => {
    expect(bar(null, null)).toBeNull()
    expect(bar('2026-09-01', '2026-10-04')).toBeNull()
    expect(bar('2026-10-19', '2026-10-25')).toBeNull()
  })

  it('repère les week-ends et aujourd’hui', () => {
    const days = planningDays(from, 7, parseIsoDate('2026-10-07')!)
    expect(days.filter((d) => d.isWeekend).map((d) => d.index)).toEqual([5, 6])
    expect(days.find((d) => d.isToday)?.index).toBe(2)
    expect(days[0]?.isMonday).toBe(true)
  })
})
