# syntax=docker/dockerfile:1
# Cibles : `dev` (serveur Vite, docker-compose.yml)
#          `prod` (fichiers statiques servis par nginx, docker-compose.prod.yml)

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ─── Développement ──────────────────────────────────────────────────────────
FROM deps AS dev
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# ─── Build ──────────────────────────────────────────────────────────────────
FROM deps AS build
COPY . .
RUN npm run build

# ─── Production ─────────────────────────────────────────────────────────────
FROM nginx:1.29-alpine AS prod
# Modèle traité par l'image nginx au démarrage (variable BACKEND_URL)
ENV BACKEND_URL=backend:8000
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY nginx-security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://127.0.0.1/healthz || exit 1
