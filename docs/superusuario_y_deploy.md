# Superusuario y despliegue

## 1. Crear un superusuario nuevo en Django

Desde la raiz del proyecto:

```powershell
python manage.py createsuperuser
```

Django te pedira:

- `Username`
- `Email address`
- `Password`
- `Password (again)`

Cuando termine, podras entrar en:

```text
/admin/
```

## 2. Recuperar la clave de un superusuario existente

Si olvidaste la clave, no se recupera en texto plano. Lo correcto es asignar una nueva.

### Opcion A: desde consola interactiva de Django

```powershell
python manage.py shell
```

Luego:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username="admin")
user.set_password("NuevaClaveSegura2026!")
user.is_staff = True
user.is_superuser = True
user.save()
exit()
```

### Opcion B: en una sola linea

```powershell
python manage.py shell -c "from django.contrib.auth import get_user_model; u = get_user_model().objects.get(username='admin'); u.set_password('NuevaClaveSegura2026!'); u.is_staff=True; u.is_superuser=True; u.save()"
```

### Opcion C: si no recuerdas el nombre del usuario administrador

```powershell
python manage.py shell -c "from django.contrib.auth import get_user_model; print(list(get_user_model().objects.filter(is_superuser=True).values_list('username', flat=True)))"
```

## 3. Crear un superusuario directamente en produccion

Una vez desplegado en Render:

1. Abre tu servicio web.
2. Entra a `Shell`.
3. Ejecuta:

```bash
python manage.py createsuperuser
```

Si solo quieres resetear una clave en produccion:

```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; u = get_user_model().objects.get(username='admin'); u.set_password('NuevaClaveSegura2026!'); u.save()"
```

## 4. Base de datos PostgreSQL

Si trabajas con PostgreSQL local, verifica primero que el servicio este levantado y que tu `.env` tenga:

```env
USE_SQLITE=False
DB_NAME=grupo_boccato
DB_USER=postgres
DB_PASSWORD=tu_clave
DB_HOST=127.0.0.1
DB_PORT=5432
```

Luego corre:

```powershell
python manage.py migrate
```

## 5. Publicar para que un cliente lo vea

Este repositorio quedo preparado para `Render`, que es mas adecuado que Vercel para este Django con PostgreSQL y archivos estaticos.

Archivos agregados:

- `render.yaml`
- `build.sh`
- `.python-version`

## 6. Paso a paso en Render

1. Sube estos cambios a GitHub.
2. En Render, entra a `Blueprints`.
3. Elige `New Blueprint Instance`.
4. Conecta tu repositorio de GitHub.
5. Render detectara `render.yaml` y creara un servicio web y una base PostgreSQL.
6. Confirma el deploy.
7. Espera a que termine el build.
8. Abre la URL `https://...onrender.com`.
9. Entra a `https://...onrender.com/admin/`.
10. Crea el superusuario desde `Shell` si aun no existe.

Si usas el plan `free`, tomalo solo como demo o vista previa. La base PostgreSQL gratuita de Render expira a los 30 dias y no es adecuada para produccion estable.

## 7. Variables importantes

Si quieres configurarlas manualmente en vez de usar el blueprint:

- `DATABASE_URL`
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_SSL_REDIRECT=True`

## 8. Nota importante sobre imagenes subidas por admin

El proyecto ya puede quedar visible online, pero las imagenes que subas al panel de Django no deberian depender del disco temporal del servicio.

Para una version productiva estable, el siguiente paso recomendado es mover `media` a:

- Cloudinary
- Amazon S3
- un disco persistente
