# 🎩 Grupo Boccato — Sistema de Gestión Gastronómica

**Plataforma web completa para Boccato di Cardinale · Boutique Gourmet · Santiago de Chile**

`Django 6.0.3` · `PostgreSQL 18` · `Bootstrap 5.3` · `Python 3.11+`

---

## 📋 Tabla de Contenidos

1. [Descripción](#descripción)
2. [Instalación Rápida](#instalación-rápida)
3. [Instalación Manual](#instalación-manual)
4. [Crear el Instalador (.exe / .command / .sh)](#crear-el-instalador)
5. [Distribución por Plataforma](#distribución-por-plataforma)
6. [Configuración](#configuración)
7. [Usuarios y Roles](#usuarios-y-roles)
8. [Módulos del Sistema](#módulos)
9. [URLs del Sistema](#urls)
10. [Solución de Problemas](#problemas)

---

## 📖 Descripción

**Grupo Boccato** es un sistema gastronómico integral que incluye:

| Módulo | Descripción |
|---|---|
| 🛍️ Tienda Online | Catálogo, carrito, órdenes y pagos Stripe |
| 🍽️ Carta Digital | Almuerzo, cena, terraza, vinos, licores |
| 📱 Comandas | Pantalla táctil para garzones con layout de mesas |
| 💳 Caja | Cobros, métodos de pago y libro de auditoría |
| 🖼️ Galería | Fotos dinámicas de la Terraza & Bar |
| 📊 Panel Admin | Gestión completa con reportes y historial |

---

## 🚀 Instalación Rápida

### Requisitos previos
- Python 3.11+ → [python.org/downloads](https://python.org/downloads)
- PostgreSQL 14+ → [postgresql.org/download](https://postgresql.org/download)

### Windows
```powershell
# 1. Descargar y extraer GrupoBoccato_v1.5.0_Windows.zip
# 2. Abrir PowerShell en la carpeta extraída:
python install.py
# 3. Seguir las instrucciones en pantalla
# 4. Al finalizar: doble click en INICIAR_BOCCATO.bat
```

### macOS
```bash
# 1. Descargar y extraer GrupoBoccato_v1.5.0_macOS.tar.gz
tar -xzf GrupoBoccato_v1.5.0_macOS.tar.gz
cd GrupoBoccato_v1.5.0

# 2. Instalar prereqs (si no están):
brew install python@3.11 postgresql@16
brew services start postgresql@16

# 3. Instalar:
python3 install.py

# 4. Iniciar: doble click en INICIAR_BOCCATO.command
```

### Linux (Ubuntu/Debian)
```bash
# 1. Instalar prereqs:
sudo apt update && sudo apt install python3.11 python3-pip python3-venv postgresql

# 2. Extraer e instalar:
tar -xzf GrupoBoccato_v1.5.0_Linux.tar.gz
cd GrupoBoccato_v1.5.0
python3 install.py

# 3. Iniciar:
./iniciar_boccato.sh
```

### Instalación silenciosa (sin preguntas)
```bash
python install.py --silencioso
```

---

## 🔧 Instalación Manual

Si prefieres hacer cada paso a mano:

### 1. Clonar / extraer el proyecto
```bash
cd /ruta/donde/quieras/instalar
# El proyecto debe estar en esta carpeta
```

### 2. Crear entorno virtual
```bash
# Windows:
python -m venv venv
venv\Scripts\activate

# Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear base de datos PostgreSQL
```sql
-- Ejecutar en pgAdmin o psql como superusuario:
CREATE USER boccato_user WITH PASSWORD 'Boccato.2026*Gold';
CREATE DATABASE boccato_db WITH OWNER = boccato_user ENCODING = 'UTF8' TEMPLATE = template0;
GRANT ALL PRIVILEGES ON DATABASE boccato_db TO boccato_user;
```

### 5. Crear archivo .env
```bash
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env

# Editar .env con tus credenciales
```

### 6. Migraciones
```bash
python manage.py migrate
```

### 7. Superusuario
```bash
python manage.py createsuperuser
```

### 8. Iniciar servidor
```bash
python manage.py runserver 0.0.0.0:8001
```

---

## 📦 Crear el Instalador

### Estructura de archivos de instalación

```
Grupo_Boccato/
├── install.py      ← Instalador Python (multiplataforma)
├── build.py        ← Constructor de distribuciones
├── setup.iss       ← Script Inno Setup (instalador .exe Windows)
└── dist/           ← Distribuciones generadas
    ├── windows/    ← .exe o .zip
    ├── macos/      ← .tar.gz o .dmg
    └── linux/      ← .tar.gz o .deb
```

### Generar la distribución de tu plataforma

```bash
# Auto-detectar plataforma:
python build.py

# Específico:
python build.py --windows
python build.py --mac
python build.py --linux
python build.py --todos
```

### Windows — Crear el instalador .exe

**Opción A — Con Inno Setup (recomendado):**

1. Descargar e instalar **Inno Setup 6**:
   `https://jrsoftware.org/isinfo.php`

2. Abrir `setup.iss` en Inno Setup Compiler

3. Click en **Build → Compile** (o F9)

4. El `.exe` se genera en `dist/windows/GrupoBoccato_v1.5.0_Setup.exe`

**Opción B — ZIP portable (sin Inno Setup):**

```bash
python build.py --windows
# Genera: dist/windows/GrupoBoccato_v1.5.0_Windows.zip
```

### macOS — Crear el instalador .command

```bash
python build.py --mac
# Genera: dist/macos/GrupoBoccato_v1.5.0_macOS.tar.gz
# Si estás en Mac, también intenta crear un .dmg
```

El usuario final hace:
1. Extraer el `.tar.gz`
2. Doble click en `INICIAR_BOCCATO.command`

### Linux — Crear el paquete

```bash
python build.py --linux
# Genera: dist/linux/GrupoBoccato_v1.5.0_Linux.tar.gz
# También crea estructura .deb en dist/linux/

# Para compilar el .deb:
dpkg-deb --build dist/linux/grupo-boccato_deb/
```

### Para instalar como servicio en Linux (producción)

```bash
sudo cp boccato.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable boccato
sudo systemctl start boccato
sudo systemctl status boccato
```

---

## ⚙️ Distribución por Plataforma

| Plataforma | Archivo | Cómo instalar | Cómo iniciar |
|---|---|---|---|
| Windows | `*_Setup.exe` o `*_Windows.zip` | Doble click en .exe | `INICIAR_BOCCATO.bat` |
| macOS | `*_macOS.tar.gz` o `*.dmg` | Extraer + `python3 install.py` | `INICIAR_BOCCATO.command` |
| Linux | `*_Linux.tar.gz` o `*.deb` | Extraer + `python3 install.py` | `./iniciar_boccato.sh` |

### Pasos que hace el instalador automáticamente

```
1. Detecta Python 3.11+ y PostgreSQL
2. Crea el entorno virtual ./venv/
3. Instala todas las dependencias (requirements.txt)
4. Crea el usuario y base de datos PostgreSQL
5. Genera el archivo .env con SECRET_KEY única
6. Ejecuta las migraciones de Django
7. Crea el superusuario administrador
8. Recolecta archivos estáticos
9. Crea los scripts de inicio/parada nativos
10. Ofrece abrir el navegador automáticamente
```

---

## 🔐 Configuración (.env)

```env
SECRET_KEY=clave-generada-automáticamente
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=boccato_db
DB_USER=boccato_user
DB_PASSWORD=Boccato.2026*Gold
DB_HOST=127.0.0.1
DB_PORT=5432

STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

> El instalador genera este archivo automáticamente.

---

## 👥 Usuarios y Roles

| Rol | Acceso | Crear desde |
|---|---|---|
| Superusuario | Todo | `python manage.py createsuperuser` |
| Staff | Panel admin | Django Admin → Users |
| Tesorero | Panel tesorero + caja | Admin → Caja → PerfilCaja |
| Cajero | Dashboard caja | Admin → Caja → PerfilCaja |
| Garzón | Comandas | Admin → Comandas → PerfilGarzon |

---

## 📦 Módulos

| URL | Módulo |
|---|---|
| `/` | Tienda online |
| `/carta/` | Carta y menús |
| `/terraza/` | Galería terraza & bar |
| `/comandas/` | Sistema de comandas (garzones) |
| `/caja/` | Módulo de caja (cajero) |
| `/caja/tesorero/` | Panel tesorero |
| `/caja/tesorero/auditoria/` | Libro de auditoría |
| `/panel/` | Panel admin Boccato |
| `/admin/` | Django admin |

---

## 🌐 URLs del Sistema

Después de instalar, el sistema estará en:

- **Local:** `http://127.0.0.1:8001`
- **Red local (tablets, celulares):** `http://TU_IP_LOCAL:8001`

Para conocer tu IP local:
```bash
# Windows:
ipconfig

# Mac/Linux:
ifconfig | grep inet
```

---

## 🛠️ Solución de Problemas

### `python` no se reconoce
Reinstala Python marcando **"Add Python to PATH"**

### Error de conexión PostgreSQL
```bash
# Verificar que PostgreSQL corre:
# Windows:
services.msc → buscar "postgresql"

# Mac:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql
```

### Puerto 8001 ocupado
```bash
# Windows:
netstat -ano | findstr :8001
taskkill /PID <numero> /F

# Mac/Linux:
lsof -i :8001
kill -9 <PID>

# O usar otro puerto:
python manage.py runserver 0.0.0.0:8002
```

### Desinstalar
```bash
python install.py --desinstalar
```

---

## 📅 Versiones

| Versión | Descripción |
|---|---|
| v1.5.0 | Sistema de caja con auditoría inmutable + instalador multiplataforma |
| v1.4.0 | Sistema de comandas táctil para garzones |
| v1.3.0 | Carta y menús (almuerzo, cena, vinos, licores) |
| v1.2.0 | Terraza & Bar con galería dinámica |
| v1.1.0 | Panel admin personalizado + ofertas + campañas |
| v1.0.0 | Tienda online base |

---

*Boccato di Cardinale · Boutique Gourmet · Santiago de Chile · 2026  Arturo Soto Aliste - pulsso@gmail.com*