# KeepPace

[![CI](https://github.com/pmau-d/KeepPace/actions/workflows/ci.yml/badge.svg)](https://github.com/pmau-d/KeepPace/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Vue 3](https://img.shields.io/badge/vue-3.5-42b883?logo=vuedotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-strict-3178C6?logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/fastapi-009688?logo=fastapi&logoColor=white)
![PostgreSQL 15](https://img.shields.io/badge/postgresql-15-4169E1?logo=postgresql&logoColor=white)

**The dashboard for consultants who follow up at the right time.**

[🇫🇷 Français](README.md) · 🇬🇧 English

KeepPace tracks your tasks client by client and takes your contacts' availability
into account: there is no point chasing someone on holiday, but you do want to
reach them before they leave and as soon as they are back. Every change is kept
in a history that is never erased.

> The interface is in French. This page describes it in English; screenshots use
> the bundled demo data, where every company and person is fictitious.

![Demo: command palette, postponing a follow-up, board and planning](docs/screenshots/demo.gif)

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/taches.jpg" alt="Task list grouped by due date" /></td>
    <td width="50%"><img src="docs/screenshots/relances.jpg" alt="“Follow up today” view with the daily digest" /></td>
  </tr>
  <tr>
    <td align="center"><em>Tasks by due date, with each client's availability explained</em></td>
    <td align="center"><em>Follow up today, with the daily digest</em></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/screenshots/planning.jpg" alt="Planning of absences and due dates" /></td>
    <td width="50%"><img src="docs/screenshots/tableau.jpg" alt="Kanban board by status" /></td>
  </tr>
  <tr>
    <td align="center"><em>Planning: absences and due dates over 4 weeks</em></td>
    <td align="center"><em>Board by status, drag and drop or keyboard</em></td>
  </tr>
</table>

## Contents

- [Features](#features)
- [Quick start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Development](#development)
- [Production](#production)
- [Business rules](#business-rules)
- [Contributing](#contributing) · [Security](#security) · [License](#license)

## Features

**Track**

- **Tasks per client**: status (to do, in progress, waiting for client, done),
  priority (flag), due date, free-form custom status (“waiting for the
  supplier”…), grouped by day with overdue tasks first; compact mode.
- **Recurring tasks**: every day, week, month or year, with an interval;
  completing one occurrence creates the next one without drifting.
- **Board** (Kanban) by status, with drag and drop or the keyboard.
- **Full history**: every change is logged with readable labels; deleting
  archives instead (reversible, with “Undo”).

**Follow up at the right time**

- **Client availability**: absence period (from… to…) and a computed status
  (present, leaving soon, absent, back soon, recently back), explained on each
  task (“Absent until Fri 9 Oct”).
- **Absence import** from an `.ics` calendar (matched by email or full name), or
  by pasting an **out-of-office reply**: the dates are recognised in French and
  English (“du 3 au 17 octobre”, “back on October 20th”…). Everything is parsed
  in the browser.
- **Planning**: absences as bars and due dates over 2 to 8 weeks.
- **Follow up today**: tasks to handle now with their reason (overdue, due
  today, client leaving, client back, waiting with no news), excluding clients
  who cannot be reached.
- **“Follow up in N days”** in one click (logged in the history) and a
  pre-filled **follow-up email draft**.
- **Daily digest** in the app and, if you opt in, by email every morning.

**Work fast**

- **Command palette** (Ctrl/⌘ K): commands, tasks and clients.
- **Keyboard shortcuts**: `n` new task, `/` search, `g` then `t`, `b`, `r`, `p`
  or `a` to switch views, `?` for help.
- **Full-text search** in titles, descriptions and comments; filters by status,
  availability and client; paginated list.
- **CSV export** of the filtered tasks, ready for Excel (`;` separator, UTF-8).
- **User accounts**: each account only sees its own data.
- **Comfort**: one URL per task, dark mode, works on phones, components usable
  with a keyboard and screen readers.

<details>
<summary>More screenshots: task details, palette, dark mode, mobile</summary>

| | |
| --- | --- |
| ![Task detail panel](docs/screenshots/detail-tache.jpg) | ![Command palette](docs/screenshots/palette.jpg) |
| ![Task list in dark mode](docs/screenshots/mode-sombre.jpg) | <img src="docs/screenshots/mobile.jpg" alt="Task list on a phone" width="300" /> |

</details>

## Quick start

Requirements: [Docker](https://docs.docker.com/get-docker/) with Docker Compose v2.

```bash
git clone https://github.com/pmau-d/KeepPace.git
cd KeepPace
cp .env.example .env                                  # then adjust the values
docker compose up --build
```

| Service                         | URL                          |
| ------------------------------- | ---------------------------- |
| Application                     | http://localhost:3000        |
| API                             | http://localhost:8000        |
| API documentation               | http://localhost:8000/docs   |
| Development emails (Mailpit)    | http://localhost:8025        |

Create an account from the login screen, or load fictitious demo data:

```bash
docker compose exec backend python -m scripts.seed_demo
# → account demo@example.com, password printed by the command
```

## Architecture

```mermaid
flowchart LR
    browser["Browser<br/>Vue 3 · Pinia · Vue Router"]
    subgraph docker["Docker Compose"]
        nginx["nginx<br/>static files + /api proxy"]
        api["FastAPI API<br/>SQLAlchemy · Alembic"]
        db[("PostgreSQL 15")]
    end
    browser -- "HTTPS (httpOnly session cookie)" --> nginx
    nginx -- "/api/*" --> api
    api --> db
```

| Layer      | Technologies                                                        |
| ---------- | ------------------------------------------------------------------- |
| Frontend   | Vue 3.5 + TypeScript (strict), Vite, Pinia, Vue Router, Tailwind CSS 4, Axios |
| Backend    | Python, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2                  |
| Security   | Argon2 (passwords), JWT in an httpOnly cookie, login rate limiting  |
| Data       | PostgreSQL 15 (in-memory SQLite for tests)                          |
| Quality    | pytest, ruff, vue-tsc, Vitest, ESLint, Prettier, GitHub Actions     |
| Deployment | Multi-stage Docker images, nginx, health checks                     |

### Data model

```mermaid
erDiagram
    users ||--o{ companies : owns
    companies ||--o{ clients : employs
    clients ||--o{ tasks : "is about"
    tasks ||--o{ task_comments : has
    tasks ||--o{ task_logs : "is tracked by"
```

Companies, clients and tasks are never deleted: they carry an archive date
(`archived_at`). The log (`task_logs`) keeps the old and new value of every
change, plus frozen labels (“Camille Durand · Atelier Boréal”) that stay
readable after a rename.

## Configuration

All configuration goes through environment variables, read from `.env` (see
[`.env.example`](.env.example)). The `.env` file is never committed.

| Variable                      | Default               | Purpose                                                           |
| ----------------------------- | --------------------- | ----------------------------------------------------------------- |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | *required* | PostgreSQL credentials                                    |
| `SECRET_KEY`                  | dev key               | Session signing key. **Required in production** (32+ characters)  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days)      | Session lifetime                                                  |
| `ALLOW_REGISTRATION`          | `true`                | Set to `false` to close sign-ups                                  |
| `COOKIE_SECURE`               | `true` in production  | Session cookie restricted to HTTPS                                |
| `CORS_ORIGINS`                | *(empty)*             | Allowed origins, comma-separated (not needed through `/api`)      |
| `TIMEZONE`                    | `Europe/Paris`        | Time zone used to compute “today”                                 |
| `HTTP_PORT`                   | `80`                  | Port published by nginx (production)                              |
| `WEB_CONCURRENCY`             | `2`                   | Number of API processes (production)                              |
| `DIGEST_ENABLED`              | `false`               | Allows the daily email digest (each account opts in)              |
| `DIGEST_HOUR`                 | `8`                   | Digest sending hour (in `TIMEZONE`)                               |
| `SMTP_HOST` / `SMTP_PORT`     | *(empty)* / `587`     | Mail server; Mailpit is preconfigured in development              |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | *(empty)*         | SMTP credentials                                                  |
| `SMTP_FROM`                   | `KeepPace <noreply@example.com>` | Sender address                                         |
| `SMTP_STARTTLS` / `SMTP_SSL`  | `true` / `false`      | SMTP connection encryption                                        |
| `APP_URL`                     | `http://localhost:3000` | Public address, used for links in emails                        |

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Development

### With Docker

`docker compose up --build` starts the database, the API (hot reload), the Vite
dev server and Mailpit. Migrations run when the API starts. To try the email
digest, set `DIGEST_ENABLED=true` in `.env`: messages land in Mailpit
(http://localhost:8025) and nothing leaves your machine.

### Without Docker

Backend (Python and a reachable PostgreSQL database):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/keeppace
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (Node.js 20.19 or later):

```bash
cd frontend
npm ci
npm run dev        # http://localhost:3000, /api proxied to localhost:8000
```

### Tests and quality

| Command (backend)                  | Purpose                                      |
| ---------------------------------- | -------------------------------------------- |
| `pytest`                           | Tests (in-memory SQLite, no database needed) |
| `TEST_DATABASE_URL=… pytest`       | Same tests against a real PostgreSQL (CI mode) |
| `ruff check . && ruff format --check .` | Lint and formatting                     |

| Command (frontend)                 | Purpose                            |
| ---------------------------------- | ---------------------------------- |
| `npm test`                         | Vitest tests                       |
| `npm run lint`                     | Type check (vue-tsc) then ESLint   |
| `npm run type-check`               | Type check only                    |
| `npm run format:check`             | Prettier                           |
| `npm run build`                    | Production build                   |

GitHub Actions runs all of this on every pull request, with the backend tests on
PostgreSQL 15, and builds the production Docker images.

### Migrations

```bash
cd backend
alembic revision -m "describe the change"   # then write upgrade()/downgrade()
alembic upgrade head
```

A test checks that the migrations produce exactly the models' schema: a
forgotten migration fails the CI.

## Production

```bash
cp .env.example .env    # fill in real values, including SECRET_KEY
docker compose -f docker-compose.prod.yml up -d --build
```

- Only nginx is exposed; it serves the app and proxies `/api` to the API (same
  origin, so no CORS to open).
- Put a TLS terminator (Caddy, Traefik, nginx…) in front of the published port:
  the session cookie is `Secure` in production. For a quick local HTTP test, set
  `COOKIE_SECURE=false`.
- The API refuses to start in production with the default secret key; the
  interactive documentation is disabled there.
- Once your accounts exist, close sign-ups with `ALLOW_REGISTRATION=false`.
- Backups: the `postgres_data` volume holds all the data, for example
  `docker compose -f docker-compose.prod.yml exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql`.

## Business rules

<details>
<summary>Client availability status</summary>

| Status            | Condition                                                         |
| ----------------- | ----------------------------------------------------------------- |
| 🟢 Present        | No absence, absence more than 3 days away, or back more than 5 days ago |
| 🟠 Leaving soon   | The absence starts within the next 3 days                         |
| 🔴 Absent         | Absence in progress, back in more than 3 days or no return date   |
| 🟡 Back soon      | Absence in progress, back within 0 to 3 days                      |
| 🔵 Recently back  | Back within the last 5 days                                       |

An empty start date means the absence has already started. The rule exists only
once, as a SQL expression (`backend/app/presence.py`), used both to filter and to
display the status.

</details>

<details>
<summary>Reasons in “Follow up today”</summary>

Open tasks whose client is neither absent nor about to return, by urgency:

1. overdue;
2. due today;
3. the client leaves within 3 days;
4. the client came back less than 5 days ago;
5. a “waiting for client” task with no update for 3 days.

</details>

## Contributing

Contributions are welcome: read [CONTRIBUTING.md](CONTRIBUTING.md) (setup,
commit conventions, checks before a pull request; in French, but issues and pull
requests in English are fine). Release notes are in [CHANGELOG.md](CHANGELOG.md).

## Security

To report a vulnerability, do not open a public issue: follow
[SECURITY.md](SECURITY.md).

## License

Released under the [MIT](LICENSE) license.
