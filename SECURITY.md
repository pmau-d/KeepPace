# Politique de sécurité

🇫🇷 Français · [🇬🇧 English](SECURITY.en.md)

## Versions prises en charge

Seule la dernière version publiée (branche `main`) reçoit des correctifs de
sécurité.

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique.** Utilisez le signalement privé de GitHub :
onglet **Security** du dépôt → **Report a vulnerability**
([documentation](https://docs.github.com/fr/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)).

Merci d'indiquer :

- la version ou le commit concerné ;
- une description de la faille et de son impact ;
- les étapes pour la reproduire, dans un environnement de test avec des données
  fictives.

Vous recevrez un accusé de réception dans les meilleurs délais. Une fois le
correctif publié, la vulnérabilité pourra être rendue publique, avec votre
accord, en vous créditant.

## Mesures en place

- Mots de passe hachés avec Argon2 ; session en JWT signé dans un cookie
  `httpOnly`, `SameSite=Lax` et `Secure` en production.
- Limitation des échecs de connexion par adresse IP et par email.
- Cloisonnement strict des données par compte (une ressource d'un autre compte
  répond 404).
- Refus de démarrer en production avec la clé secrète par défaut ; CORS fermé
  par défaut ; documentation interactive de l'API désactivée en production.
- En-têtes de sécurité servis par nginx (CSP, `X-Frame-Options`,
  `X-Content-Type-Options`, `Referrer-Policy`) ; conteneur d'API exécuté sans
  privilèges root.
- Neutralisation des formules dans l'export CSV.
- Dépendances surveillées par Dependabot.

## Limites connues

- La limitation des tentatives de connexion est gardée en mémoire, par
  processus : derrière plusieurs processus ou serveurs, prévoir un stockage
  partagé (Redis) ou une limitation au niveau du proxy.
- HTTPS n'est pas fourni par le projet : placez un terminateur TLS devant nginx.
