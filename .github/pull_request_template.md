## Contexte / Context

<!-- Pourquoi ce changement ? Lien vers l'issue : « Corrige #123 »
     Why this change? Link to the issue: "Fixes #123" -->

## Changements / Changes

<!-- Ce qui change, en quelques points · What changes, in a few points -->

-

## Tests

<!-- Comment c'est vérifié, avec les résultats réels · How it was checked, with actual results -->

- [ ] Backend : `ruff check . && ruff format --check . && pytest`
- [ ] Frontend : `npm run lint && npm run format:check && npm test && npm run build`
- [ ] Vérifié à la main dans l'application (préciser le parcours) · Checked by hand in the app (describe the flow)

## Risques / points d'attention · Risks / points of attention

<!-- Migration de base, données existantes, comportement modifié, déploiement…
     Database migration, existing data, changed behaviour, deployment… -->

- [ ] Aucune donnée réelle ni aucun secret dans le diff (données fictives uniquement) · No real data and no secret in the diff (fictitious data only)
- [ ] Documentation mise à jour en français et en anglais si nécessaire · Documentation updated in French and English if needed
