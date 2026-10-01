import { nextTick, onBeforeUnmount, ref, type Ref } from 'vue'

export interface PopoverPosition {
  top: number
  left: number
  minWidth: number
}

/**
 * Popover affiché dans <body> (Teleport) et positionné sous son déclencheur.
 * Il échappe ainsi aux conteneurs `overflow: auto` (panneau de tâche, modales)
 * qui le couperaient, et remonte au-dessus du bouton s'il manque de place.
 */
export function usePopover(trigger: Ref<HTMLElement | null>, panel: Ref<HTMLElement | null>) {
  const open = ref(false)
  const position = ref<PopoverPosition>({ top: 0, left: 0, minWidth: 0 })

  function place() {
    const anchor = trigger.value?.getBoundingClientRect()
    if (!anchor) return
    const height = panel.value?.offsetHeight ?? 0
    const width = panel.value?.offsetWidth ?? anchor.width
    const spaceBelow = window.innerHeight - anchor.bottom
    const top =
      spaceBelow < height + 8 && anchor.top > height + 8 ? anchor.top - height - 4 : anchor.bottom + 4
    const left = Math.min(anchor.left, Math.max(8, window.innerWidth - width - 8))
    position.value = { top, left, minWidth: anchor.width }
  }

  function onPointerDown(event: PointerEvent) {
    const target = event.target as Node
    if (trigger.value?.contains(target) || panel.value?.contains(target)) return
    close()
  }

  function onScroll(event: Event) {
    // Le défilement interne du popover (longue liste) ne le ferme pas.
    if (panel.value?.contains(event.target as Node)) return
    close()
  }

  async function show() {
    if (open.value) return
    open.value = true
    await nextTick()
    place()
    document.addEventListener('pointerdown', onPointerDown, true)
    window.addEventListener('scroll', onScroll, true)
    window.addEventListener('resize', close)
  }

  function close() {
    if (!open.value) return
    open.value = false
    document.removeEventListener('pointerdown', onPointerDown, true)
    window.removeEventListener('scroll', onScroll, true)
    window.removeEventListener('resize', close)
  }

  function toggle() {
    return open.value ? close() : show()
  }

  onBeforeUnmount(close)

  return { open, position, show, close, toggle, place }
}
