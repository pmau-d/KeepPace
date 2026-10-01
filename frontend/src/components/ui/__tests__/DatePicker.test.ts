import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import DatePicker from '../DatePicker.vue'

const dialog = () => document.querySelector<HTMLElement>('[role="dialog"]')
const day = (iso: string) => document.querySelector<HTMLButtonElement>(`[data-date="${iso}"]`)

describe('DatePicker', () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-10-01T10:00:00'))
  })
  afterEach(() => {
    vi.useRealTimers()
    document.body.innerHTML = ''
  })

  it('affiche la date choisie en toutes lettres', () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '2026-10-07' }, attachTo: document.body })
    expect(wrapper.text()).toContain('mer. 7 oct. 2026')
  })

  it('ouvre le mois de la date et renvoie le jour cliqué au format AAAA-MM-JJ', async () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '2026-10-07' }, attachTo: document.body })
    await wrapper.find('button').trigger('click')
    await nextTick()
    expect(dialog()?.textContent).toContain('Octobre 2026')
    day('2026-10-15')!.click()
    await nextTick()
    expect(wrapper.emitted('update:modelValue')).toEqual([['2026-10-15']])
    expect(dialog()).toBeNull()
  })

  it('se déplace au clavier et change de mois', async () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '2026-10-31' }, attachTo: document.body })
    await wrapper.find('button').trigger('click')
    await nextTick()
    await nextTick()
    day('2026-10-31')!.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }))
    await nextTick()
    expect(dialog()?.textContent).toContain('Novembre 2026')
    expect(document.activeElement?.getAttribute('data-date')).toBe('2026-11-01')
  })

  it('désactive les jours hors des bornes', async () => {
    const wrapper = mount(DatePicker, {
      props: { modelValue: '', min: '2026-10-10' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    await nextTick()
    expect(day('2026-10-09')!.disabled).toBe(true)
    expect(day('2026-10-10')!.disabled).toBe(false)
  })

  it('peut être vidé', async () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '2026-10-07' }, attachTo: document.body })
    await wrapper.find('button[aria-label="Effacer la date"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([['']])
  })
})
