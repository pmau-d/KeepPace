# KeepPace

[![CI](https://github.com/pmau-d/KeepPace/actions/workflows/ci.yml/badge.svg)](https://github.com/pmau-d/KeepPace/actions/workflows/ci.yml)
[![Licence : MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
![Vue 3](https://img.shields.io/badge/vue-3.5-42b883?logo=vuedotjs&logoColor=white)
![PostgreSQL 15](https://img.shields.io/badge/postgresql-15-4169E1?logo=postgresql&logoColor=white)

**Le tableau de bord des consultants qui relancent au bon moment.**

KeepPace suit vos tâches client par client et tient compte de la présence de vos
interlocuteurs : inutile de relancer quelqu'un en congés, mais il faut le joindre
avant son départ et dès son retour. Chaque modification est tracée dans un
historique qui n'est jamais effacé.

![Liste des tâches, regroupées par échéance](docs/screenshots/taches.jpg)

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/relances.jpg" alt="Vue « À relancer aujourd'hui »" /></td>
    <td width="50%"><img src="docs/screenshots/detail-tache.jpg" alt="Panneau de détail d'une tâche" /></td>
  </tr>
  <tr>
    <td align="center"><em>À relancer aujourd'hui, par ordre d'urgence</em></td>
    <td align="center"><em>Détail d'une tâche : édition, commentaires, historique</em></td>
  </tr>
</table>

> Les captures utilisent les données de démonstration fournies avec le projet :
> toutes les entreprises et personnes sont fictives.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Démarrage rapide](#démarrage-rapide)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Développement](#développement)
- [Mise en production](#mise-en-production)
- [Règles métier](#règles-métier)
- [Contribuer](#contribuer) · [Sécurité](#sécurité) · [Licence](#licence)

## Fonctionnalités

- **Tâches par client** : statut (à faire, en cours, en attente client, terminé),
  priorité, échéance, statut personnalisé libre (« en attente du fournisseur »…),
  regroupement par jour avec les retards en tête.
- **Présence des clients** : période d'absence (du… au…) et statut calculé
  automatiquement : présent, bientôt absent, absent, bientôt de retour, rentré
  récemment.
- **À relancer aujourd'hui** : les tâches à traiter maintenant avec leur motif
  (échéance dépassée, échéance du jour, client qui part, client qui rentre,
  attente sans nouvelle), sans les clients injoignables.
- **Historique complet** : chaque changement est journalisé avec des libellés
  lisibles ; supprimer archive (réversible, avec « Annuler ») au lieu d'effacer.
- **Recherche plein texte** dans les titres, descriptions et commentaires ;
  filtres par statut, présence et client ; liste paginée.
- **Export CSV** des tâches filtrées, prêt pour Excel (séparateur `;`, UTF-8).
- **Comptes utilisateurs** : chaque compte ne voit que ses propres données.
- **Confort** : une URL par tâche, mode sombre, navigation au clavier.

<details>
<summary>Aperçu en mode sombre</summary>

![Liste des tâches en mode sombre](docs/screenshots/mode-sombre.jpg)

</details>

## Démarrage rapide

Prérequis : [Docker](https://docs.docker.com/get-docker/) avec Docker Compose v2.

```bash
git clone https://github.com/pmau-d/KeepPace.git
cd KeepPace
cp .env.example .env                                  # puis ajuster les valeurs
docker compose up --build
```

| Service                  | URL                          |
| ------------------------ | ---------------------------- |
| Application              | http://localhost:3000        |
| API                      | http://localhost:8000        |
| Documentation de l'API   | http://localhost:8000/docs   |

Créez un compte depuis l'écran de connexion, ou chargez des données de
démonstration fictives :

```bash
docker compose exec backend python -m scripts.seed_demo
# → compte demo@example.com, mot de passe affiché par la commande
```

## Architecture

```mermaid
flowchart LR
    navigateur["Navigateur<br/>Vue 3 · Pinia · Vue Router"]
    subgraph docker["Docker Compose"]
        nginx["nginx<br/>fichiers statiques + proxy /api"]
        api["API FastAPI<br/>SQLAlchemy · Alembic"]
        db[("PostgreSQL 15")]
    end
    navigateur -- "HTTPS (cookie de session httpOnly)" --> nginx
    nginx -- "/api/*" --> api
    api --> db
```

| Couche      | Technologies                                                        |
| ----------- | ------------------------------------------------------------------- |
| Frontend    | Vue 3.5, Vite 8, Pinia, Vue Router, Tailwind CSS 4, Axios           |
| Backend     | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2             |
| Sécurité    | Argon2 (mots de passe), JWT en cookie httpOnly, limitation des tentatives |
| Données     | PostgreSQL 15 (SQLite en mémoire pour les tests)                    |
| Qualité     | pytest, ruff, Vitest, ESLint, Prettier, GitHub Actions              |
| Déploiement | Images Docker multi-étapes, nginx, healthchecks                     |

<details>
<summary>Arborescence</summary>

```
KeepPace/
├── backend/
│   ├── app/
│   │   ├── main.py            # application FastAPI, sonde /health
│   │   ├── config.py          # configuration (variables d'environnement)
│   │   ├── models.py          # modèles SQLAlchemy
│   │   ├── schemas.py         # schémas Pydantic (entrées / sorties)
│   │   ├── security.py        # hachage, jetons, limitation des connexions
│   │   ├── presence.py        # règle de présence (expression SQL unique)
│   │   ├── archive.py         # archivage en cascade et restauration
│   │   ├── csv_export.py      # export CSV
│   │   └── routers/           # auth, companies, clients, tasks
│   ├── alembic/versions/      # migrations du schéma
│   ├── scripts/seed_demo.py   # données de démonstration fictives
│   └── tests/                 # pytest (API, auth, migrations)
├── frontend/
│   ├── src/
│   │   ├── views/             # connexion, tâches, relances, archives
│   │   ├── components/        # liste, cartes, panneau de tâche, modales
│   │   ├── stores/            # Pinia : auth, tâches, clients, toasts
│   │   ├── router/            # routes et garde d'authentification
│   │   └── utils/             # libellés, regroupement par jour
│   └── nginx.conf             # configuration de production
├── docker-compose.yml         # développement
└── docker-compose.prod.yml    # production
```

</details>

### Modèle de données

```mermaid
erDiagram
    users ||--o{ companies : possède
    companies ||--o{ clients : emploie
    clients ||--o{ tasks : concerne
    tasks ||--o{ task_comments : a
    tasks ||--o{ task_logs : "est tracée par"
```

Entreprises, clients et tâches ne sont jamais supprimés : ils portent une date
d'archivage (`archived_at`). Le journal (`task_logs`) conserve pour chaque
changement l'ancienne et la nouvelle valeur, ainsi que des libellés figés
(« Camille Durand · Atelier Boréal ») qui restent lisibles même après un
renommage.

## Configuration

Toute la configuration passe par des variables d'environnement, lues depuis
`.env` (voir [`.env.example`](.env.example)). Le fichier `.env` n'est jamais
versionné.

| Variable                      | Défaut                | Rôle                                                              |
| ----------------------------- | --------------------- | ----------------------------------------------------------------- |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | *obligatoires* | Identifiants de la base PostgreSQL                        |
| `SECRET_KEY`                  | clé de dev            | Signature des sessions. **Obligatoire en production** (32 caractères min.) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 jours)     | Durée de validité d'une session                                  |
| `ALLOW_REGISTRATION`          | `true`                | Passer à `false` pour fermer les inscriptions                     |
| `COOKIE_SECURE`               | `true` en production  | Cookie de session réservé à HTTPS                                 |
| `CORS_ORIGINS`                | *(vide)*              | Origines autorisées, séparées par des virgules (inutile via `/api`) |
| `TIMEZONE`                    | `Europe/Paris`        | Fuseau servant à calculer « aujourd'hui »                         |
| `HTTP_PORT`                   | `80`                  | Port publié par nginx (production)                                |
| `WEB_CONCURRENCY`             | `2`                   | Nombre de processus de l'API (production)                         |

Générer une clé secrète :

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Développement

### Avec Docker

`docker compose up --build` lance la base, l'API (rechargement à chaud) et le
serveur Vite. Les migrations sont appliquées au démarrage de l'API.

### Sans Docker

Backend (Python 3.12 et une base PostgreSQL accessible) :

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://utilisateur:motdepasse@localhost:5432/keeppace
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (Node.js 20.19 ou plus récent) :

```bash
cd frontend
npm ci
npm run dev        # http://localhost:3000, /api relayé vers localhost:8000
```

### Tests et qualité

| Commande (backend)                 | Rôle                                         |
| ---------------------------------- | -------------------------------------------- |
| `pytest`                           | Tests (SQLite en mémoire, aucune base requise) |
| `TEST_DATABASE_URL=… pytest`       | Mêmes tests sur un vrai PostgreSQL (mode CI) |
| `ruff check . && ruff format --check .` | Lint et formatage                       |

| Commande (frontend)                | Rôle                               |
| ---------------------------------- | ---------------------------------- |
| `npm test`                         | Tests Vitest                       |
| `npm run lint`                     | ESLint                             |
| `npm run format:check`             | Prettier                           |
| `npm run build`                    | Build de production                |

La CI GitHub Actions exécute tout cela à chaque pull request, avec les tests
backend sur PostgreSQL 15, et construit les images Docker de production.

### Migrations

```bash
cd backend
alembic revision -m "description du changement"   # puis écrire upgrade()/downgrade()
alembic upgrade head
```

Un test vérifie que les migrations produisent exactement le schéma des modèles :
une migration oubliée fait échouer la CI.

## Mise en production

```bash
cp .env.example .env    # renseigner de vraies valeurs, dont SECRET_KEY
docker compose -f docker-compose.prod.yml up -d --build
```

- Seul nginx est exposé ; il sert l'application et relaie `/api` vers l'API
  (même origine, donc pas de CORS à ouvrir).
- Placez un terminateur TLS (Caddy, Traefik, nginx…) devant le port publié : le
  cookie de session est `Secure` en production. Pour un essai local en HTTP
  simple, définissez `COOKIE_SECURE=false`.
- L'API refuse de démarrer en production avec la clé secrète par défaut ; la
  documentation interactive y est désactivée.
- Une fois vos comptes créés, fermez les inscriptions avec
  `ALLOW_REGISTRATION=false`.
- Sauvegardes : le volume `postgres_data` contient toutes les données, par
  exemple `docker compose -f docker-compose.prod.yml exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > sauvegarde.sql`.

### Mise à jour depuis une version sans comptes

Les migrations reprennent une base existante sans perte. Les données créées
avant l'ajout des comptes sont rattachées automatiquement au **premier compte
inscrit**. Conservez les identifiants PostgreSQL d'origine dans `.env` :
PostgreSQL ne les relit pas sur un volume déjà initialisé.

## Règles métier

<details>
<summary>Statut de présence d'un client</summary>

| Statut               | Condition                                                       |
| -------------------- | --------------------------------------------------------------- |
| 🟢 Présent           | Aucune absence, absence dans plus de 3 jours, ou retour il y a plus de 5 jours |
| 🟠 Bientôt absent    | L'absence commence dans les 3 prochains jours                   |
| 🔴 Absent            | Absence en cours, retour dans plus de 3 jours ou non daté       |
| 🟡 Bientôt de retour | Absence en cours, retour dans 0 à 3 jours                       |
| 🔵 Rentré récemment  | Retour dans les 5 derniers jours                                |

Une date de début vide signifie que l'absence a déjà commencé. La règle n'existe
qu'une fois, sous forme d'expression SQL (`backend/app/presence.py`), utilisée à
la fois pour filtrer et pour afficher le statut.

</details>

<details>
<summary>Motifs de « À relancer aujourd'hui »</summary>

Tâches ouvertes, dont le client n'est ni absent ni sur le point de rentrer, par
ordre d'urgence :

1. échéance dépassée ;
2. échéance aujourd'hui ;
3. le client part dans les 3 jours ;
4. le client est rentré depuis moins de 5 jours ;
5. tâche « en attente client » sans mise à jour depuis 3 jours.

</details>

## Contribuer

Les contributions sont les bienvenues : lisez [CONTRIBUTING.md](CONTRIBUTING.md)
(installation, conventions de commit, vérifications avant une pull request).
L'historique des versions est tenu dans [CHANGELOG.md](CHANGELOG.md).

## Sécurité

Pour signaler une vulnérabilité, ne créez pas d'issue publique : suivez
[SECURITY.md](SECURITY.md).

## Licence

Distribué sous licence [MIT](LICENSE).
