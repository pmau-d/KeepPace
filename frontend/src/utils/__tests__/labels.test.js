import { describe, expect, it } from 'vitest'
import { formatDate, formatLogValue, fullName, presenceLabel } from '../labels.js'

describe('labels', () => {
  it('formate une date sans décalage de fuseau', () => {
    expect(formatDate('2026-10-01')).toBe('01/10/2026')
  })

  it('compose le nom complet', () => {
    expect(fullName({ first_name: 'Alice', last_name: null })).toBe('Alice')
    expect(fullName({ first_name: 'Alice', last_name: 'Martin' })).toBe('Alice Martin')
  })

  it("rend lisibles les valeurs de l'historique", () => {
    expect(formatLogValue({ field_changed: 'status', new_value: 'BLOCKED' }, 'new')).toBe('En attente client')
    expect(
      formatLogValue({ field_changed: 'client_id', old_value: 'uuid', old_label: 'Bob · Globex' }, 'old'),
    ).toBe('Bob · Globex')
    expect(formatLogValue({ field_changed: 'archived', new_value: 'true' }, 'new')).toBe('Archivée')
    expect(formatLogValue({ field_changed: 'archived', old_value: null }, 'old')).toBeNull()
  })

  it('connaît tous les statuts de présence', () => {
    expect(presenceLabel('LEAVING_SOON')).toBe('Bientôt absent')
    expect(presenceLabel('???')).toBe('Inconnu')
  })
})
