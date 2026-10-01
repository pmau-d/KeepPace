# Contribuer à KeepPace

🇫🇷 Français · [🇬🇧 English](CONTRIBUTING.en.md)

Merci de votre intérêt ! Ce guide explique comment proposer une modification.
En participant, vous acceptez de respecter le [code de conduite](CODE_OF_CONDUCT.md).

## Avant de commencer

- Pour un bug, ouvrez une [issue](../../issues/new/choose) avec les étapes pour le
  reproduire.
- Pour une nouvelle fonctionnalité, ouvrez d'abord une issue pour en discuter :
  cela évite de travailler sur quelque chose qui ne serait pas retenu.
- Une faille de sécurité ne se signale **pas** dans une issue publique : voir
  [SECURITY.md](SECURITY.md).

## Installer l'environnement

Le plus simple est Docker (voir le [README](README.md#démarrage-rapide)) :

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend python -m scripts.seed_demo   # données fictives
```

Pour travailler sans Docker, suivez la section
[Développement](README.md#développement) du README.

## Proposer une modification

1. Créez une branche depuis `main` : `feat/…`, `fix/…`, `docs/…`, `refactor/…`,
   `test/…` ou `chore/…`, en minuscules avec des tirets
   (ex. `fix/filtre-presence`).
2. Faites des commits atomiques au format
   [Conventional Commits](https://www.conventionalcommits.org/fr/), en français :

   ```
   type(portée): description courte à l'impératif ou au nominal

   Corps qui explique le pourquoi du changement (le quoi se lit dans le diff).
   ```

   Types usuels : `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.
3. Vérifiez que tout est au vert en local :

   ```bash
   # Backend
   cd backend && ruff check . && ruff format --check . && pytest

   # Frontend
   cd frontend && npm run lint && npm run format:check && npm test && npm run build
   ```

4. Ouvrez une pull request vers `main` en remplissant le modèle (contexte,
   changements, tests, risques).

## Conventions

- **Backend** : code formaté par `ruff format`, typage des signatures, une
  migration Alembic pour tout changement de schéma (un test vérifie qu'aucune
  n'a été oubliée), des tests pytest pour chaque comportement de l'API.
- **Frontend** : TypeScript strict (`<script setup lang="ts">`, props et événements
  typés, types de l'API dans `src/types/api.ts`), logique métier dans les
  stores Pinia ou les fonctions de `src/utils/`, retours visibles pour
  l'utilisateur (toasts) plutôt qu'erreurs silencieuses.
- **Données** : n'utilisez que des données fictives dans les tests, les captures
  et les exemples (domaine `example.com`). Ne commitez jamais de secret ni de
  fichier `.env`.
- **Langue** : interface, messages d'erreur, commits et documentation en
  français. La documentation a une version anglaise (`*.en.md`), tenue à jour
  en même temps.

## Revue

Une pull request est fusionnée quand la CI est verte et qu'une relecture l'a
approuvée. Les fusions se font en « squash and merge » par défaut.
