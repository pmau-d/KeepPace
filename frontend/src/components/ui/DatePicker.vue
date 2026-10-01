<template>
  <div class="relative flex items-center" v-bind="$attrs">
    <button
      :id="id"
      ref="trigger"
      type="button"
      :disabled="disabled"
      aria-haspopup="dialog"
      :aria-expanded="open"
      :aria-label="
        ariaLabel ? `${ariaLabel} : ${selected ? formatShortDate(selected) : 'aucune date'}` : undefined
      "
      :class="[
        'w-full inline-flex items-center gap-2 text-sm rounded-lg px-3 py-2 text-left transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:opacity-50',
        'bg-slate-100 hover:bg-slate-200/70 dark:bg-slate-700 dark:hover:bg-slate-600/70',
        open && 'ring-2 ring-indigo-500',
      ]"
      @click="toggleCalendar"
      @keydown.down.prevent="openCalendar"
    >
      <CalendarDays class="w-4 h-4 shrink-0 text-slate-400" aria-hidden="true" />
      <span :class="['flex-1 truncate', selected ? 'text-slate-700 dark:text-slate-100' : 'text-slate-400']">
        {{ selected ? formatShortDate(selected) : placeholder }}
      </span>
    </button>
    <button
      v-if="clearable && selected && !disabled"
      type="button"
      class="absolute right-2 p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600"
      aria-label="Effacer la date"
      @click="setValue('')"
    >
      <X class="w-3.5 h-3.5" aria-hidden="true" />
    </button>
  </div>

  <Teleport to="body">
    <div
      v-if="open"
      ref="panel"
      role="dialog"
      aria-modal="false"
      :aria-label="ariaLabel ?? 'Choisir une date'"
      :style="{ top: `${position.top}px`, left: `${position.left}px` }"
      class="fixed z-[90] w-72 p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xl"
      @keydown.esc.stop.prevent="closeCalendar()"
    >
      <div class="flex items-center justify-between mb-2">
        <button
          type="button"
          class="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
          aria-label="Mois précédent"
          @click="shiftMonth(-1)"
        >
          <ChevronLeft class="w-4 h-4" aria-hidden="true" />
        </button>
        <p class="text-sm font-semibold text-slate-700 dark:text-slate-100" aria-live="polite">
          {{ formatMonth(viewMonth) }}
        </p>
        <button
          type="button"
          class="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
          aria-label="Mois suivant"
          @click="shiftMonth(1)"
        >
          <ChevronRight class="w-4 h-4" aria-hidden="true" />
        </button>
      </div>

      <table role="grid" class="w-full text-center" :aria-label="formatMonth(viewMonth)">
        <thead>
          <tr>
            <th
              v-for="day in WEEKDAYS"
              :key="day.long"
              scope="col"
              :abbr="day.long"
              class="text-[11px] font-medium text-slate-400 pb-1"
            >
              {{ day.short }}
            </th>
          </tr>
        </thead>
        <tbody @keydown="onGridKeydown">
          <tr v-for="(week, w) in weeks" :key="w">
            <td v-for="day in week" :key="day.getTime()" class="p-0.5">
              <button
                type="button"
                :tabindex="isSameDay(day, focused) ? 0 : -1"
                :data-date="toIsoDate(day)"
                :disabled="isDisabled(day)"
                :aria-selected="selected ? isSameDay(day, selected) : false"
                :aria-current="isSameDay(day, today) ? 'date' : undefined"
                :aria-label="formatShortDate(day)"
                :class="dayClass(day)"
                @click="pick(day)"
              >
                {{ day.getDate() }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="flex justify-between mt-2 pt-2 border-t border-slate-100 dark:border-slate-700">
        <button
          type="button"
          class="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline disabled:opacity-40"
          :disabled="isDisabled(today)"
          @click="pick(today)"
        >
          Aujourd'hui
        </button>
        <button
          v-if="clearable"
          type="button"
          class="text-xs text-slate-500 dark:text-slate-400 hover:underline"
          @click="setValue('')"
        >
          Effacer
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { CalendarDays, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import { usePopover } from '../../composables/usePopover'
import {
  addDays,
  addMonths,
  formatMonth,
  formatShortDate,
  isSameDay,
  monthGrid,
  parseIsoDate,
  startOfDay,
  startOfWeek,
  toIsoDate,
} from '../../utils/dates'

const WEEKDAYS = [
  { short: 'L', long: 'lundi' },
  { short: 'M', long: 'mardi' },
  { short: 'M', long: 'mercredi' },
  { short: 'J', long: 'jeudi' },
  { short: 'V', long: 'vendredi' },
  { short: 'S', long: 'samedi' },
  { short: 'D', long: 'dimanche' },
]

// Deux racines (champ + calendrier téléporté) : les attributs vont sur le champ.
defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    /** Date AAAA-MM-JJ, ou chaîne vide pour « aucune date ». */
    modelValue: string
    id?: string
    ariaLabel?: string
    placeholder?: string
    min?: string
    max?: string
    clearable?: boolean
    disabled?: boolean
  }>(),
  {
    id: undefined,
    ariaLabel: undefined,
    placeholder: 'Aucune date',
    min: undefined,
    max: undefined,
    clearable: true,
    disabled: false,
  },
)
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const trigger = ref<HTMLElement | null>(null)
const panel = ref<HTMLElement | null>(null)
const { open, position, show, close } = usePopover(trigger, panel)

const today = startOfDay(new Date())
const selected = computed(() => parseIsoDate(props.modelValue))
const minDate = computed(() => parseIsoDate(props.min))
const maxDate = computed(() => parseIsoDate(props.max))
// Jour qui porte le focus clavier dans la grille
const focused = ref<Date>(today)
const viewMonth = computed(() => new Date(focused.value.getFullYear(), focused.value.getMonth(), 1))
const weeks = computed(() => {
  const days = monthGrid(viewMonth.value)
  return Array.from({ length: 6 }, (_, w) => days.slice(w * 7, w * 7 + 7))
})

function isDisabled(day: Date): boolean {
  return Boolean((minDate.value && day < minDate.value) || (maxDate.value && day > maxDate.value))
}

function dayClass(day: Date) {
  const isSelected = selected.value && isSameDay(day, selected.value)
  const inMonth = day.getMonth() === viewMonth.value.getMonth()
  return [
    'w-9 h-9 rounded-lg text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:opacity-30 disabled:cursor-not-allowed',
    isSelected
      ? 'bg-indigo-600 text-white font-semibold'
      : inMonth
        ? 'text-slate-700 dark:text-slate-200 hover:bg-indigo-50 dark:hover:bg-slate-700'
        : 'text-slate-300 dark:text-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700/50',
    !isSelected && isSameDay(day, today) && 'ring-1 ring-indigo-400 font-semibold',
  ]
}

async function focusDay() {
  await nextTick()
  panel.value?.querySelector<HTMLButtonElement>(`[data-date="${toIsoDate(focused.value)}"]`)?.focus()
}

async function openCalendar() {
  focused.value = selected.value ?? today
  await show()
  await focusDay()
}

function toggleCalendar() {
  if (open.value) closeCalendar()
  else void openCalendar()
}

function closeCalendar(refocus = true) {
  close()
  if (refocus) trigger.value?.focus()
}

function setValue(value: string) {
  if (value !== props.modelValue) emit('update:modelValue', value)
  if (open.value) closeCalendar()
}

function pick(day: Date) {
  if (!isDisabled(day)) setValue(toIsoDate(day))
}

function shiftMonth(months: number) {
  focused.value = addMonths(focused.value, months)
}

function onGridKeydown(event: KeyboardEvent) {
  const moves: Record<string, () => Date> = {
    ArrowLeft: () => addDays(focused.value, -1),
    ArrowRight: () => addDays(focused.value, 1),
    ArrowUp: () => addDays(focused.value, -7),
    ArrowDown: () => addDays(focused.value, 7),
    Home: () => startOfWeek(focused.value),
    End: () => addDays(startOfWeek(focused.value), 6),
    PageUp: () => addMonths(focused.value, event.shiftKey ? -12 : -1),
    PageDown: () => addMonths(focused.value, event.shiftKey ? 12 : 1),
  }
  const next = moves[event.key]
  if (!next) return
  event.preventDefault()
  focused.value = next()
  void focusDay()
}
</script>
