# API CRUD de Ventas de Autos

## Programación IV - Universidad Tecnológica Nacional

---

## Descripción del Proyecto

Este proyecto implementa una **API REST completa** para la gestión de ventas de autos desarrollada con **FastAPI**, **SQLModel** y **PostgreSQL**. 

La aplicación permite administrar un inventario de vehículos y registrar las ventas realizadas, implementando todas las operaciones CRUD (Create, Read, Update, Delete) para ambas entidades y aplicando patrones de diseño profesionales como el **Repository Pattern** y **Dependency Injection**.

---

## Autor

**Desarrollado por:** Juan Cruz Fernandez Osuna 
**Materia:** Programación IV  
**Universidad:** Universidad Tecnológica Nacional  
**Año:** 2025

---

## Características Implementadas

- ✅ **CRUD Completo**: Operaciones Create, Read, Update, Delete para Autos y Ventas
- ✅ **Validaciones Robustas**: Validación de datos con Pydantic y reglas de negocio personalizadas
- ✅ **Patrón Repository**: Implementación completa del patrón Repository para acceso a datos
- ✅ **Paginación**: Paginación implementada en todos los endpoints de listado
- ✅ **Búsquedas Avanzadas**: Filtros por marca, modelo, precio, fecha, comprador
- ✅ **Relaciones**: Gestión de relaciones uno-a-muchos entre Autos y Ventas
- ✅ **Documentación Automática**: Documentación interactiva con Swagger UI y ReDoc
- ✅ **Manejo de Errores**: Manejo apropiado de errores HTTP (400, 404, 422, 500)

---

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para construir APIs REST
- **SQLModel**: ORM basado en SQLAlchemy y Pydantic para modelado de datos
- **PostgreSQL**: Base de datos relacional robusta
- **Pydantic**: Validación de datos y serialización
- **Python 3.13**: Lenguaje de programación utilizado

---

## Arquitectura del Proyecto

### Patrón de Diseño Implementado

He implementado el **Patrón Repository** para separar la lógica de acceso a datos de la lógica de negocio. Esto permite:

- **Separación de responsabilidades**: Los endpoints no acceden directamente a la base de datos
- **Testabilidad**: Facilita la creación de tests unitarios con mocks
- **Mantenibilidad**: Cambios en la capa de datos no afectan los endpoints
- **Reutilización**: La lógica de acceso a datos puede reutilizarse

### Estructura del Proyecto

```
TrabajoFastAPI/
├── main.py              # Aplicación FastAPI principal, configuración y endpoints generales
├── database.py          # Configuración de conexión a PostgreSQL y gestión de sesiones
├── models.py            # Modelos SQLModel (Auto, Venta) y esquemas Pydantic
├── repository.py        # Implementación del patrón Repository (interfaces y clases concretas)
├── autos.py            # Router con todos los endpoints relacionados con autos
├── ventas.py           # Router con todos los endpoints relacionados con ventas
├── requirements.txt     # Dependencias del proyecto con versiones específicas
└── README.md           # Este archivo de documentación
```

### Descripción de Archivos

#### `main.py`
- Configuración principal de la aplicación FastAPI
- Registro de routers (`autos` y `ventas`)
- Manejo global de excepciones (404, 500)
- Endpoints generales (`/`, `/health`, `/stats`)
- Configuración de CORS

#### `models.py`
- Define los modelos de datos usando SQLModel
- Modelos base: `AutoBase`, `VentaBase`
- Modelos de tabla: `Auto`, `Venta` (con relaciones)
- Modelos para operaciones: `AutoCreate`, `AutoUpdate`, `VentaCreate`, `VentaUpdate`
- Modelos de respuesta: `AutoResponse`, `VentaResponse`, etc.
- Validadores personalizados con Pydantic

#### `repository.py`
- Interfaces abstractas: `AutoRepositoryInterface`, `VentaRepositoryInterface`
- Implementaciones concretas: `AutoRepository`, `VentaRepository`
- Factory Pattern para crear instancias de repositorios
- Manejo de errores de base de datos

#### `autos.py`
- Router de FastAPI para endpoints de autos
- Endpoints CRUD completos
- Búsqueda por número de chasis
- Búsqueda avanzada con filtros
- Estadísticas de autos

#### `ventas.py`
- Router de FastAPI para endpoints de ventas
- Endpoints CRUD completos
- Búsqueda por auto y comprador
- Búsqueda avanzada con filtros
- Estadísticas y reportes de ventas

#### `database.py`
- Configuración de conexión a PostgreSQL
- Gestión de sesiones con Dependency Injection
- Creación automática de tablas
- Utilidades para desarrollo y testing

---

## Cómo Funciona la Aplicación

### Flujo de una Petición

1. **Cliente** realiza una petición HTTP a un endpoint (ej: `POST /autos`)
2. **FastAPI** recibe la petición y la enruta al router correspondiente (`autos.py`)
3. **Endpoint** valida los datos usando los modelos Pydantic (`AutoCreate`)
4. **Dependency Injection** proporciona una sesión de base de datos y un repositorio
5. **Repository** ejecuta la lógica de acceso a datos (crear auto en la BD)
6. **SQLModel** traduce las operaciones a SQL y las ejecuta en PostgreSQL
7. **Respuesta** se serializa usando los modelos de respuesta (`AutoResponse`)
8. **FastAPI** retorna la respuesta JSON al cliente

### Relaciones entre Entidades

La aplicación implementa una relación **uno-a-muchos** entre `Auto` y `Venta`:

- Un `Auto` puede tener múltiples `Venta`s
- Una `Venta` pertenece a un único `Auto`
- La relación se implementa mediante `foreign_key` en la tabla `venta`
- SQLModel maneja automáticamente las relaciones mediante `Relationship`

### Validaciones Implementadas

#### Auto
- **Año**: Debe estar entre 1900 y el año actual
- **Número de chasis**: Debe ser único, alfanumérico y se normaliza a mayúsculas
- **Marca y modelo**: No pueden estar vacíos, se normalizan con formato título

#### Venta
- **Precio**: Debe ser mayor a 0 y se redondea a 2 decimales
- **Nombre comprador**: No puede estar vacío, se normaliza con formato título
- **Fecha de venta**: No puede ser una fecha futura
- **Auto ID**: Debe existir un auto con ese ID antes de crear la venta

---

## Instalación y Configuración

### Requisitos Previos

- **Python 3.8 o superior** (probado con Python 3.13)
- **PostgreSQL** instalado y corriendo
- **pip** (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd TrabajoFastAPI
   ```

2. **Crear entorno virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar PostgreSQL**
   
   Crear la base de datos:
   ```sql
   CREATE DATABASE autos_db;
   ```
   
   Configurar variables de entorno creando un archivo `.env`:
   ```env
   DATABASE_URL=postgresql://usuario:password@localhost:5432/autos_db
   ENVIRONMENT=development
   ```
   
   > **Nota**: Reemplazar `usuario` y `password` con las credenciales de PostgreSQL.

5. **Inicializar la base de datos**
   
   La aplicación creará automáticamente las tablas al iniciar. También se puede ejecutar manualmente:
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

Una vez iniciada, la aplicación estará disponible en:
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
| GET | `/autos/{auto_id}/with-ventas` | Obtener auto con sus ventas asociadas |
| GET | `/autos/search/` | Búsqueda avanzada con filtros |
| GET | `/autos/stats/summary` | Estadísticas de autos |
| GET | `/autos/validate/chasis/{numero_chasis}` | Validar disponibilidad de chasis |

### Ventas (`/ventas`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/ventas` | Crear nueva venta |
| GET | `/ventas` | Listar ventas con paginación |
| GET | `/ventas/{venta_id}` | Obtener venta por ID |
| PUT | `/ventas/{venta_id}` | Actualizar venta |
| DELETE | `/ventas/{venta_id}` | Eliminar venta |
| GET | `/ventas/auto/{auto_id}` | Obtener ventas de un auto específico |
| GET | `/ventas/comprador/{nombre}` | Obtener ventas por nombre de comprador |
| GET | `/ventas/{venta_id}/with-auto` | Obtener venta con información del auto |
| GET | `/ventas/search/` | Búsqueda avanzada con filtros |
| GET | `/ventas/stats/summary` | Estadísticas generales de ventas |
| GET | `/ventas/stats/monthly` | Estadísticas mensuales |
| GET | `/ventas/reports/top-buyers` | Mejores compradores |
| GET | `/ventas/reports/recent` | Ventas recientes |

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

---

## Solución de Problemas

### Error de Conexión a Base de Datos

1. Verificar que PostgreSQL esté corriendo
2. Verificar credenciales en el archivo `.env`
3. Verificar que la base de datos `autos_db` exista

### Error al Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### Puerto 8000 ya en uso

```bash
# Cambiar el puerto en main.py o usar:
uvicorn main:app --reload --port 8001
```

---

## Documentación Adicional

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Pydantic**: https://docs.pydantic.dev/

---

## Notas Técnicas

- La documentación interactiva está disponible automáticamente en `/docs` (Swagger UI) y `/redoc`
- El endpoint `/health` permite verificar el estado de la aplicación y la conexión a la base de datos
- El endpoint `/stats` proporciona estadísticas generales del sistema
- Todas las respuestas están en formato JSON
- Los errores siguen el formato estándar de FastAPI con códigos HTTP apropiados
- La aplicación crea automáticamente las tablas en PostgreSQL al iniciar
- Se utiliza Dependency Injection para gestionar sesiones de base de datos y repositorios

---

## Licencia

Este proyecto es parte de un trabajo práctico para materia Programación IV con el fin de obtener la regularidad de la materia.
