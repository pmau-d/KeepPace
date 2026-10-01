// Calculs de la vue Planning : une ligne par client, une colonne par jour.
import type { Client } from '../types/api'
import { addDays, daysBetween, parseIsoDate } from './dates'

export interface AbsenceBar {
  /** Index du premier jour couvert dans la période affichée (0 = premier jour). */
  start: number
  /** Nombre de jours couverts dans la période affichée. */
  span: number
  /** L'absence a commencé avant la période (ou sans date de début). */
  continuesBefore: boolean
  /** L'absence se poursuit après la période (ou retour non daté). */
  continuesAfter: boolean
  /** Retour non daté. */
  openEnded: boolean
}

/**
 * Barre d'absence d'un client sur `days` jours à partir de `from`, ou null si
 * l'absence ne touche pas la période. Une absence sans date de début est
 * considérée comme déjà commencée ; sans date de fin, comme non datée.
 */
export function absenceBar(
  client: Pick<Client, 'absence_start_date' | 'absence_end_date'>,
  from: Date,
  days: number,
): AbsenceBar | null {
  const start = parseIsoDate(client.absence_start_date)
  const end = parseIsoDate(client.absence_end_date)
  if (!start && !end) return null
  const last = addDays(from, days - 1)
  if (start && start > last) return null
  if (end && end < from) return null
  const first = start && start > from ? daysBetween(from, start) : 0
  const stop = end && end < last ? daysBetween(from, end) : days - 1
  return {
    start: first,
    span: stop - first + 1,
    continuesBefore: !start || start < from,
    continuesAfter: !end || end > last,
    openEnded: !end,
  }
}

/** Les jours de la période, avec les repères utiles à l'affichage. */
export function planningDays(from: Date, days: number, today: Date) {
  return Array.from({ length: days }, (_, index) => {
    const date = addDays(from, index)
    const weekday = date.getDay()
    return {
      date,
      index,
      isWeekend: weekday === 0 || weekday === 6,
      isToday: daysBetween(today, date) === 0,
      isMonday: weekday === 1,
      isFirstOfMonth: date.getDate() === 1,
    }
  })
}
