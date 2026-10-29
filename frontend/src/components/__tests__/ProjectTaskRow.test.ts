import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../api/index', () => ({
  projectTasksApi: { addChecklistItem: vi.fn(), updateChecklistItem: vi.fn(), deleteChecklistItem: vi.fn() },
}))

import { projectTasksApi } from '../../api/index'
import ProjectTaskRow from '../ProjectTaskRow.vue'
import { makeProjectTask, response } from '../../test/factories'

const checklist = [
  { id: 'c1', label: 'Relire', done: true, position: 0 },
  { id: 'c2', label: 'Trier', done: false, position: 1 },
]

function mountRow(overrides = {}) {
  return mount(ProjectTaskRow, { props: { task: makeProjectTask({ id: 't1', checklist, ...overrides }) } })
}

describe('ProjectTaskRow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('résume la progression de la checklist et la déplie à la demande', async () => {
    const wrapper = mountRow()
    const toggle = wrapper.find('button[aria-label^="Checklist"]')
    expect(toggle.text()).toBe('1/2')
    expect(wrapper.find('input[type="checkbox"]').exists()).toBe(false)
    await toggle.trigger('click')
    expect(wrapper.findAll('input[type="checkbox"]')).toHaveLength(2)
  })

  it("propose « Checklist » quand il n'y a aucune case", () => {
    expect(mountRow({ checklist: [] }).find('button[aria-label^="Checklist"]').text()).toBe('Checklist')
  })

  it("coche une case via l'API puis demande le rechargement", async () => {
    vi.mocked(projectTasksApi.updateChecklistItem).mockResolvedValue(response(checklist[1]) as never)
    const wrapper = mountRow()
    await wrapper.find('button[aria-label^="Checklist"]').trigger('click')
    await wrapper.findAll('input[type="checkbox"]')[1]!.trigger('change')
    await flushPromises()
    expect(projectTasksApi.updateChecklistItem).toHaveBeenCalledWith('t1', 'c2', { done: true })
    expect(wrapper.emitted('changed')).toHaveLength(1)
  })

  it("ajoute une case via l'API", async () => {
    vi.mocked(projectTasksApi.addChecklistItem).mockResolvedValue(response(checklist[0]) as never)
    const wrapper = mountRow({ checklist: [] })
    await wrapper.find('button[aria-label^="Checklist"]').trigger('click')
    await wrapper.find('input[type="text"]').setValue('Relire')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(projectTasksApi.addChecklistItem).toHaveBeenCalledWith('t1', 'Relire')
    expect(wrapper.emitted('changed')).toHaveLength(1)
  })

  it('termine la tâche depuis le bandeau quand tout est coché', async () => {
    const all = checklist.map((c) => ({ ...c, done: true }))
    const wrapper = mountRow({ checklist: all })
    await wrapper.find('button[aria-label^="Checklist"]').trigger('click')
    await wrapper.find('[role="status"] button').trigger('click')
    expect(wrapper.emitted('toggle')).toHaveLength(1)
  })
})
