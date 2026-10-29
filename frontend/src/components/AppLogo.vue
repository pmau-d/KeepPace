<template>
  <!-- Le dégradé est en CSS : un <linearGradient> SVG référencé par id casse quand
       la première copie du logo est dans un élément masqué (tiroir mobile). -->
  <span
    :class="[
      'inline-flex shrink-0 items-center justify-center bg-linear-to-br from-indigo-500 to-violet-600 shadow-sm',
      sizeClass,
    ]"
    aria-hidden="true"
  >
    <svg viewBox="0 0 64 64" class="w-[72%] h-[72%]">
      <path
        d="M16 31 27 42 48 18"
        fill="none"
        stroke="#fff"
        stroke-width="6.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M16 51h32"
        fill="none"
        stroke="#fff"
        stroke-opacity=".55"
        stroke-width="5"
        stroke-linecap="round"
      />
    </svg>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })

const sizeClass = computed(
  () => ({ sm: 'w-7 h-7 rounded-lg', md: 'w-9 h-9 rounded-xl', lg: 'w-11 h-11 rounded-xl' })[props.size],
)
</script>
