# API CRUD de Ventas de Autos

## Programación IV - Universidad Tecnológica Nacional

---

## Descripción

API REST completa para la gestión de ventas de autos desarrollada con **FastAPI**, **SQLModel** y **PostgreSQL**. El sistema permite administrar un inventario de autos y registrar las ventas realizadas, implementando todas las operaciones CRUD y aplicando patrones de diseño profesionales.

---

## Características

- ✅ **CRUD Completo**: Operaciones Create, Read, Update, Delete para Autos y Ventas
- ✅ **Validaciones Robustas**: Validación de datos con Pydantic y reglas de negocio
- ✅ **Patrón Repository**: Implementación del patrón Repository para acceso a datos
- ✅ **Paginación**: Paginación en todos los endpoints de listado
- ✅ **Búsquedas Avanzadas**: Filtros por marca, modelo, precio, fecha, comprador
- ✅ **Relaciones**: Gestión de relaciones uno-a-muchos entre Autos y Ventas
- ✅ **Documentación Automática**: Documentación interactiva con Swagger UI y ReDoc
- ✅ **Manejo de Errores**: Manejo apropiado de errores HTTP (400, 404, 422)

---

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para construir APIs
- **SQLModel**: ORM basado en SQLAlchemy y Pydantic
- **PostgreSQL**: Base de datos relacional
- **Pydantic**: Validación de datos y serialización
- **Python 3.8+**: Lenguaje de programación

---

## Estructura del Proyecto

```
TrabajoFastAPI/
├── main.py              # Aplicación FastAPI principal
├── database.py          # Configuración de base de datos
├── models.py            # Modelos SQLModel
├── repository.py        # Patrón Repository para acceso a datos
├── autos.py            # Router de endpoints para autos
├── ventas.py           # Router de endpoints para ventas
├── requirements.txt     # Dependencias Python
└── README.md           # Documentación del proyecto
```

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.8 o superior**
   - Verificar versión: `python --version`
   - Descargar desde: https://www.python.org/downloads/

2. **PostgreSQL**
   - Windows: https://www.postgresql.org/download/windows/
   - Linux: `sudo apt-get install postgresql postgresql-contrib`
   - macOS: `brew install postgresql`

3. **pip** (gestor de paquetes de Python)

---

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd TrabajoFastAPI
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

1. Crear la base de datos:
```sql
CREATE DATABASE autos_db;
```

2. Configurar variables de entorno:

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL="postgresql://usuario:password@localhost:5432/autos_db"
$env:ENVIRONMENT="development"
```

**Windows (CMD):**
```cmd
set DATABASE_URL=postgresql://usuario:password@localhost:5432/autos_db
set ENVIRONMENT=development
```

**Linux/macOS:**
```bash
export DATABASE_URL="postgresql://usuario:password@localhost:5432/autos_db"
export ENVIRONMENT="development"
```

**O crear un archivo `.env`** (recomendado):
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/autos_db
ENVIRONMENT=development
```

> **Nota**: Reemplaza `usuario` y `password` con tus credenciales de PostgreSQL.

### 5. Inicializar la base de datos

La aplicación creará automáticamente las tablas al iniciar. También puedes ejecutar:

```bash
python database.py init
```

---

## Ejecución

### Modo Desarrollo

```bash
# Opción 1: Usando uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Ejecutando main.py
python main.py
```

### Verificar que la aplicación está corriendo

Abre tu navegador y visita:
- **API Principal**: http://localhost:8000
- **Documentación Swagger UI**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Endpoints de la API

### Autos (`/autos`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/autos` | Crear nuevo auto |
| GET | `/autos` | Listar autos con paginación |
| GET | `/autos/{auto_id}` | Obtener auto por ID |
| PUT | `/autos/{auto_id}` | Actualizar auto |
| DELETE | `/autos/{auto_id}` | Eliminar auto |
| GET | `/autos/chasis/{numero_chasis}` | Buscar por número de chasis |
| GET | `/autos/{auto_id}/with-ventas` | Auto con sus ventas |
| GET | `/autos/search/` | Búsqueda avanzada con filtros |

### Ventas (`/ventas`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/ventas` | Crear nueva venta |
| GET | `/ventas` | Listar ventas con paginación |
| GET | `/ventas/{venta_id}` | Obtener venta por ID |
| PUT | `/ventas/{venta_id}` | Actualizar venta |
| DELETE | `/ventas/{venta_id}` | Eliminar venta |
| GET | `/ventas/auto/{auto_id}` | Ventas de un auto específico |
| GET | `/ventas/comprador/{nombre}` | Ventas por nombre de comprador |
| GET | `/ventas/{venta_id}/with-auto` | Venta con información del auto |
| GET | `/ventas/search/` | Búsqueda avanzada con filtros |

---

## Ejemplos de Uso

### Crear un Auto

```bash
POST http://localhost:8000/autos
Content-Type: application/json

{
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2023,
    "numero_chasis": "TOY2023COR123456"
}
```

### Crear una Venta

```bash
POST http://localhost:8000/ventas
Content-Type: application/json

{
    "nombre_comprador": "Juan Pérez",
    "precio": 25000.00,
    "auto_id": 1,
    "fecha_venta": "2024-03-15T10:30:00"
}
```

### Obtener Auto con Ventas

```bash
GET http://localhost:8000/autos/1/with-ventas
```

### Buscar Autos por Marca

```bash
GET http://localhost:8000/autos/search/?marca=Toyota&skip=0&limit=10
```

### Buscar Ventas por Rango de Precios

```bash
GET http://localhost:8000/ventas/search/?precio_min=20000&precio_max=30000
```

---

## Validaciones Implementadas

### Auto
- ✅ Año entre 1900 y año actual
- ✅ Número de chasis único y alfanumérico
- ✅ Marca y modelo no vacíos

### Venta
- ✅ Precio mayor a 0
- ✅ Nombre del comprador no vacío
- ✅ Fecha de venta no futura
- ✅ Auto debe existir antes de crear la venta

---

## Estructura de Datos

### Auto
```json
{
    "id": 1,
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2023,
    "numero_chasis": "TOY2023COR123456"
}
```

### Venta
```json
{
    "id": 1,
    "nombre_comprador": "Juan Pérez",
    "precio": 25000.00,
    "auto_id": 1,
    "fecha_venta": "2024-03-15T10:30:00"
}
```

---

## Comandos Útiles

### Base de Datos

```bash
# Inicializar base de datos
python database.py init

# Probar conexión
python database.py test

# Ver información de configuración
python database.py info

# Reiniciar base de datos (⚠️ PELIGROSO - elimina todos los datos)
python database.py reset
```

### Verificar Conexión a PostgreSQL

```bash
psql -h localhost -p 5432 -U usuario -d autos_db
```

---

## Solución de Problemas

### Error de Conexión a Base de Datos

1. Verificar que PostgreSQL esté corriendo:
   ```bash
   # Windows
   services.msc (buscar PostgreSQL)
   
   # Linux
   sudo systemctl status postgresql
   
   # macOS
   brew services list
   ```

2. Verificar credenciales en `DATABASE_URL`

3. Verificar que la base de datos `autos_db` exista

### Error al Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias una por una si es necesario
pip install fastapi
pip install sqlmodel
pip install psycopg2-binary
```

### Puerto 8000 ya en uso

```bash
# Cambiar el puerto
uvicorn main:app --reload --port 8001
```

---

## Documentación Adicional

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Pydantic**: https://docs.pydantic.dev/

---

## Autor

Desarrollado para **Programación IV - Universidad Tecnológica Nacional**

---

## Licencia

Este proyecto es parte de un trabajo práctico académico.

---

## Notas

- La documentación interactiva está disponible en `/docs` (Swagger UI) y `/redoc`
- El endpoint `/health` permite verificar el estado de la aplicación
- El endpoint `/stats` proporciona estadísticas generales del sistema
- Todas las respuestas están en formato JSON
- Los errores siguen el formato estándar de FastAPI

---

**¡Éxitos en el desarrollo!** 🚗💻

