# Contributing to KeepPace

[🇫🇷 Français](CONTRIBUTING.md) · 🇬🇧 English

Thank you for your interest! This guide explains how to propose a change.
By taking part, you agree to follow the [code of conduct](CODE_OF_CONDUCT.en.md).

## Before you start

- For a bug, open an [issue](../../issues/new/choose) with the steps to
  reproduce it.
- For a new feature, open an issue first to discuss it: this avoids working on
  something that would not be accepted.
- A security vulnerability must **not** be reported in a public issue: see
  [SECURITY.en.md](SECURITY.en.md).

Issues and pull requests can be written in English or French.

## Setting up the environment

The easiest way is Docker (see the [README](README.en.md#quick-start)):

```bash
cp .env.example .env
docker compose up --build
docker compose exec backend python -m scripts.seed_demo   # fictitious data
```

To work without Docker, follow the [Development](README.en.md#development)
section of the README.

## Proposing a change

1. Create a branch from `main`: `feat/…`, `fix/…`, `docs/…`, `refactor/…`,
   `test/…` or `chore/…`, lowercase with hyphens
   (e.g. `fix/presence-filter`).
2. Make atomic commits following
   [Conventional Commits](https://www.conventionalcommits.org/). Commit messages
   in the repository are written in French; English is accepted from external
   contributors:

   ```
   type(scope): short description

   Body explaining why the change is made (the what can be read in the diff).
   ```

   Usual types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.
3. Check that everything is green locally:

   ```bash
   # Backend
   cd backend && ruff check . && ruff format --check . && pytest

   # Frontend
   cd frontend && npm run lint && npm run format:check && npm test && npm run build
   ```

4. Open a pull request to `main` and fill in the template (context, changes,
   tests, risks).

## Conventions

- **Backend**: code formatted by `ruff format`, typed signatures, an Alembic
  migration for every schema change (a test checks that none was forgotten),
  pytest tests for every API behaviour.
- **Frontend**: strict TypeScript (`<script setup lang="ts">`, typed props and
  events, API types in `src/types/api.ts`), business logic in Pinia stores or
  in `src/utils/` functions, visible feedback for the user (toasts) rather than
  silent errors.
- **Data**: only use fictitious data in tests, screenshots and examples
  (`example.com` domain). Never commit a secret or a `.env` file.
- **Language**: interface, error messages and commits in French. Documentation
  in French, with an English version (`*.en.md`) kept in sync.

## Review

A pull request is merged when CI is green and a review has approved it. Merges
use "squash and merge" by default.
