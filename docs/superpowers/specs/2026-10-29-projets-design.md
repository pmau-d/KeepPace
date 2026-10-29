# Projets de développement, vitrine publique et checklists

Date : 2026-10-29 · Statut : à valider

## Contexte

KeepPace sert aujourd'hui au suivi de tâches clients, entièrement privé (chaque
route exige une connexion, chaque donnée a un `owner_id`). Le besoin : suivre aussi
des **projets de développement**, dont une vitrine est **publique**, avec leurs
bugs et retours après présentation, et des **tâches récurrentes à checklist**
(« check ticket de bug »). La clientèle reste strictement privée.

## Décisions

- Un projet est une **entité séparée** des clients (pas de présence ni de relance).
- Le public voit une **vitrine seule** : nom, description, statut, avancement,
  jalons et tâches terminées. Tâches en cours, bugs, retours, commentaires et
  historique restent privés.
- Entrée publique : **`/projets`** (galerie) et **`/projets/:slug`**. La connexion
  reste sur `/login`. `/` reste le tableau de bord privé.
- Les tâches de projet ont un **type** : tâche, bug ou amélioration.
- Le mode « check ticket » est une **checklist par tâche**, réinitialisée à chaque
  occurrence d'une tâche récurrente.
- Récurrence « toutes les 2 semaines » : déjà possible (`WEEKLY`, intervalle 2).

## 1. Modèle de données

Nouvelles migrations Alembic (0008 et suivantes), sans toucher aux données existantes.

- `projects` : `id`, `owner_id`, `name`, `slug` (unique par compte), `description`,
  `status` (idée, en cours, en pause, livré), `is_public` (faux par défaut),
  `archived_at`. L'avancement est calculé (tâches terminées / tâches du projet),
  jamais stocké.
- `project_tasks` : structure des `tasks` (titre, description, statut, statut
  personnalisé, priorité, échéance, récurrence, intervalle, archivage) plus
  `project_id` et `kind` (`TASK`, `BUG`, `IMPROVEMENT`). Commentaires et historique
  réutilisent le même fonctionnement que les tâches clients.
- `checklist_items` : `id`, rattaché à une tâche client **ou** projet (une seule des
  deux clés étrangères renseignée, contrainte CHECK), `label`, `done`, `position`.

## 2. API

- Privée (connexion requise, filtrée par `owner_id`) : CRUD des projets, des tâches
  de projet et des éléments de checklist.
- Publique, lecture seule, sans cookie :
  - `GET /api/public/projects` : galerie des projets publics.
  - `GET /api/public/projects/{slug}` : détail de la vitrine.
- Les routes publiques utilisent des **schémas de réponse dédiés** qui ne contiennent
  que les champs de la vitrine, jamais les schémas privés. `owner_id` n'en sort pas.
- Un projet privé, archivé ou inexistant répond **404** (pas 403).
- Limitation de débit sur les routes publiques.

## 3. Récurrence et checklist

- Terminer une tâche récurrente crée l'occurrence suivante (code de `recurrence.py`
  partagé entre tâches clients et tâches de projet) avec la **même checklist, cases
  décochées**. L'occurrence terminée garde ses cases : historique des vérifications.
- Progression « 3/5 » dans les listes. Pas de clôture automatique : quand tout est
  coché, l'interface propose « Terminer ? ».
- Chaque case cochée ou décochée est tracée dans l'historique de la tâche.

## 4. Interface

- **Publique** : `/projets` (cartes : nom, statut, barre d'avancement, description
  courte) et `/projets/:slug` (vitrine). Lien « Se connecter » discret.
- **Barre latérale** : section « Projets » à côté des clients.
- **Page projet privée** : en-tête (statut, avancement, interrupteur public/privé),
  onglets Tâches, Bugs, Améliorations, Tableau, Activité ; filtre par type ;
  création rapide d'un bug ou d'un retour avec type présélectionné.
- **Accueil privé** : léger, centré sur le quotidien : relances du jour, tâches à
  faire, projets actifs avec avancement, bugs ouverts.
- Le design system actuel est conservé (mode sombre, densité, raccourcis, palette
  de commandes) ; soin particulier sur cartes, espacements et barres d'avancement.

## 5. Tests et sécurité

- Backend : tests d'isolation par `owner_id` pour projets et tâches de projet ;
  **tests anti-fuite** sur les routes publiques (aucune donnée client, aucune
  tâche non terminée, aucun commentaire, aucun `owner_id`) ; test de la
  réinitialisation de checklist à la récurrence ; test des migrations.
- Frontend : tests des stores, du routeur (routes publiques accessibles sans
  connexion, le reste protégé) et des composants de checklist.

## 6. Livraison en 4 PR

1. **Projets** : tables, API privée, pages, barre latérale, tâches typées.
2. **Vitrine publique** : routes publiques, galerie, page publique, tests anti-fuite.
3. **Checklists** : cases à cocher, réinitialisation à la récurrence, historique.
4. **Accueil et finitions visuelles**.

## Hors périmètre

Commentaires publics, projet partagé entre plusieurs utilisateurs, import de
tickets GitHub.
