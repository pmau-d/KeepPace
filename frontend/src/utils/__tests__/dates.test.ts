import { describe, expect, it } from 'vitest'
import {
  addMonths,
  daysBetween,
  formatDayHeading,
  monthGrid,
  parseIsoDate,
  startOfWeek,
  toIsoDate,
} from '../dates'

describe('dates', () => {
  it('lit et écrit une date sans décalage de fuseau', () => {
    expect(toIsoDate(parseIsoDate('2026-03-29')!)).toBe('2026-03-29')
    expect(parseIsoDate('pas une date')).toBeNull()
  })

  it('borne le changement de mois au dernier jour', () => {
    expect(toIsoDate(addMonths(parseIsoDate('2026-01-31')!, 1))).toBe('2026-02-28')
  })

  it('fait commencer la semaine le lundi', () => {
    expect(toIsoDate(startOfWeek(parseIsoDate('2026-10-04')!))).toBe('2026-09-28')
    const grid = monthGrid(parseIsoDate('2026-10-15')!)
    expect(grid).toHaveLength(42)
    expect(toIsoDate(grid[0]!)).toBe('2026-09-28')
  })

  it('compte les jours calendaires, changement d’heure compris', () => {
    expect(daysBetween(parseIsoDate('2026-10-24')!, parseIsoDate('2026-10-26')!)).toBe(2)
  })

  it("n'affiche l'année que si elle n'est pas l'année en cours", () => {
    const today = parseIsoDate('2026-10-01')!
    expect(formatDayHeading(parseIsoDate('2026-10-07')!, today)).toBe('Mercredi 7 octobre')
    expect(formatDayHeading(parseIsoDate('2027-01-04')!, today)).toBe('Lundi 4 janvier 2027')
  })
})
