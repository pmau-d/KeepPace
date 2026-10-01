import { afterEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import BaseSelect from '../BaseSelect.vue'

const options = [
  { value: 'TODO', label: 'À faire' },
  { value: 'IN_PROGRESS', label: 'En cours' },
  { value: 'DONE', label: 'Terminé' },
]

function mountSelect(modelValue = 'TODO') {
  return mount(BaseSelect, {
    props: { modelValue, options, ariaLabel: 'Statut' },
    attachTo: document.body,
  })
}

const listbox = () => document.querySelector<HTMLElement>('[role="listbox"]')

describe('BaseSelect', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('affiche le libellé de la valeur et ouvre la liste au clic', async () => {
    const wrapper = mountSelect('IN_PROGRESS')
    expect(wrapper.find('button').text()).toContain('En cours')
    await wrapper.find('button').trigger('click')
    await nextTick()
    expect(listbox()).not.toBeNull()
    expect(wrapper.find('button').attributes('aria-expanded')).toBe('true')
    const selected = document.querySelector('[role="option"][aria-selected="true"]')
    expect(selected?.textContent).toContain('En cours')
  })

  it('se pilote au clavier : flèches puis Entrée', async () => {
    const wrapper = mountSelect('TODO')
    await wrapper.find('button').trigger('keydown', { key: 'ArrowDown' })
    await nextTick()
    const list = listbox()!
    list.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }))
    list.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    await nextTick()
    expect(wrapper.emitted('update:modelValue')).toEqual([['IN_PROGRESS']])
    expect(listbox()).toBeNull()
  })

  it('va à une option en tapant ses premières lettres, et Échap referme sans choisir', async () => {
    const wrapper = mountSelect('TODO')
    await wrapper.find('button').trigger('click')
    await nextTick()
    const list = listbox()!
    list.dispatchEvent(new KeyboardEvent('keydown', { key: 't', bubbles: true }))
    await nextTick()
    expect(list.getAttribute('aria-activedescendant')).toMatch(/option-2$/)
    list.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    await nextTick()
    expect(listbox()).toBeNull()
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
  })

  it('ne signale pas de changement quand on choisit la valeur actuelle', async () => {
    const wrapper = mountSelect('TODO')
    await wrapper.find('button').trigger('click')
    await nextTick()
    document.querySelector<HTMLElement>('[role="option"]')!.click()
    await nextTick()
    expect(wrapper.emitted('change')).toBeUndefined()
  })
})
