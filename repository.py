from abc import ABC, abstractmethod
from typing import Optional, List
from sqlmodel import Session, select, func, and_
from sqlalchemy.exc import IntegrityError as SQLIntegrityError

from models import (
    Auto, Venta, AutoCreate, AutoUpdate, VentaCreate, VentaUpdate,
    AutoSearchParams, VentaSearchParams
)
from database import handle_database_error, IntegrityError


class AutoRepositoryInterface(ABC):
    """Interfaz abstracta para el repositorio de vehiculos"""
    
    @abstractmethod
    def create(self, auto: AutoCreate) -> Auto:
        """Registra un nuevo vehiculo"""
        pass
    
    @abstractmethod
    def get_by_id(self, auto_id: int) -> Optional[Auto]:
        """Obtiene un vehiculo por su identificador"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Auto]:
        """Lista todos los vehiculos con paginacion"""
        pass
    
    @abstractmethod
    def update(self, auto_id: int, auto_update: AutoUpdate) -> Optional[Auto]:
        """Actualiza los datos de un vehiculo"""
        pass
    
    @abstractmethod
    def delete(self, auto_id: int) -> bool:
        """Elimina un vehiculo del sistema"""
        pass
    
    @abstractmethod
    def get_by_chasis(self, numero_chasis: str) -> Optional[Auto]:
        """Busca un vehiculo por su numero de chasis"""
        pass
    
    @abstractmethod
    def search(self, params: AutoSearchParams, skip: int = 0, limit: int = 10) -> List[Auto]:
        """Busca vehiculos aplicando filtros"""
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        """Cuenta el total de vehiculos registrados"""
        pass


class VentaRepositoryInterface(ABC):
    """Interfaz abstracta para el repositorio de ventas"""
    
    @abstractmethod
    def create(self, venta: VentaCreate) -> Venta:
        """Registra una nueva venta"""
        pass
    
    @abstractmethod
    def get_by_id(self, venta_id: int) -> Optional[Venta]:
        """Obtiene una venta por su identificador"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Venta]:
        """Lista todas las ventas con paginacion"""
        pass
    
    @abstractmethod
    def update(self, venta_id: int, venta_update: VentaUpdate) -> Optional[Venta]:
        """Actualiza los datos de una venta"""
        pass
    
    @abstractmethod
    def delete(self, venta_id: int) -> bool:
        """Elimina una venta del sistema"""
        pass
    
    @abstractmethod
    def get_by_auto_id(self, auto_id: int) -> List[Venta]:
        """Obtiene todas las ventas de un vehiculo"""
        pass
    
    @abstractmethod
    def get_by_comprador(self, nombre: str) -> List[Venta]:
        """Obtiene todas las ventas de un comprador"""
        pass
    
    @abstractmethod
    def search(self, params: VentaSearchParams, skip: int = 0, limit: int = 10) -> List[Venta]:
        """Busca ventas aplicando filtros"""
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        """Cuenta el total de ventas registradas"""
        pass


class AutoRepository(AutoRepositoryInterface):
    """Implementacion del repositorio de vehiculos"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create(self, nuevo_auto: AutoCreate) -> Auto:
        """Registra un nuevo vehiculo en la base de datos"""
        try:
            vehiculo_existente = self.get_by_chasis(nuevo_auto.numero_chasis)
            if vehiculo_existente:
                raise IntegrityError(f"Ya existe un vehiculo con el numero de chasis: {nuevo_auto.numero_chasis}")
            
            vehiculo = Auto.model_validate(nuevo_auto)
            self.db_session.add(vehiculo)
            self.db_session.commit()
            self.db_session.refresh(vehiculo)
            return vehiculo
            
        except SQLIntegrityError as error:
            self.db_session.rollback()
            raise handle_database_error(error)
        except Exception as error:
            self.db_session.rollback()
            raise handle_database_error(error)
    
    def get_by_id(self, auto_id: int) -> Optional[Auto]:
        """Obtiene un vehiculo por su identificador"""
        try:
            consulta = select(Auto).where(Auto.id == auto_id)
            return self.db_session.exec(consulta).first()
        except Exception as error:
            raise handle_database_error(error)
    
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Auto]:
        """Lista todos los vehiculos con paginacion"""
        try:
            consulta = select(Auto).offset(skip).limit(limit).order_by(Auto.id)
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def update(self, auto_id: int, datos_actualizacion: AutoUpdate) -> Optional[Auto]:
        """Actualiza los datos de un vehiculo existente"""
        try:
            vehiculo = self.get_by_id(auto_id)
            if not vehiculo:
                return None
            
            if datos_actualizacion.numero_chasis:
                vehiculo_existente = self.get_by_chasis(datos_actualizacion.numero_chasis)
                if vehiculo_existente and vehiculo_existente.id != auto_id:
                    raise IntegrityError(f"Ya existe un vehiculo con el numero de chasis: {datos_actualizacion.numero_chasis}")
            
            datos = datos_actualizacion.model_dump(exclude_unset=True)
            for campo, valor in datos.items():
                setattr(vehiculo, campo, valor)
            
            self.db_session.add(vehiculo)
            self.db_session.commit()
            self.db_session.refresh(vehiculo)
            return vehiculo
            
        except SQLIntegrityError as error:
            self.db_session.rollback()
            raise handle_database_error(error)
        except Exception as error:
            self.db_session.rollback()
            raise handle_database_error(error)
    
    def delete(self, auto_id: int) -> bool:
        """Elimina un vehiculo de la base de datos"""
        try:
            vehiculo = self.get_by_id(auto_id)
            if not vehiculo:
                return False
            
            cantidad_ventas = self.db_session.exec(
                select(func.count(Venta.id)).where(Venta.auto_id == auto_id)
            ).first()
            
            if cantidad_ventas and cantidad_ventas > 0:
                raise IntegrityError(f"No se puede eliminar el vehiculo porque tiene {cantidad_ventas} venta(s) asociada(s)")
            
            self.db_session.delete(vehiculo)
            self.db_session.commit()
            return True
            
        except SQLIntegrityError as error:
            self.db_session.rollback()
            raise handle_database_error(error)
        except Exception as error:
            self.db_session.rollback()
            raise handle_database_error(error)
    
    def get_by_chasis(self, numero_chasis: str) -> Optional[Auto]:
        """Busca un vehiculo por su numero de chasis"""
        try:
            consulta = select(Auto).where(Auto.numero_chasis == numero_chasis.upper())
            return self.db_session.exec(consulta).first()
        except Exception as error:
            raise handle_database_error(error)
    
    def search(self, filtros: AutoSearchParams, skip: int = 0, limit: int = 10) -> List[Auto]:
        """Busca vehiculos aplicando filtros especificos"""
        try:
            consulta = select(Auto)
            condiciones = []
            
            if filtros.marca:
                condiciones.append(Auto.marca.ilike(f"%{filtros.marca}%"))
            
            if filtros.modelo:
                condiciones.append(Auto.modelo.ilike(f"%{filtros.modelo}%"))
            
            if filtros.año_min:
                condiciones.append(Auto.año >= filtros.año_min)
            
            if filtros.año_max:
                condiciones.append(Auto.año <= filtros.año_max)
            
            if condiciones:
                consulta = consulta.where(and_(*condiciones))
            
            consulta = consulta.offset(skip).limit(limit).order_by(Auto.marca, Auto.modelo, Auto.año)
            
            return list(self.db_session.exec(consulta).all())
            
        except Exception as error:
            raise handle_database_error(error)
    
    def count_all(self) -> int:
        """Cuenta el total de vehiculos registrados"""
        try:
            consulta = select(func.count(Auto.id))
            return self.db_session.exec(consulta).first() or 0
        except Exception as error:
            raise handle_database_error(error)
    
    def get_with_ventas(self, auto_id: int) -> Optional[Auto]:
        """Obtiene un vehiculo junto con todas sus ventas"""
        try:
            consulta = select(Auto).where(Auto.id == auto_id)
            vehiculo = self.db_session.exec(consulta).first()
            if vehiculo:
                consulta_ventas = select(Venta).where(Venta.auto_id == auto_id)
                vehiculo.ventas = list(self.db_session.exec(consulta_ventas).all())
            return vehiculo
        except Exception as error:
            raise handle_database_error(error)


class VentaRepository(VentaRepositoryInterface):
    """Implementacion del repositorio de ventas"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create(self, nueva_venta: VentaCreate) -> Venta:
        """Registra una nueva venta en la base de datos"""
        try:
            consulta_auto = select(Auto).where(Auto.id == nueva_venta.auto_id)
            vehiculo = self.db_session.exec(consulta_auto).first()
            if not vehiculo:
                raise IntegrityError(f"No existe un vehiculo con ID: {nueva_venta.auto_id}")
            
            venta = Venta.model_validate(nueva_venta)
            self.db_session.add(venta)
            self.db_session.commit()
            self.db_session.refresh(venta)
            return venta
            
        except SQLIntegrityError as error:
            self.db_session.rollback()
            raise handle_database_error(error)
        except Exception as error:
            self.db_session.rollback()
            raise handle_database_error(error)
    
    def get_by_id(self, venta_id: int) -> Optional[Venta]:
        """Obtiene una venta por su identificador"""
        try:
            consulta = select(Venta).where(Venta.id == venta_id)
            return self.db_session.exec(consulta).first()
        except Exception as error:
            raise handle_database_error(error)
    
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Venta]:
        """Lista todas las ventas con paginacion"""
        try:
            consulta = select(Venta).offset(skip).limit(limit).order_by(Venta.fecha_venta.desc())
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def update(self, venta_id: int, datos_actualizacion: VentaUpdate) -> Optional[Venta]:
        """Actualiza los datos de una venta existente"""
        try:
            venta = self.get_by_id(venta_id)
            if not venta:
                return None
            
            if datos_actualizacion.auto_id:
                consulta_auto = select(Auto).where(Auto.id == datos_actualizacion.auto_id)
                vehiculo = self.db_session.exec(consulta_auto).first()
                if not vehiculo:
                    raise IntegrityError(f"No existe un vehiculo con ID: {datos_actualizacion.auto_id}")
            
            datos = datos_actualizacion.model_dump(exclude_unset=True)
            for campo, valor in datos.items():
                setattr(venta, campo, valor)
            
            self.db_session.add(venta)
            self.db_session.commit()
            self.db_session.refresh(venta)
            return venta
            
        except SQLIntegrityError as error:
            self.db_session.rollback()
            raise handle_database_error(error)
        except Exception as error:
            self.db_session.rollback()
            raise handle_database_error(error)
    
    def delete(self, venta_id: int) -> bool:
        """Elimina una venta de la base de datos"""
        try:
            venta = self.get_by_id(venta_id)
            if not venta:
                return False
            
            self.db_session.delete(venta)
            self.db_session.commit()
            return True
            
        except SQLIntegrityError as error:
            self.db_session.rollback()
            raise handle_database_error(error)
        except Exception as error:
            self.db_session.rollback()
            raise handle_database_error(error)
    
    def get_by_auto_id(self, auto_id: int) -> List[Venta]:
        """Obtiene todas las ventas de un vehiculo especifico"""
        try:
            consulta = select(Venta).where(Venta.auto_id == auto_id).order_by(Venta.fecha_venta.desc())
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def get_by_comprador(self, nombre: str) -> List[Venta]:
        """Obtiene todas las ventas de un comprador especifico"""
        try:
            consulta = select(Venta).where(
                Venta.nombre_comprador.ilike(f"%{nombre}%")
            ).order_by(Venta.fecha_venta.desc())
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def search(self, filtros: VentaSearchParams, skip: int = 0, limit: int = 10) -> List[Venta]:
        """Busca ventas aplicando filtros especificos"""
        try:
            consulta = select(Venta)
            condiciones = []
            
            if filtros.nombre_comprador:
                condiciones.append(Venta.nombre_comprador.ilike(f"%{filtros.nombre_comprador}%"))
            
            if filtros.precio_min:
                condiciones.append(Venta.precio >= filtros.precio_min)
            
            if filtros.precio_max:
                condiciones.append(Venta.precio <= filtros.precio_max)
            
            if filtros.fecha_inicio:
                condiciones.append(Venta.fecha_venta >= filtros.fecha_inicio)
            
            if filtros.fecha_fin:
                condiciones.append(Venta.fecha_venta <= filtros.fecha_fin)
            
            if filtros.auto_id:
                condiciones.append(Venta.auto_id == filtros.auto_id)
            
            if condiciones:
                consulta = consulta.where(and_(*condiciones))
            
            consulta = consulta.offset(skip).limit(limit).order_by(Venta.fecha_venta.desc())
            
            return list(self.db_session.exec(consulta).all())
            
        except Exception as error:
            raise handle_database_error(error)
    
    def count_all(self) -> int:
        """Cuenta el total de ventas registradas"""
        try:
            consulta = select(func.count(Venta.id))
            return self.db_session.exec(consulta).first() or 0
        except Exception as error:
            raise handle_database_error(error)
    
    def get_with_auto(self, venta_id: int) -> Optional[Venta]:
        """Obtiene una venta junto con la informacion del vehiculo asociado"""
        try:
            consulta = select(Venta).where(Venta.id == venta_id)
            venta = self.db_session.exec(consulta).first()
            if venta:
                consulta_auto = select(Auto).where(Auto.id == venta.auto_id)
                venta.auto = self.db_session.exec(consulta_auto).first()
            return venta
        except Exception as error:
            raise handle_database_error(error)
    
    def get_sales_statistics(self) -> dict:
        """Genera estadisticas generales sobre las ventas"""
        try:
            total_ventas = self.count_all()
            
            total_ingresos = self.db_session.exec(
                select(func.sum(Venta.precio))
            ).first() or 0
            
            precio_promedio = self.db_session.exec(
                select(func.avg(Venta.precio))
            ).first() or 0
            
            precio_maximo = self.db_session.exec(
                select(func.max(Venta.precio))
            ).first() or 0
            
            precio_minimo = self.db_session.exec(
                select(func.min(Venta.precio))
            ).first() or 0
            
            return {
                "total_ventas": total_ventas,
                "total_ingresos": float(total_ingresos),
                "precio_promedio": float(precio_promedio),
                "precio_maximo": float(precio_maximo),
                "precio_minimo": float(precio_minimo)
            }
            
        except Exception as error:
            raise handle_database_error(error)


class RepositoryFactory:
    """Factory para crear instancias de repositorios"""
    
    @staticmethod
    def create_auto_repository(db_session: Session) -> AutoRepositoryInterface:
        """Crea una instancia del repositorio de vehiculos"""
        return AutoRepository(db_session)
    
    @staticmethod
    def create_venta_repository(db_session: Session) -> VentaRepositoryInterface:
        """Crea una instancia del repositorio de ventas"""
        return VentaRepository(db_session)


def get_auto_repository(db_session: Session):
    """Funcion helper para dependency injection del repositorio de vehiculos"""
    return RepositoryFactory.create_auto_repository(db_session)


def get_venta_repository(db_session: Session):
    """Funcion helper para dependency injection del repositorio de ventas"""
    return RepositoryFactory.create_venta_repository(db_session)
