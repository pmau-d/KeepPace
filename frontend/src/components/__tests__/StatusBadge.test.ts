import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '../StatusBadge.vue'

describe('StatusBadge', () => {
  it('affiche le libellé français du statut', () => {
    expect(mount(StatusBadge, { props: { status: 'IN_PROGRESS' } }).text()).toBe('En cours')
  })

  it('retombe sur la valeur brute pour un statut inconnu', () => {
    expect(mount(StatusBadge, { props: { status: 'ARCHIVED' } }).text()).toBe('ARCHIVED')
  })
})
