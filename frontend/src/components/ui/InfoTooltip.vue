<template>
  <button
    ref="trigger"
    type="button"
    class="p-0.5 rounded-sm text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
    :aria-label="label"
    :aria-expanded="open"
    :aria-describedby="open ? tooltipId : undefined"
    @mouseenter="show"
    @mouseleave="close"
    @focus="show"
    @blur="close"
    @click="toggle"
    @keydown.esc="close"
  >
    <Info class="w-3.5 h-3.5" aria-hidden="true" />
  </button>
  <Teleport to="body">
    <div
      v-if="open"
      :id="tooltipId"
      ref="panel"
      role="tooltip"
      :style="{ top: `${position.top}px`, left: `${position.left}px` }"
      class="fixed z-[90] w-56 p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xl text-xs text-slate-600 dark:text-slate-300"
    >
      <slot />
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, useId } from 'vue'
import { Info } from '@lucide/vue'
import { usePopover } from '../../composables/usePopover'

defineProps<{ label: string }>()

const trigger = ref<HTMLElement | null>(null)
const panel = ref<HTMLElement | null>(null)
const { open, position, show, close, toggle } = usePopover(trigger, panel)
const tooltipId = `tooltip-${useId()}`
</script>
