import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ChecklistEditor from '../ChecklistEditor.vue'
import type { ChecklistItem } from '../../../types/api'

const item = (id: string, done = false): ChecklistItem => ({ id, label: `Case ${id}`, done, position: 0 })

function mountEditor(items: ChecklistItem[], canFinish = true) {
  return mount(ChecklistEditor, { props: { items, canFinish } })
}

describe('ChecklistEditor', () => {
  it('affiche les cases et leur état', () => {
    const wrapper = mountEditor([item('a', true), item('b')])
    const boxes = wrapper.findAll('input[type="checkbox"]')
    expect(boxes.map((box) => (box.element as HTMLInputElement).checked)).toEqual([true, false])
    expect(wrapper.text()).toContain('Case a')
  })

  it('explique le principe quand la checklist est vide', () => {
    expect(mountEditor([]).text()).toContain('décochées à chaque occurrence')
  })

  it('signale la case à cocher ou décocher', async () => {
    const wrapper = mountEditor([item('a')])
    await wrapper.find('input[type="checkbox"]').trigger('change')
    expect(wrapper.emitted('toggle')?.[0]).toEqual([item('a')])
  })

  it('ajoute une case sans espaces superflus puis vide le champ', async () => {
    const wrapper = mountEditor([])
    const input = wrapper.find('input[type="text"]')
    await input.setValue('  Relire les tickets ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('add')?.[0]).toEqual(['Relire les tickets'])
    expect((input.element as HTMLInputElement).value).toBe('')
  })

  it("n'ajoute pas de case vide", async () => {
    const wrapper = mountEditor([])
    await wrapper.find('input[type="text"]').setValue('   ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('add')).toBeUndefined()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
  })

  it('supprime une case', async () => {
    const wrapper = mountEditor([item('a')])
    await wrapper.find('button[aria-label^="Supprimer"]').trigger('click')
    expect(wrapper.emitted('remove')?.[0]).toEqual([item('a')])
  })

  it('propose de terminer la tâche seulement quand tout est coché', async () => {
    expect(
      mountEditor([item('a', true), item('b')])
        .find('[role="status"]')
        .exists(),
    ).toBe(false)
    const complete = mountEditor([item('a', true), item('b', true)])
    expect(complete.find('[role="status"]').text()).toContain('Tout est coché')
    await complete.find('[role="status"] button').trigger('click')
    expect(complete.emitted('finish')).toHaveLength(1)
  })

  it("ne propose rien si la tâche n'est pas terminable ou sans case", () => {
    expect(
      mountEditor([item('a', true)], false)
        .find('[role="status"]')
        .exists(),
    ).toBe(false)
    expect(mountEditor([]).find('[role="status"]').exists()).toBe(false)
  })
})
