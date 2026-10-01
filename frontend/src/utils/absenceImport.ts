// Rapprochement des événements d'un calendrier avec les clients.
import type { Client } from '../types/api'
import type { CalendarEvent } from './ics'
import { parseIsoDate, startOfDay } from './dates'
import { fullName } from './labels'
import { normalize } from './text'

/** Le client concerné : même adresse email, sinon nom complet présent dans le titre. */
export function matchClient(event: CalendarEvent, clients: Client[]): Client | null {
  const byEmail = clients.find((c) => c.email && event.emails.includes(c.email.toLowerCase()))
  if (byEmail) return byEmail
  const title = normalize(event.summary)
  const named = clients.filter((c) => c.last_name && title.includes(normalize(fullName(c))))
  return named.length === 1 ? named[0]! : null
}

/** Événement passé : il ne change plus la présence du client. */
export function isPast(event: CalendarEvent, today: Date = new Date()): boolean {
  return parseIsoDate(event.end)! < startOfDay(today)
}

/**
 * Une seule période d'absence par client : celle en cours, sinon la plus
 * proche à venir.
 */
export function pickPeriod(events: CalendarEvent[], today: Date = new Date()): CalendarEvent | null {
  const upcoming = events.filter((e) => !isPast(e, today)).sort((a, b) => a.start.localeCompare(b.start))
  return upcoming[0] ?? null
}
