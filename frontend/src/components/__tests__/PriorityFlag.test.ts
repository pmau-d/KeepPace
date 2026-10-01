import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import PriorityFlag from '../PriorityFlag.vue'

describe('PriorityFlag', () => {
  it('annonce la priorité aux lecteurs d’écran', () => {
    const wrapper = mount(PriorityFlag, { props: { priority: 'HIGH' } })
    expect(wrapper.attributes('aria-label')).toBe('Priorité haute')
    expect(wrapper.attributes('role')).toBe('img')
  })

  it('ne remplit le drapeau que pour la priorité haute', () => {
    expect(
      mount(PriorityFlag, { props: { priority: 'HIGH' } })
        .find('svg')
        .attributes('fill'),
    ).toBe('currentColor')
    expect(
      mount(PriorityFlag, { props: { priority: 'LOW' } })
        .find('svg')
        .attributes('fill'),
    ).toBe('none')
  })
})
