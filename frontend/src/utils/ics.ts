// Lecture minimale d'un calendrier iCalendar (RFC 5545) : les événements
// (VEVENT) avec leurs dates, leur titre et les adresses des participants.
import type { IsoDate } from '../types/api'
import { addDays, parseIsoDate, toIsoDate } from './dates'

export interface CalendarEvent {
  summary: string
  /** Premier jour (inclus). */
  start: IsoDate
  /** Dernier jour (inclus). */
  end: IsoDate
  emails: string[]
}

/** Les lignes longues sont repliées : une ligne qui commence par une espace prolonge la précédente. */
function unfold(text: string): string[] {
  return text
    .replace(/\r\n/g, '\n')
    .replace(/\n[ \t]/g, '')
    .split('\n')
}

function unescape(value: string): string {
  return value
    .replace(/\\n/gi, ' ')
    .replace(/\\([,;\\])/g, '$1')
    .trim()
}

/** « 20261003 » ou « 20261003T090000Z » → date calendaire (heure ignorée). */
function parseIcsDate(value: string): Date | null {
  const match = /^(\d{4})(\d{2})(\d{2})/.exec(value.trim())
  return match ? parseIsoDate(`${match[1]}-${match[2]}-${match[3]}`) : null
}

export function parseIcs(text: string): CalendarEvent[] {
  const events: CalendarEvent[] = []
  let current: { summary: string; start?: Date; end?: Date; allDay: boolean; emails: string[] } | null = null
  for (const line of unfold(text)) {
    const colon = line.indexOf(':')
    if (colon < 0) continue
    const [name = '', ...params] = line.slice(0, colon).split(';')
    const value = line.slice(colon + 1)
    const key = name.toUpperCase()
    if (key === 'BEGIN' && value.trim().toUpperCase() === 'VEVENT') {
      current = { summary: '', allDay: false, emails: [] }
    } else if (key === 'END' && value.trim().toUpperCase() === 'VEVENT' && current) {
      if (current.start) {
        // DTEND d'un événement « journée entière » est exclusif (lendemain du dernier jour).
        let end = current.end ?? current.start
        if (current.allDay && current.end && end > current.start) end = addDays(end, -1)
        events.push({
          summary: current.summary,
          start: toIsoDate(current.start),
          end: toIsoDate(end),
          emails: current.emails,
        })
      }
      current = null
    } else if (current) {
      if (key === 'SUMMARY') current.summary = unescape(value)
      else if (key === 'DTSTART') {
        current.start = parseIcsDate(value) ?? undefined
        current.allDay = params.some((p) => p.toUpperCase() === 'VALUE=DATE') || /^\d{8}$/.test(value.trim())
      } else if (key === 'DTEND') current.end = parseIcsDate(value) ?? undefined
      else if (key === 'ATTENDEE' || key === 'ORGANIZER') {
        const email = /mailto:([^;\s]+)/i.exec(value)?.[1]
        if (email) current.emails.push(email.toLowerCase())
      }
    }
  }
  return events
}
