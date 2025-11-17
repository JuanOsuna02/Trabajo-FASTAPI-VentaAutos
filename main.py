from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os

from database import initialize_database, test_database_connection, get_database_info
from autos import router as autos_router
from ventas import router as ventas_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando servidor FastAPI...")
    
    try:
        initialize_database()
        print("Base de datos conectada exitosamente")
        
        db_config = get_database_info()
        print(f"Conectado a: {db_config['database_url']}")
        
    except Exception as error:
        print(f"Error durante la inicializacion: {error}")
        raise
    
    print("Servidor iniciado correctamente")
    print("Documentacion disponible en: http://localhost:8000/docs")
    print("Documentacion alternativa: http://localhost:8000/redoc")
    
    yield
    
    print("Cerrando servidor...")
    print("Adios!")


app = FastAPI(
    title="API de Ventas de Autos",
    description="""
    ## API REST para gestion de ventas de autos
    
    Sistema completo para administrar inventario de vehiculos y registrar ventas.
    
    ### Caracteristicas principales:
    
    * **Gestion de Autos**: Operaciones CRUD para vehiculos
    * **Gestion de Ventas**: Registro y seguimiento de ventas
    * **Busquedas**: Filtros avanzados por marca, modelo, precio, fecha
    * **Estadisticas**: Reportes y analisis de ventas
    * **Validaciones**: Reglas de negocio e integridad de datos
    
    ### Stack tecnologico:
    
    * **FastAPI**: Framework web moderno
    * **SQLModel**: ORM basado en SQLAlchemy y Pydantic
    * **PostgreSQL**: Base de datos relacional
    * **Pydantic**: Validacion y serializacion
    
    ### Caracteristicas tecnicas:
    
    * Paginacion en endpoints de listado
    * Manejo de errores HTTP estandar
    * Validaciones de integridad referencial
    * Documentacion interactiva automatica
    * Patron Repository para acceso a datos
    
    ---
    
    **Desarrollado para**: Programacion IV - Universidad Tecnologica Nacional
    """,
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "desarrollo@utn.edu.ar",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(autos_router)
app.include_router(ventas_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "mensaje": "API de Ventas de Autos",
        "version": "1.0.0",
        "descripcion": "API REST para gestion de inventario y ventas de vehiculos",
        "documentacion": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints_principales": {
            "autos": "/autos",
            "ventas": "/ventas",
            "salud": "/health",
            "estadisticas": "/stats"
        },
        "tecnologias": ["FastAPI", "SQLModel", "PostgreSQL", "Pydantic"],
        "universidad": "Universidad Tecnologica Nacional",
        "materia": "Programacion IV"
    }


@app.get("/health", tags=["health"])
async def health_check():
    try:
        conexion_ok = test_database_connection()
        config_db = get_database_info()
        
        return {
            "status": "healthy" if conexion_ok else "unhealthy",
            "timestamp": "2024-11-17T15:30:00Z",
            "version": "1.0.0",
            "database": {
                "connected": conexion_ok,
                "url": config_db["database_url"],
                "pool_size": config_db["pool_size"]
            },
            "environment": config_db["environment"]
        }
        
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error en verificacion de salud: {str(error)}"
        )


@app.get("/stats", tags=["statistics"])
async def get_general_stats():
    try:
        from database import get_session
        from repository import get_auto_repository, get_venta_repository
        
        session_gen = get_session()
        db_session = next(session_gen)
        
        try:
            repo_autos = get_auto_repository(db_session)
            repo_ventas = get_venta_repository(db_session)
            
            total_autos = repo_autos.count_all()
            total_ventas = repo_ventas.count_all()
            estadisticas = repo_ventas.get_sales_statistics()
            
            return {
                "resumen_general": {
                    "total_autos_registrados": total_autos,
                    "total_ventas_realizadas": total_ventas,
                    "ingresos_totales": estadisticas["total_ingresos"],
                    "precio_promedio_venta": estadisticas["precio_promedio"]
                },
                "estadisticas_detalladas": {
                    "autos": f"/autos/stats/summary",
                    "ventas": f"/ventas/stats/summary"
                },
                "ultima_actualizacion": "2024-11-17T15:30:00Z"
            }
            
        finally:
            db_session.close()
            
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadisticas: {str(error)}"
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Recurso no encontrado",
            "mensaje": "La URL solicitada no existe en esta API",
            "codigo": 404,
            "documentacion": "/docs"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "mensaje": "Ha ocurrido un error inesperado. Por favor, contacte al administrador.",
            "codigo": 500,
            "soporte": "desarrollo@utn.edu.ar"
        }
    )


def obtener_configuracion():
    return {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "reload": os.getenv("ENVIRONMENT", "development").lower() == "development",
        "log_level": os.getenv("LOG_LEVEL", "info").lower()
    }


if __name__ == "__main__":
    config = obtener_configuracion()
    
    print("Configuracion del servidor:")
    print(f"   Host: {config['host']}")
    print(f"   Puerto: {config['port']}")
    print(f"   Recarga automatica: {config['reload']}")
    print(f"   Nivel de log: {config['log_level']}")
    print()
    
    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        reload=config["reload"],
        log_level=config["log_level"]
    )
