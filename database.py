import os
import logging
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine
from sqlalchemy import text

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class DatabaseConfig:
    
    def __init__(self):
        self.database_url = self._obtener_url()
        self.echo = self._obtener_echo()
        
    def _obtener_url(self) -> str:
        url = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:password@localhost:5432/autos_db"
        )
        
        if not url:
            raise ValueError("DATABASE_URL no esta configurada")
            
        return url
    
    def _obtener_echo(self) -> bool:
        entorno = os.getenv("ENVIRONMENT", "development").lower()
        return entorno == "development"


config = DatabaseConfig()

motor_db: Engine = create_engine(
    config.database_url,
    echo=config.echo,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)


def create_db_and_tables() -> None:
    try:
        SQLModel.metadata.create_all(motor_db)
        print("[OK] Tablas creadas correctamente")
    except Exception as error:
        print(f"[ERROR] Error al crear tablas: {error}")
        raise


def drop_db_and_tables() -> None:
    try:
        SQLModel.metadata.drop_all(motor_db)
        print("[ADVERTENCIA] Todas las tablas han sido eliminadas")
    except Exception as error:
        print(f"[ERROR] Error al eliminar tablas: {error}")
        raise


def test_database_connection() -> bool:
    try:
        with Session(motor_db) as db_session:
            db_session.exec(text("SELECT 1"))
            print("[OK] Conexion a base de datos exitosa")
            return True
    except Exception as error:
        print(f"[ERROR] Error de conexion a base de datos: {error}")
        return False


def get_session() -> Generator[Session, None, None]:
    with Session(motor_db) as db_session:
        try:
            yield db_session
        except Exception as error:
            db_session.rollback()
            print(f"[ERROR] Error en sesion de base de datos: {error}")
            raise
        finally:
            db_session.close()


def reset_database() -> None:
    print("[ADVERTENCIA] Reiniciando base de datos...")
    drop_db_and_tables()
    create_db_and_tables()
    print("[OK] Base de datos reiniciada correctamente")


def get_database_info() -> dict:
    url_segura = config.database_url
    if "@" in url_segura:
        partes = url_segura.split("://")
        if len(partes) == 2:
            protocolo = partes[0]
            resto = partes[1]
            if "@" in resto:
                credenciales, host = resto.split("@", 1)
                url_segura = f"{protocolo}://***:***@{host}"
    
    return {
        "database_url": url_segura,
        "echo_sql": config.echo,
        "pool_size": motor_db.pool.size(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


def initialize_database() -> None:
    print("Inicializando base de datos...")
    
    if not test_database_connection():
        raise ConnectionError("No se pudo conectar a la base de datos")
    
    create_db_and_tables()
    
    info_db = get_database_info()
    print(f"Base de datos configurada: {info_db['database_url']}")
    print(f"SQL Echo: {info_db['echo_sql']}")
    print(f"Pool Size: {info_db['pool_size']}")
    
    print("[OK] Base de datos inicializada correctamente")


class DatabaseError(Exception):
    pass


class ConnectionError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


def handle_database_error(error: Exception) -> DatabaseError:
    mensaje_error = str(error).lower()
    
    if "connection" in mensaje_error:
        return ConnectionError(f"Error de conexion a base de datos: {mensaje_error}")
    elif "unique" in mensaje_error or "duplicate" in mensaje_error:
        return IntegrityError(f"Violacion de restriccion unica: {mensaje_error}")
    elif "foreign key" in mensaje_error:
        return IntegrityError(f"Violacion de clave foranea: {mensaje_error}")
    else:
        return DatabaseError(f"Error de base de datos: {mensaje_error}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python database.py [init|reset|test|info]")
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    if comando == "init":
        initialize_database()
    elif comando == "reset":
        confirmacion = input("[ADVERTENCIA] ¿Estas seguro de reiniciar la base de datos? (y/N): ")
        if confirmacion.lower() == 'y':
            reset_database()
        else:
            print("Operacion cancelada")
    elif comando == "test":
        test_database_connection()
    elif comando == "info":
        informacion = get_database_info()
        print("Informacion de Base de Datos:")
        for clave, valor in informacion.items():
            print(f"  {clave}: {valor}")
    else:
        print(f"Comando desconocido: {comando}")
        print("Comandos disponibles: init, reset, test, info")
        sys.exit(1)
