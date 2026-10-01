# Security policy

[🇫🇷 Français](SECURITY.md) · 🇬🇧 English

## Supported versions

Only the latest released version (`main` branch) receives security fixes.

## Reporting a vulnerability

**Do not open a public issue.** Use GitHub private reporting: the repository's
**Security** tab → **Report a vulnerability**
([documentation](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)).

Please include:

- the affected version or commit;
- a description of the vulnerability and its impact;
- the steps to reproduce it, in a test environment with fictitious data.

You will receive an acknowledgement as soon as possible. Once the fix is
released, the vulnerability may be made public, with your consent, crediting
you.

## Measures in place

- Passwords hashed with Argon2; session as a signed JWT in an `httpOnly`,
  `SameSite=Lax` cookie, `Secure` in production.
- Failed logins rate-limited per IP address and per e-mail.
- Strict data isolation per account (a resource of another account returns
  404).
- Refuses to start in production with the default secret key; CORS closed by
  default; interactive API documentation disabled in production.
- Security headers served by nginx (CSP, `X-Frame-Options`,
  `X-Content-Type-Options`, `Referrer-Policy`); API container running without
  root privileges.
- Formula neutralisation in the CSV export.
- Dependencies monitored by Dependabot.

## Known limitations

- Login attempt limiting is kept in memory, per process: behind several
  processes or servers, use shared storage (Redis) or rate limiting at the
  proxy level.
- HTTPS is not provided by the project: put a TLS terminator in front of nginx.
