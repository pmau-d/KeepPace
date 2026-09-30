<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-900 p-4">
    <div class="w-full max-w-sm">
      <div class="flex items-center gap-3 justify-center mb-8">
        <div
          class="w-11 h-11 bg-linear-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center shadow-sm"
        >
          <span class="text-white font-bold">KP</span>
        </div>
        <div>
          <p class="font-bold text-xl text-slate-800 dark:text-white leading-none">KeepPace</p>
          <p class="text-xs text-slate-400 mt-1">Suivi des tâches et des relances clients</p>
        </div>
      </div>

      <form
        class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 space-y-4"
        novalidate
        @submit.prevent="submit"
      >
        <h1 class="text-lg font-semibold text-slate-800 dark:text-slate-100">
          {{ isRegister ? 'Créer un compte' : 'Connexion' }}
        </h1>

        <div v-if="isRegister">
          <label for="full-name" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Nom <span class="text-slate-400 font-normal text-xs">(optionnel)</span>
          </label>
          <input id="full-name" v-model="form.fullName" type="text" autocomplete="name" :class="inputClass" />
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >Email</label
          >
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            autocomplete="email"
            autofocus
            :class="inputClass"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Mot de passe
          </label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            :minlength="isRegister ? 10 : undefined"
            :autocomplete="isRegister ? 'new-password' : 'current-password'"
            :class="inputClass"
          />
          <p v-if="isRegister" class="text-xs text-slate-400 mt-1">10 caractères minimum.</p>
        </div>

        <p v-if="error" role="alert" class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>

        <button
          type="submit"
          :disabled="submitting"
          class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors"
        >
          {{ submitting ? 'Veuillez patienter…' : isRegister ? 'Créer mon compte' : 'Se connecter' }}
        </button>

        <p class="text-sm text-center text-slate-500 dark:text-slate-400">
          <template v-if="isRegister">
            Déjà un compte ?
            <RouterLink
              :to="{ name: 'login', query: route.query }"
              class="text-indigo-600 dark:text-indigo-400 font-medium"
            >
              Se connecter
            </RouterLink>
          </template>
          <template v-else>
            Pas encore de compte ?
            <RouterLink
              :to="{ name: 'register', query: route.query }"
              class="text-indigo-600 dark:text-indigo-400 font-medium"
            >
              Créer un compte
            </RouterLink>
          </template>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { errorMessage } from '../api/index.js'
import { useAuthStore } from '../stores/auth.js'

const props = defineProps({ mode: { type: String, default: 'login' } })

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const isRegister = computed(() => props.mode === 'register')
const form = reactive({ email: '', password: '', fullName: '' })
const error = ref('')
const submitting = ref(false)

const inputClass =
  'w-full text-sm bg-slate-100 dark:bg-slate-700 dark:text-slate-100 border-0 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500'

watch(isRegister, () => {
  error.value = ''
})

/** Seules les redirections internes sont suivies (pas de « //site-externe »). */
function redirectTarget() {
  const target = route.query.redirect
  return typeof target === 'string' && target.startsWith('/') && !target.startsWith('//') ? target : '/'
}

async function submit() {
  if (!form.email || !form.password) {
    error.value = 'Renseignez votre email et votre mot de passe.'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    if (isRegister.value) {
      await auth.register({ email: form.email, password: form.password, full_name: form.fullName || null })
    } else {
      await auth.login(form.email, form.password)
    }
    await router.replace(redirectTarget())
  } catch (e) {
    error.value = errorMessage(e, isRegister.value ? 'Inscription impossible.' : 'Connexion impossible.')
  } finally {
    submitting.value = false
  }
}
</script>
