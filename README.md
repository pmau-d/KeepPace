# KeepPace

[![CI](https://github.com/pmau-d/KeepPace/actions/workflows/ci.yml/badge.svg)](https://github.com/pmau-d/KeepPace/actions/workflows/ci.yml)
[![Licence : MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
![Python 3.14](https://img.shields.io/badge/python-3.14-3776AB?logo=python&logoColor=white)
![Vue 3](https://img.shields.io/badge/vue-3.5-42b883?logo=vuedotjs&logoColor=white)
![PostgreSQL 15](https://img.shields.io/badge/postgresql-15-4169E1?logo=postgresql&logoColor=white)

**Le tableau de bord des consultants qui relancent au bon moment.**

🇫🇷 Français · [🇬🇧 English](README.en.md)

KeepPace suit vos tâches client par client et tient compte de la présence de vos
interlocuteurs : inutile de relancer quelqu'un en congés, mais il faut le joindre
avant son départ et dès son retour. Chaque modification est tracée dans un
historique qui n'est jamais effacé.

![Démonstration : palette de commandes, report d'une relance, tableau et planning](docs/screenshots/demo.gif)

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/taches.jpg" alt="Liste des tâches regroupées par échéance" /></td>
    <td width="50%"><img src="docs/screenshots/relances.jpg" alt="Vue « À relancer aujourd'hui » avec le récap du jour" /></td>
  </tr>
  <tr>
    <td align="center"><em>Tâches par échéance, présence des clients expliquée</em></td>
    <td align="center"><em>À relancer aujourd'hui, avec le récap du jour</em></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/screenshots/planning.jpg" alt="Planning des absences et des échéances" /></td>
    <td width="50%"><img src="docs/screenshots/tableau.jpg" alt="Tableau Kanban par statut" /></td>
  </tr>
  <tr>
    <td align="center"><em>Planning : absences et échéances sur 4 semaines</em></td>
    <td align="center"><em>Tableau par statut, au glisser-déposer ou au clavier</em></td>
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

**Suivre**

- **Tâches par client** : statut (à faire, en cours, en attente client, terminé),
  priorité (drapeau), échéance, statut personnalisé libre (« en attente du
  fournisseur »…), regroupées par jour avec les retards en tête ; mode compact.
- **Tâches récurrentes** : chaque jour, semaine, mois ou année, avec un
  intervalle ; terminer une occurrence crée la suivante sans dériver.
- **Tableau** (Kanban) par statut, au glisser-déposer ou au clavier.
- **Historique complet** : chaque changement est journalisé avec des libellés
  lisibles ; supprimer archive (réversible, avec « Annuler ») au lieu d'effacer.

**Relancer au bon moment**

- **Présence des clients** : période d'absence (du… au…) et statut calculé
  automatiquement (présent, bientôt absent, absent, bientôt de retour, rentré
  récemment), expliqué sur chaque tâche (« Absent jusqu'au ven. 9 oct. »).
- **Import des absences** depuis un calendrier `.ics` (rapprochement par email
  ou par nom) ou en collant une **réponse automatique** : les dates sont
  reconnues (« du 3 au 17 octobre », « back on October 20th »…). Tout est
  analysé dans le navigateur.
- **Planning** : absences en barres et échéances sur 2 à 8 semaines.
- **À relancer aujourd'hui** : les tâches à traiter maintenant avec leur motif
  (échéance dépassée, échéance du jour, client qui part, client qui rentre,
  attente sans nouvelle), sans les clients injoignables.
- **« Relancer dans N jours »** en un clic (tracé dans l'historique) et
  **brouillon d'email** de relance prérempli.
- **Récap quotidien** dans l'application et, si vous l'activez, par email
  chaque matin.

**Travailler vite**

- **Palette de commandes** (Ctrl/⌘ K) : commandes, tâches et clients.
- **Raccourcis clavier** : `n` nouvelle tâche, `/` rechercher, `g` puis `t`,
  `b`, `r`, `p` ou `a` pour changer de vue, `?` pour l'aide.
- **Recherche plein texte** dans les titres, descriptions et commentaires ;
  filtres par statut, présence et client ; liste paginée.
- **Export CSV** des tâches filtrées, prêt pour Excel (séparateur `;`, UTF-8).
- **Comptes utilisateurs** : chaque compte ne voit que ses propres données.
- **Confort** : une URL par tâche, mode sombre, utilisable sur téléphone,
  composants accessibles au clavier et aux lecteurs d'écran.

<details>
<summary>Autres aperçus : détail d'une tâche, palette, mode sombre, mobile</summary>

| | |
| --- | --- |
| ![Panneau de détail d'une tâche](docs/screenshots/detail-tache.jpg) | ![Palette de commandes](docs/screenshots/palette.jpg) |
| ![Liste des tâches en mode sombre](docs/screenshots/mode-sombre.jpg) | <img src="docs/screenshots/mobile.jpg" alt="Liste des tâches sur téléphone" width="300" /> |

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
| Emails de développement (Mailpit) | http://localhost:8025 |

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
| Frontend    | Vue 3.5 + TypeScript (strict), Vite 8, Pinia, Vue Router, Tailwind CSS 4, Axios |
| Backend     | Python 3.14, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2             |
| Sécurité    | Argon2 (mots de passe), JWT en cookie httpOnly, limitation des tentatives |
| Données     | PostgreSQL 15 (SQLite en mémoire pour les tests)                    |
| Qualité     | pytest, ruff, vue-tsc, Vitest, ESLint, Prettier, GitHub Actions     |
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
│   │   ├── follow_up.py       # tâches à relancer aujourd'hui
│   │   ├── recurrence.py      # occurrence suivante des tâches récurrentes
│   │   ├── digest.py          # récap quotidien (contenu, email, envoi planifié)
│   │   └── routers/           # auth, companies, clients, tasks, digest
│   ├── alembic/versions/      # migrations du schéma
│   ├── scripts/seed_demo.py   # données de démonstration fictives
│   └── tests/                 # pytest (API, auth, migrations)
├── frontend/
│   ├── src/
│   │   ├── views/             # connexion, tâches, tableau, relances, planning, archives
│   │   ├── components/        # liste, cartes, panneau de tâche, palette, modales
│   │   ├── components/ui/     # menu déroulant, calendrier, info-bulle
│   │   ├── commands/          # commandes de la palette et des raccourcis
│   │   ├── stores/            # Pinia : auth, tâches, clients, toasts
│   │   ├── router/            # routes et garde d'authentification
│   │   ├── types/             # types TypeScript de l'API
│   │   └── utils/             # dates, libellés, planning, import ICS, messages d'absence
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
| `BACKEND_URL`                 | `backend:8000`        | Hôte et port de l'API vus par nginx (image frontend)              |
| `DEMO_MODE`                   | `false`               | Démo publique : crée le compte de démonstration au démarrage      |
| `DIGEST_ENABLED`              | `false`               | Autorise l'envoi du récap quotidien par email (chaque compte l'active) |
| `DIGEST_HOUR`                 | `8`                   | Heure d'envoi du récap (fuseau `TIMEZONE`)                        |
| `SMTP_HOST` / `SMTP_PORT`     | *(vide)* / `587`      | Serveur d'envoi ; en dev, Mailpit est déjà configuré              |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | *(vide)*          | Identifiants SMTP                                                 |
| `SMTP_FROM`                   | `KeepPace <noreply@example.com>` | Expéditeur des emails                                  |
| `SMTP_STARTTLS` / `SMTP_SSL`  | `true` / `false`      | Chiffrement de la connexion SMTP                                  |
| `APP_URL`                     | `http://localhost:3000` | Adresse publique, pour les liens des emails                     |

Générer une clé secrète :

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Développement

### Avec Docker

`docker compose up --build` lance la base, l'API (rechargement à chaud), le
serveur Vite et Mailpit. Les migrations sont appliquées au démarrage de l'API.
Pour essayer le récap par email, mettez `DIGEST_ENABLED=true` dans `.env` :
les messages arrivent dans Mailpit (http://localhost:8025), rien ne sort.

### Sans Docker

Backend (Python 3.14, 3.12 minimum, et une base PostgreSQL accessible) :

```bash
cd backend
python3.14 -m venv .venv && source .venv/bin/activate
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
| `npm run lint`                     | Vérification des types (vue-tsc) puis ESLint |
| `npm run type-check`               | Vérification des types seule       |
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

### Démo publique

Le blueprint [`render.yaml`](render.yaml) déploie une démo sur
[Render](https://render.com) (base, API, frontend, compte de démonstration
fictif, inscriptions fermées) ; il demande un compte Render. Étapes, limites et
autres hébergeurs : [docs/deploiement.md](docs/deploiement.md).

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
(installation, conventions de commit, vérifications avant une pull request) et le
[code de conduite](CODE_OF_CONDUCT.md).
L'historique des versions est tenu dans [CHANGELOG.md](CHANGELOG.md).

## Sécurité

Pour signaler une vulnérabilité, ne créez pas d'issue publique : suivez
[SECURITY.md](SECURITY.md).

## Licence

Distribué sous licence [MIT](LICENSE).
