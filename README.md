## 🚀 Guía de despliegue del back-end (Render + PostgreSQL)

El back-end es una API hecha con **FastAPI** y **SQLModel**. En local usa SQLite y en la nube usa PostgreSQL, y se elige solo según la variable `DATABASE_URL`.

**API en línea:** https://analizador-cvs.onrender.com  
**Documentación interactiva:** https://analizador-cvs.onrender.com/docs

> El plan gratuito de Render duerme el servicio tras unos 15 minutos sin uso, así que la primera petición puede tardar cerca de un minuto en responder.

### Rutas principales

| Método | Ruta | Descripción | Requiere login |
|---|---|---|:---:|
| POST | `/auth/register` | Crea un usuario | No |
| POST | `/auth/login` | Inicia sesión y devuelve un token JWT | No |
| GET | `/auth/me` | Datos del usuario autenticado | Sí |
| POST | `/analyses` | Sube un CV (PDF) y una vacante y devuelve el análisis | Sí |
| GET | `/analyses` | Historial de análisis del usuario | Sí |
| GET | `/analyses/{id}` | Detalle de un análisis | Sí |

Las rutas protegidas necesitan el encabezado `Authorization: Bearer <token>`.

### Ejecutar el back-end en tu computadora

**Requisitos:** Python 3.12 o superior y Git.

```bash
# 1. Clonar el repositorio
git clone https://github.com/luistunas7874-droid/analizador-cvs.git
cd analizador-cvs/backend

# 2. Crear y activar el entorno virtual (Windows)
python -m venv venv
venv\Scripts\activate

# 3. Instalar las dependencias
pip install -r requirements.txt
```

4. Crear un archivo `.env` dentro de `backend` con una clave secreta:

```
SECRET_KEY=pon-aqui-un-texto-largo-y-aleatorio
```

Para generar una clave segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

5. Arrancar el servidor:

```bash
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000/docs para probar la API. Se crea el archivo `analizador.db` (SQLite) automáticamente.

### Desplegar en Render

**1. Crear la base de datos PostgreSQL**

1. Crea una cuenta en [render.com](https://render.com) con tu cuenta de GitHub.
2. En el panel, pulsa **New** → **Postgres**.
3. Ponle el nombre `analizador-db`, elige una región (por ejemplo Ohio) y el plan **Free**.
4. Pulsa **Create Database** y espera a que el estado sea **Available**.
5. Copia la **Internal Database URL** (la vas a necesitar en el paso 3).

> Las bases gratuitas de Render caducan 30 días después de crearse.

**2. Crear el servicio web**

1. Pulsa **New** → **Web Service** y conecta el repositorio `analizador-cvs`.
2. Configura estos campos:

| Campo | Valor |
|---|---|
| Name | `analizador-cvs` |
| Region | La **misma** que la base de datos |
| Branch | `main` |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

**3. Variables de entorno**

| Key | Value |
|---|---|
| `DATABASE_URL` | La Internal Database URL de la base de datos |
| `SECRET_KEY` | Una clave secreta larga y aleatoria (puede usarse el botón **Generate**) |

**4. Desplegar**

Pulsa **Create Web Service** (o **Deploy Web Service**). Cuando el log diga `Your service is live`, abre la URL que da Render seguida de `/docs` para comprobar que funciona.

Cada vez que se una un cambio a la rama `main`, Render vuelve a desplegar automáticamente.

### Estructura del back-end

```
backend/
├── app/
│   ├── main.py       # Aplicación y rutas de autenticación
│   ├── analisis.py   # Rutas de análisis e historial
│   ├── ia.py         # Función que llama a la IA
│   ├── auth.py       # Contraseñas cifradas y tokens JWT
│   ├── database.py   # Conexión a la base de datos
│   └── models.py     # Tablas y formatos de la API
└── requirements.txt
```