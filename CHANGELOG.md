# Journal des modifications

Toutes les évolutions notables de ce projet sont consignées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
projet respecte le [versionnage sémantique](https://semver.org/lang/fr/).

## [Non publié]

## [1.1.0] — 2026-10-01

### Ajouté

- **Tableau** (Kanban) par statut, au glisser-déposer ou au clavier.
- **Planning** : absences des clients en barres et échéances sur 2 à 8 semaines.
- **Tâches récurrentes** (jour, semaine, mois, année, avec intervalle) :
  terminer une occurrence crée la suivante, une seule fois et sans dériver.
- **« Relancer dans N jours »** (tracé dans l'historique) et brouillon d'email
  de relance prérempli.
- **Récap quotidien** dans « À relancer » et par email chaque matin pour les
  comptes qui l'activent (désactivé par défaut, SMTP configurable, Mailpit en
  développement).
- **Import des absences** depuis un calendrier `.ics` et reconnaissance des
  dates d'une réponse automatique collée (français et anglais).
- **Palette de commandes** (Ctrl/⌘ K) et raccourcis clavier (`n`, `/`,
  `g` puis `t`/`b`/`r`/`p`/`a`, `d`, `?`).
- Nombre de tâches ouvertes par client dans la barre latérale ; tiroir de
  navigation sur téléphone.
- Blueprint Render (`render.yaml`) et mode démo (`DEMO_MODE`) pour une démo
  publique ; `BACKEND_URL` pour l'image frontend.
- README en anglais, GIF de démonstration, nouvelles captures.

### Modifié

- Frontend migré en **TypeScript strict** (vue-tsc dans le lint et la CI).
- La priorité devient un drapeau ; les pastilles de couleur sont réservées à
  la présence des clients. Icônes Lucide à la place des emojis.
- Menus déroulants et sélecteur de date maison, cohérents en clair et en
  sombre, utilisables au clavier.
- Titres de jour et dates au même format (« Mercredi 7 octobre », « mar.
  29 sept. ») ; mode compact de la liste ; absence d'un client expliquée sur
  ses tâches ; légende des présences en info-bulle.

### Corrigé

- Les tests de migration ne laissent plus de données dans la base PostgreSQL
  partagée de la CI.

## [1.0.0] — 2026-09-30

Première version publique.

### Ajouté

- Comptes utilisateurs (inscription, connexion, déconnexion) ; chaque compte ne
  voit que ses propres entreprises, clients et tâches.
- Vue « À relancer aujourd'hui » avec le motif de chaque relance.
- Export CSV des tâches filtrées, compatible Excel.
- Date de début d'absence des clients et statut « Bientôt absent ».
- Archives : restauration des tâches, clients et entreprises archivés, bouton
  « Annuler » après un archivage.
- Recherche dans les titres, descriptions et commentaires ; liste paginée.
- Une URL par tâche ; toasts de succès et d'erreur ; boîtes de confirmation.
- Script de données de démonstration fictives.
- Images Docker de production (nginx, API sans root), healthchecks,
  `docker-compose.prod.yml`.
- Migrations Alembic, tests pytest et Vitest, lint (ruff, ESLint, Prettier),
  intégration continue GitHub Actions.

### Modifié

- Supprimer archive au lieu d'effacer : l'historique des tâches est conservé,
  avec des libellés lisibles.
- La règle de présence n'existe plus qu'une fois (expression SQL) et
  « aujourd'hui » est évalué dans le fuseau configuré.
- Statut et priorité validés par l'API et contraints en base ; horodatages
  avec fuseau horaire.
- Dépendances mises à jour (FastAPI, SQLAlchemy 2.1, Vue 3.5, Vite 8,
  Tailwind CSS 4).

### Supprimé

- Point d'accès `DELETE /admin/reset`, qui effaçait toute la base sans contrôle.

### Sécurité

- Mots de passe hachés en Argon2, cookie de session `httpOnly`, limitation des
  tentatives de connexion, CORS fermé par défaut, identifiants hors du code.

[Non publié]: https://github.com/pmau-d/KeepPace/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/pmau-d/KeepPace/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/pmau-d/KeepPace/releases/tag/v1.0.0
