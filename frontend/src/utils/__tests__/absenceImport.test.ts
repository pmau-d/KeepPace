import { describe, expect, it } from 'vitest'
import { isPast, matchClient, pickPeriod } from '../absenceImport'
import type { CalendarEvent } from '../ics'
import { makeClient } from '../../test/factories'

const event = (summary: string, start: string, end: string, emails: string[] = []): CalendarEvent => ({
  summary,
  start,
  end,
  emails,
})
const ines = makeClient({ id: 'ines', first_name: 'Inès', last_name: 'Moreau', email: 'ines@example.com' })
const hugo = makeClient({ id: 'hugo', first_name: 'Hugo', last_name: 'Lefèvre', email: null })
const nathan = makeClient({ id: 'nathan', first_name: 'Nathan', last_name: null })
const clients = [ines, hugo, nathan]
const today = new Date('2026-10-01T10:00:00')

describe('import des absences', () => {
  it("reconnaît le client par l'email, puis par le nom complet (accents et casse ignorés)", () => {
    expect(matchClient(event('Congés', '2026-10-03', '2026-10-10', ['ines@example.com']), clients)?.id).toBe(
      'ines',
    )
    expect(matchClient(event('Congés HUGO LEFEVRE', '2026-10-03', '2026-10-10'), clients)?.id).toBe('hugo')
  })

  it('ne devine pas sur un prénom seul', () => {
    expect(matchClient(event('Absence Nathan', '2026-10-03', '2026-10-10'), clients)).toBeNull()
  })

  it("garde l'absence en cours, sinon la plus proche, et ignore le passé", () => {
    const past = event('a', '2026-09-01', '2026-09-10')
    const later = event('b', '2026-12-20', '2027-01-03')
    const soon = event('c', '2026-10-12', '2026-10-16')
    expect(isPast(past, today)).toBe(true)
    expect(pickPeriod([past, later, soon], today)).toBe(soon)
    expect(pickPeriod([past], today)).toBeNull()
  })
})
