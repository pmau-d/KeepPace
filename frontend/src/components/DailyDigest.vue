<template>
  <section
    v-if="digest"
    aria-labelledby="digest-title"
    class="rounded-xl border border-indigo-100 dark:border-indigo-900/60 bg-indigo-50/60 dark:bg-indigo-950/30 p-4 space-y-3"
  >
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2
          id="digest-title"
          class="text-sm font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2"
        >
          <Sunrise class="w-4 h-4 text-indigo-500" aria-hidden="true" />
          Récap du {{ formatDayHeading(parseIsoDate(digest.day)!).toLowerCase() }}
        </h2>
        <p class="text-sm text-slate-600 dark:text-slate-300 mt-1">{{ summary }}</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          type="button"
          role="switch"
          :aria-checked="optIn"
          :disabled="!digest.email_available || saving"
          :title="digest.email_available ? '' : 'L\'envoi d\'emails n\'est pas configuré sur ce serveur'"
          class="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300 disabled:opacity-50"
          @click="toggle"
        >
          <span
            :class="[
              'relative w-8 h-4 rounded-full transition-colors shrink-0',
              optIn ? 'bg-indigo-500' : 'bg-slate-300 dark:bg-slate-600',
            ]"
          >
            <span
              :class="[
                'absolute top-0.5 w-3 h-3 bg-white rounded-full shadow-sm transition-transform',
                optIn ? 'translate-x-4' : 'translate-x-0.5',
              ]"
            ></span>
          </span>
          Recevoir par email chaque matin
        </button>
        <button
          v-if="digest.email_available"
          type="button"
          :disabled="sending"
          class="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline disabled:opacity-50"
          @click="sendNow"
        >
          M'envoyer maintenant
        </button>
      </div>
    </div>

    <div v-if="digest.leaving.length || digest.returning.length" class="grid sm:grid-cols-2 gap-3 text-sm">
      <div v-if="digest.leaving.length">
        <p class="text-xs font-semibold text-orange-600 dark:text-orange-400 mb-1">Partent bientôt</p>
        <ul class="space-y-0.5 text-slate-600 dark:text-slate-300">
          <li v-for="c in digest.leaving" :key="c.id">{{ c.name }} · le {{ day(c.on) }}</li>
        </ul>
      </div>
      <div v-if="digest.returning.length">
        <p class="text-xs font-semibold text-blue-600 dark:text-blue-400 mb-1">Reviennent bientôt</p>
        <ul class="space-y-0.5 text-slate-600 dark:text-slate-300">
          <li v-for="c in digest.returning" :key="c.id">{{ c.name }} · le {{ day(c.on) }}</li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Sunrise } from '@lucide/vue'
import { digestApi } from '../api/index'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { formatCompactDate, formatDayHeading, parseIsoDate } from '../utils/dates'
import type { Digest, IsoDate } from '../types/api'

const props = withDefaults(defineProps<{ version?: number }>(), { version: 0 })

const auth = useAuthStore()
const toast = useToastStore()
const digest = ref<Digest | null>(null)
const saving = ref(false)
const sending = ref(false)
const optIn = computed(() => auth.user?.digest_opt_in ?? false)

const plural = (count: number, one: string, many: string) => `${count} ${count > 1 ? many : one}`

const summary = computed(() => {
  const d = digest.value
  if (!d) return ''
  const parts = [
    d.follow_up_total
      ? plural(d.follow_up_total, 'tâche à relancer', 'tâches à relancer')
      : 'Aucune relance aujourd’hui',
  ]
  if (d.leaving.length)
    parts.push(plural(d.leaving.length, 'client part', 'clients partent') + ' dans les 3 jours')
  if (d.returning.length)
    parts.push(plural(d.returning.length, 'client revient', 'clients reviennent') + ' bientôt')
  return `${parts.join(', ')}.`
})

function day(value: IsoDate | null) {
  const date = parseIsoDate(value)
  return date ? formatCompactDate(date) : '—'
}

async function load() {
  digest.value = (await digestApi.get()).data
}

async function toggle() {
  saving.value = true
  try {
    await auth.setDigestOptIn(!optIn.value)
    toast.success(optIn.value ? 'Récap activé : il arrivera chaque matin.' : 'Récap par email désactivé.')
  } catch (error) {
    toast.error(error)
  } finally {
    saving.value = false
  }
}

async function sendNow() {
  sending.value = true
  try {
    const { data } = await digestApi.sendNow()
    toast.success(`Récap envoyé à ${data.sent_to}`)
  } catch (error) {
    toast.error(error, "Le récap n'a pas pu être envoyé.")
  } finally {
    sending.value = false
  }
}

watch(() => props.version, load)
onMounted(load)
</script>
