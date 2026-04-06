# Security Policy

## Secret management

Do not commit real `.env` files, API keys, SMTP credentials, Stripe secrets, database passwords or certificate files.

## Supported security posture

This project is prepared to:

- keep secrets outside the repository
- run with PostgreSQL as the default backend
- allow SQLite only as an explicit local fallback when `USE_SQLITE=True`
- restrict hosts and CSRF origins by environment variables
- enable secure cookies and HTTPS redirects in production
- send default security headers through middleware

## Responsible disclosure

If you detect a vulnerability in this codebase, report it privately to the project owner before publishing details.

## Deployment checklist

- `DEBUG=False`
- `SECRET_KEY` unique and private
- `ALLOWED_HOSTS` configured
- `CSRF_TRUSTED_ORIGINS` configured
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_SSL_REDIRECT=True`
- real SMTP credentials stored only in environment variables
- media storage reviewed before public deployment
