# KeepPace 🚀

> Application web d'organisation personnelle pour consultants — gestion de tâches avec suivi de présence client et historisation complète.

## Stack

| Couche       | Technologie                         |
|--------------|-------------------------------------|
| Frontend     | Vue 3 + Vite + Tailwind CSS + Pinia |
| Backend      | FastAPI (Python 3.11)               |
| Base de données | PostgreSQL 15                    |
| Conteneurs   | Docker & Docker Compose             |

## Lancer le projet

Prérequis : **Docker** et **Docker Compose** installés.

```bash
# À la racine du projet
docker compose up --build
```

| Service  | URL                                     |
|----------|-----------------------------------------|
| Frontend | http://localhost:3000                   |
| API      | http://localhost:8000                   |
| Swagger  | http://localhost:8000/docs              |

## Fonctionnalités

- ✅ **Gestion des tâches** — TODO / En cours / Bloqué / Terminé
- ✅ **Moteur de présence client** — 🟢 Présent · 🔵 Rentré récemment · 🟡 Bientôt de retour · 🔴 Absent
- ✅ **Audit Log** — chaque modification génère une entrée d'historique immuable
- ✅ **Slide-over** — timeline verticale complète de chaque tâche
- ✅ **Création à la volée** — créer un client/entreprise sans quitter le formulaire de tâche
- ✅ **Mode sombre** natif
- ✅ **Filtres cumulatifs** — par statut, par client, recherche textuelle, toggle "tâches terminées"

## Architecture

```
KeepPace/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI app + lifespan
│       ├── config.py        # Settings (pydantic-settings)
│       ├── database.py      # SQLAlchemy engine + wait_for_db
│       ├── models.py        # ORM models (Company, Client, Task, TaskLog)
│       ├── schemas.py       # Pydantic schemas
│       └── routers/
│           ├── companies.py
│           ├── clients.py   # incl. calcul présence
│           └── tasks.py     # incl. audit logging automatique
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js       # proxy /api → backend:8000
    ├── tailwind.config.js
    └── src/
        ├── App.vue
        ├── api/index.js
        ├── stores/
        │   ├── clientStore.js
        │   └── taskStore.js
        └── components/
            ├── Sidebar.vue
            ├── TopBar.vue
            ├── TaskList.vue
            ├── TaskCard.vue
            ├── TaskSlideOver.vue
            ├── CreateTaskModal.vue
            ├── CreateClientModal.vue
            ├── StatusBadge.vue
            └── PriorityBadge.vue
```

## Modèle de données

```
companies  ──< clients ──< tasks ──< task_logs
```

Le statut de présence est **calculé dynamiquement** côté backend à chaque requête à partir du champ `absence_end_date`.

