// Dates calendaires (sans heure) manipulées en heure locale.
// Une date « AAAA-MM-JJ » lue avec `new Date(...)` serait interprétée en UTC
// et pourrait reculer d'un jour : on passe toujours par ces fonctions.

import type { IsoDate } from '../types/api'

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/

export function parseIsoDate(value: IsoDate | null | undefined): Date | null {
  const match = value ? ISO_DATE.exec(value) : null
  if (!match) return null
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
}

export function toIsoDate(date: Date): IsoDate {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

export function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

export function addDays(date: Date, days: number): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days)
}

/** Même jour du mois suivant/précédent, borné au dernier jour (31 janv. + 1 mois = 28/29 févr.). */
export function addMonths(date: Date, months: number): Date {
  const target = new Date(date.getFullYear(), date.getMonth() + months, 1)
  const lastDay = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate()
  return new Date(target.getFullYear(), target.getMonth(), Math.min(date.getDate(), lastDay))
}

/** Lundi de la semaine de `date` (semaine à la française). */
export function startOfWeek(date: Date): Date {
  const day = (date.getDay() + 6) % 7
  return addDays(startOfDay(date), -day)
}

export function isSameDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

/** Nombre de jours entre deux dates calendaires (b - a). */
export function daysBetween(a: Date, b: Date): number {
  return Math.round((startOfDay(b).getTime() - startOfDay(a).getTime()) / 86_400_000)
}

/** Les 42 jours (6 semaines) affichés par un calendrier mensuel commençant le lundi. */
export function monthGrid(month: Date): Date[] {
  const first = startOfWeek(new Date(month.getFullYear(), month.getMonth(), 1))
  return Array.from({ length: 42 }, (_, index) => addDays(first, index))
}

function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

/** « Mercredi 7 octobre », avec l'année seulement si elle diffère de l'année en cours. */
export function formatDayHeading(date: Date, today: Date = new Date()): string {
  return capitalize(
    date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      ...(date.getFullYear() !== today.getFullYear() && { year: 'numeric' }),
    }),
  )
}

/** « mer. 7 oct. 2026 », pour les champs de date. */
export function formatShortDate(date: Date): string {
  return date.toLocaleDateString('fr-FR', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function formatMonth(date: Date): string {
  return capitalize(date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }))
}
