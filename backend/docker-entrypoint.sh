#!/bin/sh
# Applique les migrations puis lance l'API (image de production).
set -e

alembic upgrade head

# Instance de démonstration : compte et données fictives créés une seule fois.
if [ "${DEMO_MODE:-false}" = "true" ]; then
    python -m scripts.seed_demo || true
fi

# --proxy-headers : l'adresse IP réelle du client (limitation des tentatives
# de connexion) vient de nginx. Le backend n'est joignable que par nginx
# sur le réseau interne Docker, d'où l'autorisation de tous les relais.
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers "${WEB_CONCURRENCY:-2}" \
    --proxy-headers \
    --forwarded-allow-ips "*" \
    --no-server-header
