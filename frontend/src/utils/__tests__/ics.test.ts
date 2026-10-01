import { describe, expect, it } from 'vitest'
import { parseIcs } from '../ics'

const ICS = [
  'BEGIN:VCALENDAR',
  'VERSION:2.0',
  'BEGIN:VEVENT',
  'SUMMARY:Congés Inès Moreau',
  'DTSTART;VALUE=DATE:20261003',
  'DTEND;VALUE=DATE:20261018',
  'ATTENDEE;CN=Inès Moreau:mailto:Ines@Example.com',
  'END:VEVENT',
  'BEGIN:VEVENT',
  'SUMMARY:Formation\\, puis télé',
  ' travail',
  'DTSTART:20261020T090000Z',
  'DTEND:20261021T170000Z',
  'ORGANIZER:mailto:hugo@example.com',
  'END:VEVENT',
  'BEGIN:VEVENT',
  'SUMMARY:Sans date',
  'END:VEVENT',
  'END:VCALENDAR',
].join('\r\n')

describe('calendrier ICS', () => {
  it('lit les événements, journée entière comprise (fin exclusive)', () => {
    expect(parseIcs(ICS)).toEqual([
      { summary: 'Congés Inès Moreau', start: '2026-10-03', end: '2026-10-17', emails: ['ines@example.com'] },
      {
        summary: 'Formation, puis télétravail',
        start: '2026-10-20',
        end: '2026-10-21',
        emails: ['hugo@example.com'],
      },
    ])
  })

  it('ignore un fichier qui n’est pas un calendrier', () => {
    expect(parseIcs('bonjour')).toEqual([])
  })
})
