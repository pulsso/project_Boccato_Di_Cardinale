# Grupo Boccato

Sistema web gastronomico construido con Django para catalogo, carrito, pedidos, pagos por transferencia, caja y seguimiento de despacho.

## Autor y derechos

- Autor del proyecto: `AS_Royal`
- Copyright: `Copyright (c) AS_Royal. Todos los derechos reservados.`
- Este repositorio se publica con fines de portafolio y operacion del proyecto. No se autoriza reutilizacion comercial, redistribucion o copia integral sin permiso expreso de `AS_Royal`.

## Stack

- Python 3.13 recomendado en Windows
- Django 5.2
- PostgreSQL como backend principal
- SQLite solo como fallback explicito de desarrollo
- Bootstrap 5
- ReportLab para PDF de pedidos

## Backend real del proyecto

Este sistema opera sobre PostgreSQL. SQLite no es la base principal del proyecto y queda habilitada solo si se define manualmente:

```env
USE_SQLITE=True
```

Si no defines eso, Django intentara conectarse a PostgreSQL y exigira `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`.

## Instalacion recomendada en Windows

### 1. Problema original de `pip`

Si `pip` apunta a otro proyecto o a un entorno roto, evita usar `pip` directo y trabaja siempre con:

```powershell
python -m pip
```

### 2. Entorno virtual limpio

Ejecuta dentro de `C:\Users\NBK-MGONZALEZ\OneDrive\Escritorio\Grupo_Boccato`:

```powershell
Remove-Item -Recurse -Force .\venv
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

## Configuracion

Copia `.env.example` a `.env` y ajusta las credenciales reales.

### PostgreSQL por defecto

```env
DEBUG=True
USE_SQLITE=False
DB_NAME=grupo_boccato
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

### Produccion endurecida

```env
DEBUG=False
USE_SQLITE=False
ALLOWED_HOSTS=tu-dominio.cl,www.tu-dominio.cl
CSRF_TRUSTED_ORIGINS=https://tu-dominio.cl,https://www.tu-dominio.cl
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

## Seguridad aplicada

- Variables sensibles fuera del repositorio
- PostgreSQL como backend por defecto
- Validacion temprana de variables obligatorias de base de datos
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` por entorno
- Cookies HTTPOnly y configuracion segura en produccion
- `X-Frame-Options`, CSP, `Referrer-Policy` y `nosniff`
- `SECRET_KEY` obligatoria en produccion

## Documentos tributarios

Se agrego una pagina publica en:

```text
/contact/documentos-tributarios/
```

Incluye:

- Solicitud por email prellenada
- Canal de contacto configurable por `.env`
- Accesos oficiales del SII para factura electronica, boleta electronica y boleta de honorarios

## Publicar el proyecto en GitHub sin exponer secretos

```powershell
git status
git add .
git commit -m "chore: harden postgres config and docs"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

Antes de hacer push:

- Verifica que `.env` no aparezca en `git status`
- Revisa que `README.md` represente el backend real del sistema
- No subas respaldos, certificados, llaves ni bases locales
