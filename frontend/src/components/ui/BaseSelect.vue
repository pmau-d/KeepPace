<template>
  <button
    :id="id"
    ref="trigger"
    v-bind="$attrs"
    type="button"
    :disabled="disabled"
    aria-haspopup="listbox"
    :aria-expanded="open"
    :aria-controls="open ? listId : undefined"
    :aria-label="ariaLabel"
    :class="[
      'inline-flex items-center gap-2 text-sm rounded-lg text-left transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:opacity-50',
      'bg-slate-100 hover:bg-slate-200/70 dark:bg-slate-700 dark:hover:bg-slate-600/70 text-slate-700 dark:text-slate-100',
      block ? 'w-full px-3 py-2' : 'px-3 py-2',
      open && 'ring-2 ring-indigo-500',
    ]"
    @click="toggleList"
    @keydown="onTriggerKeydown"
  >
    <span
      v-if="current?.dot"
      :class="['w-2 h-2 rounded-full shrink-0', current.dot]"
      aria-hidden="true"
    ></span>
    <component :is="current.icon" v-if="current?.icon" class="w-4 h-4 shrink-0" aria-hidden="true" />
    <span :class="['flex-1 truncate', !current && 'text-slate-400']">{{
      current?.label ?? placeholder
    }}</span>
    <ChevronDown
      :class="['w-4 h-4 shrink-0 text-slate-400 transition-transform', open && 'rotate-180']"
      aria-hidden="true"
    />
  </button>

  <Teleport to="body">
    <ul
      v-if="open"
      :id="listId"
      ref="panel"
      role="listbox"
      tabindex="-1"
      :aria-label="ariaLabel"
      :aria-activedescendant="activeIndex >= 0 ? optionId(activeIndex) : undefined"
      :style="{ top: `${position.top}px`, left: `${position.left}px`, minWidth: `${position.minWidth}px` }"
      class="fixed z-[90] max-h-72 overflow-y-auto py-1 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xl focus:outline-none popover-in"
      @keydown="onListKeydown"
    >
      <li
        v-for="(option, index) in options"
        :id="optionId(index)"
        :key="option.value"
        role="option"
        :aria-selected="option.value === modelValue"
        :class="[
          'flex items-center gap-2 px-3 py-2 text-sm cursor-pointer select-none whitespace-nowrap',
          index === activeIndex ? 'bg-indigo-50 dark:bg-slate-700' : '',
          option.value === modelValue
            ? 'text-indigo-700 dark:text-indigo-300 font-medium'
            : 'text-slate-700 dark:text-slate-200',
        ]"
        @mousemove="activeIndex = index"
        @click="select(option)"
      >
        <span
          v-if="option.dot"
          :class="['w-2 h-2 rounded-full shrink-0', option.dot]"
          aria-hidden="true"
        ></span>
        <component :is="option.icon" v-if="option.icon" class="w-4 h-4 shrink-0" aria-hidden="true" />
        <span class="flex-1">{{ option.label }}</span>
        <Check v-if="option.value === modelValue" class="w-4 h-4 shrink-0" aria-hidden="true" />
      </li>
    </ul>
  </Teleport>
</template>

<script setup lang="ts" generic="T extends string">
import { computed, nextTick, ref, useId, type Component } from 'vue'
import { Check, ChevronDown } from 'lucide-vue-next'
import { usePopover } from '../../composables/usePopover'

export interface SelectOption<V extends string = string> {
  value: V
  label: string
  /** Classe Tailwind d'une pastille de couleur (ex. présence). */
  dot?: string
  icon?: Component
}

// Deux racines (bouton + liste téléportée) : les attributs du parent (class…)
// vont explicitement sur le bouton.
defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    modelValue: T
    options: SelectOption<T>[]
    id?: string
    /** Nom accessible, quand aucun <label for> ne désigne le contrôle. */
    ariaLabel?: string
    placeholder?: string
    block?: boolean
    disabled?: boolean
  }>(),
  { id: undefined, ariaLabel: undefined, placeholder: 'Choisir…', block: false, disabled: false },
)
const emit = defineEmits<{ 'update:modelValue': [value: T]; change: [value: T] }>()

const trigger = ref<HTMLElement | null>(null)
const panel = ref<HTMLElement | null>(null)
const { open, position, show, close } = usePopover(trigger, panel)
const activeIndex = ref(-1)
const listId = `select-${useId()}`
const optionId = (index: number) => `${listId}-option-${index}`

const current = computed(() => props.options.find((o) => o.value === props.modelValue))
const selectedIndex = () => props.options.findIndex((o) => o.value === props.modelValue)

async function openList(index = selectedIndex()) {
  activeIndex.value = index >= 0 ? index : 0
  await show()
  await nextTick()
  panel.value?.focus()
  scrollToActive()
}

function toggleList() {
  if (open.value) closeList()
  else void openList()
}

function closeList(refocus = true) {
  close()
  if (refocus) trigger.value?.focus()
}

function select(option: SelectOption<T>) {
  if (option.value !== props.modelValue) {
    emit('update:modelValue', option.value)
    emit('change', option.value)
  }
  closeList()
}

function scrollToActive() {
  panel.value
    ?.querySelector(`#${CSS.escape(optionId(activeIndex.value))}`)
    ?.scrollIntoView({ block: 'nearest' })
}

function move(to: number) {
  const count = props.options.length
  activeIndex.value = Math.max(0, Math.min(count - 1, to))
  scrollToActive()
}

function onTriggerKeydown(event: KeyboardEvent) {
  if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(event.key)) {
    event.preventDefault()
    const start = selectedIndex()
    void openList(event.key === 'ArrowUp' && start < 0 ? props.options.length - 1 : start)
  }
}

let typed = ''
let typedTimer: ReturnType<typeof setTimeout> | undefined

function onListKeydown(event: KeyboardEvent) {
  const option = props.options[activeIndex.value]
  switch (event.key) {
    case 'ArrowDown':
      move(activeIndex.value + 1)
      break
    case 'ArrowUp':
      move(activeIndex.value - 1)
      break
    case 'Home':
      move(0)
      break
    case 'End':
      move(props.options.length - 1)
      break
    case 'Enter':
    case ' ':
      if (option) select(option)
      break
    case 'Escape':
      closeList()
      break
    case 'Tab':
      closeList(false)
      return
    default:
      // Saisie au clavier : aller à la première option qui commence par les lettres tapées.
      if (event.key.length === 1 && !event.ctrlKey && !event.metaKey) {
        typed += event.key.toLowerCase()
        clearTimeout(typedTimer)
        typedTimer = setTimeout(() => (typed = ''), 600)
        const found = props.options.findIndex((o) => o.label.toLowerCase().startsWith(typed))
        if (found >= 0) move(found)
        break
      }
      return
  }
  event.preventDefault()
}
</script>

<style scoped>
.popover-in {
  animation: popoverIn 0.12s ease-out;
}
@keyframes popoverIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
