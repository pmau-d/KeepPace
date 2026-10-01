import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { isTyping, useShortcuts, type Shortcut } from '../useShortcuts'

function setup(shortcuts: Shortcut[]) {
  return mount(
    defineComponent({
      setup() {
        useShortcuts(() => shortcuts)
        return () => h('input', { id: 'field' })
      },
    }),
    { attachTo: document.body },
  )
}

const press = (key: string, init: KeyboardEventInit = {}, target: EventTarget = window) =>
  target.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true, ...init }))

describe('raccourcis clavier', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('déclenche une touche seule, une séquence et Ctrl/⌘ K', () => {
    const newTask = vi.fn()
    const goBoard = vi.fn()
    const palette = vi.fn()
    const wrapper = setup([
      { keys: ['n'], run: newTask },
      { keys: ['g', 'b'], run: goBoard },
      { keys: ['k'], mod: true, run: palette },
    ])
    press('n')
    press('g')
    press('b')
    press('k', { metaKey: true })
    press('k', { ctrlKey: true })
    expect(newTask).toHaveBeenCalledOnce()
    expect(goBoard).toHaveBeenCalledOnce()
    expect(palette).toHaveBeenCalledTimes(2)
    wrapper.unmount()
  })

  it('ignore les touches seules pendant la saisie, pas Ctrl/⌘ K', () => {
    const newTask = vi.fn()
    const palette = vi.fn()
    const wrapper = setup([
      { keys: ['n'], run: newTask },
      { keys: ['k'], mod: true, run: palette },
    ])
    const field = document.querySelector('#field')!
    expect(isTyping(field)).toBe(true)
    press('n', {}, field)
    press('k', { ctrlKey: true }, field)
    expect(newTask).not.toHaveBeenCalled()
    expect(palette).toHaveBeenCalledOnce()
    wrapper.unmount()
  })
})
