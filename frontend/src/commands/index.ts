// Commandes communes à la palette (Ctrl/⌘ K) et aux raccourcis clavier.
import { ref, type Component } from 'vue'
import type { Router } from 'vue-router'
import {
  Archive,
  CalendarRange,
  Download,
  Keyboard,
  ListTodo,
  Megaphone,
  Moon,
  Plus,
  Rows3,
  Search,
  SquareKanban,
  Upload,
} from '@lucide/vue'

export interface Command {
  id: string
  label: string
  group: 'Aller à' | 'Actions' | 'Affichage'
  icon: Component
  /** Raccourci affiché : ['g', 't'] ou ['n']. */
  hint?: string[]
  keywords?: string
  run: () => void
}

/** Ouvertures demandées par une commande, écoutées par les vues concernées. */
export const ui = {
  palette: ref(false),
  help: ref(false),
  importAbsences: ref(false),
}

interface Context {
  router: Router
  toggleDark: () => void
  toggleDensity: () => void
  exportUrl: () => string
}

export function buildCommands({ router, toggleDark, toggleDensity, exportUrl }: Context): Command[] {
  const go = (name: string, query?: Record<string, string>) => () => void router.push({ name, query })
  return [
    {
      id: 'tasks',
      label: 'Toutes les tâches',
      group: 'Aller à',
      icon: ListTodo,
      hint: ['g', 't'],
      run: go('tasks'),
    },
    {
      id: 'board',
      label: 'Tableau',
      group: 'Aller à',
      icon: SquareKanban,
      hint: ['g', 'b'],
      keywords: 'kanban statut',
      run: go('board'),
    },
    {
      id: 'follow-up',
      label: 'À relancer',
      group: 'Aller à',
      icon: Megaphone,
      hint: ['g', 'r'],
      keywords: 'relances récap',
      run: go('follow-up'),
    },
    {
      id: 'planning',
      label: 'Planning',
      group: 'Aller à',
      icon: CalendarRange,
      hint: ['g', 'p'],
      keywords: 'absences calendrier',
      run: go('planning'),
    },
    {
      id: 'archives',
      label: 'Archives',
      group: 'Aller à',
      icon: Archive,
      hint: ['g', 'a'],
      run: go('archives'),
    },
    {
      id: 'new-task',
      label: 'Nouvelle tâche',
      group: 'Actions',
      icon: Plus,
      hint: ['n'],
      keywords: 'créer ajouter',
      run: go('tasks', { nouvelle: '1' }),
    },
    {
      id: 'search',
      label: 'Rechercher une tâche',
      group: 'Actions',
      icon: Search,
      hint: ['/'],
      run: async () => {
        if (router.currentRoute.value.name !== 'tasks') await router.push({ name: 'tasks' })
        document.querySelector<HTMLInputElement>('#task-search')?.focus()
      },
    },
    {
      id: 'import',
      label: 'Importer des absences (.ics)',
      group: 'Actions',
      icon: Upload,
      keywords: 'calendrier congés',
      run: () => (ui.importAbsences.value = true),
    },
    {
      id: 'export',
      label: 'Exporter les tâches (CSV)',
      group: 'Actions',
      icon: Download,
      keywords: 'excel',
      run: () => window.location.assign(exportUrl()),
    },
    {
      id: 'dark',
      label: 'Basculer le mode sombre',
      group: 'Affichage',
      icon: Moon,
      hint: ['d'],
      keywords: 'thème clair',
      run: toggleDark,
    },
    {
      id: 'density',
      label: 'Basculer l’affichage compact',
      group: 'Affichage',
      icon: Rows3,
      keywords: 'densité',
      run: toggleDensity,
    },
    {
      id: 'help',
      label: 'Raccourcis clavier',
      group: 'Affichage',
      icon: Keyboard,
      hint: ['?'],
      keywords: 'aide',
      run: () => (ui.help.value = true),
    },
  ]
}
