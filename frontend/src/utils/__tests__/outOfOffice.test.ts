import { describe, expect, it } from 'vitest'
import { detectAbsence } from '../outOfOffice'

const today = new Date('2026-10-01T10:00:00')
const detect = (message: string) => detectAbsence(message, today)

describe("message d'absence", () => {
  it.each([
    ['Je suis absente du 3 au 17 octobre.', '2026-10-03', '2026-10-17'],
    ['Absent du lundi 5 octobre au vendredi 9 octobre inclus', '2026-10-05', '2026-10-09'],
    ['En congés du 03/10 au 17/10/2026, réponse à mon retour.', '2026-10-03', '2026-10-17'],
    ['I am out of office from October 3 to October 17, 2026.', '2026-10-03', '2026-10-17'],
    ['Absent du 28 décembre au 4 janvier', '2026-12-28', '2027-01-04'],
    ['Out from 2026-10-03 until 2026-10-17', '2026-10-03', '2026-10-17'],
  ])('lit une période : %s', (message, start, end) => {
    expect(detect(message)).toEqual({ start, end })
  })

  it.each([
    ['Je serai de retour le 20 octobre.', '2026-10-19'],
    ['De retour au bureau le lundi 20/10.', '2026-10-19'],
    ["I'll be back on Monday, October 20th.", '2026-10-19'],
    ["Je suis absent jusqu'au 17 octobre inclus.", '2026-10-17'],
    ['Out of the office until 17.10.2026', '2026-10-17'],
    ['Retour prévu le 1er octobre', '2026-09-30'],
  ])('lit une date de retour ou de fin : %s', (message, end) => {
    expect(detect(message)).toEqual({ start: null, end })
  })

  it('place une date sans année dans le futur proche', () => {
    expect(detect('De retour le 5 janvier')).toEqual({ start: null, end: '2027-01-04' })
  })

  it('ne devine rien sans formulation reconnue', () => {
    expect(detect('Merci pour votre message, je vous réponds rapidement.')).toBeNull()
    expect(detect('Absent du 32 au 40 octobre')).toBeNull()
  })
})
