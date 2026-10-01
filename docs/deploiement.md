# Déployer KeepPace

Deux façons de mettre KeepPace en ligne :

- **sur votre serveur**, avec `docker-compose.prod.yml` (voir le
  [README](../README.md#mise-en-production)) : c'est la solution pour de vraies
  données ;
- **en démo publique** sur [Render](https://render.com), avec le blueprint
  [`render.yaml`](../render.yaml) décrit ci-dessous.

## Démo publique sur Render

[![Déployer sur Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/pmau-d/KeepPace)

Le blueprint crée trois ressources :

| Ressource      | Rôle                                                                 |
| -------------- | -------------------------------------------------------------------- |
| `keeppace-db`  | Base PostgreSQL                                                      |
| `keeppace-api` | API (image `backend/Dockerfile`) : migrations au démarrage, `/health` |
| `keeppace`     | Frontend (image `frontend/Dockerfile`) : nginx sert l'application et relaie `/api` vers l'API |

Le mode démo est activé (`DEMO_MODE=true`) : au premier démarrage, l'API crée
le compte **demo@example.com** (mot de passe `demo-keeppace-2026`, modifiable
avec `DEMO_PASSWORD`) rempli de données fictives. Les inscriptions sont
fermées (`ALLOW_REGISTRATION=false`) et `SECRET_KEY` est générée par Render.

### Étapes

1. Créez un compte Render et cliquez sur le bouton ci-dessus (ou **New →
   Blueprint**, puis choisissez ce dépôt ou votre fork).
2. Validez les trois ressources proposées : Render construit les deux images
   et crée la base.
3. Ouvrez l'URL du service `keeppace` et connectez-vous avec le compte de
   démonstration.

### À savoir

- **Offre gratuite** : les services se mettent en veille après une période
  d'inactivité (premier chargement lent) et la base gratuite a une durée de vie
  limitée. Passez à une offre payante pour une démo permanente.
- **Données de démonstration uniquement** : `DEMO_MODE` publie un compte dont
  le mot de passe est connu. Ne l'activez jamais pour de vraies données.
- **Réinitialiser la démo** : supprimez puis recréez la base `keeppace-db` ;
  le compte de démonstration est recréé au redémarrage de l'API.
- **Récap par email** : désactivé ; il demande un serveur SMTP (`DIGEST_ENABLED`,
  `SMTP_*`, `APP_URL`, voir le README).

## Autres hébergeurs

Les deux images sont autonomes ; il suffit de fournir :

| Image            | Variables                                                      |
| ---------------- | -------------------------------------------------------------- |
| API (`backend/`) | `ENVIRONMENT=production`, `DATABASE_URL`, `SECRET_KEY` (32 caractères min.) ; port 8000 |
| Frontend (`frontend/`) | `BACKEND_URL` : hôte et port de l'API vus depuis le frontend (ex. `api.internal:8000`) ; port 80 |

L'URL de base PostgreSQL peut être au format `postgres://`, `postgresql://` ou
`postgresql+psycopg://`. Placez un terminateur HTTPS devant le frontend : le
cookie de session est `Secure` en production.
