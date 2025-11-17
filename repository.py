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
    
    @abstractmethod
    def create(self, auto: AutoCreate) -> Auto:
        pass
    
    @abstractmethod
    def get_by_id(self, auto_id: int) -> Optional[Auto]:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Auto]:
        pass
    
    @abstractmethod
    def update(self, auto_id: int, auto_update: AutoUpdate) -> Optional[Auto]:
        pass
    
    @abstractmethod
    def delete(self, auto_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_chasis(self, numero_chasis: str) -> Optional[Auto]:
        pass
    
    @abstractmethod
    def search(self, params: AutoSearchParams, skip: int = 0, limit: int = 10) -> List[Auto]:
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        pass


class VentaRepositoryInterface(ABC):
    
    @abstractmethod
    def create(self, venta: VentaCreate) -> Venta:
        pass
    
    @abstractmethod
    def get_by_id(self, venta_id: int) -> Optional[Venta]:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Venta]:
        pass
    
    @abstractmethod
    def update(self, venta_id: int, venta_update: VentaUpdate) -> Optional[Venta]:
        pass
    
    @abstractmethod
    def delete(self, venta_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_auto_id(self, auto_id: int) -> List[Venta]:
        pass
    
    @abstractmethod
    def get_by_comprador(self, nombre: str) -> List[Venta]:
        pass
    
    @abstractmethod
    def search(self, params: VentaSearchParams, skip: int = 0, limit: int = 10) -> List[Venta]:
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        pass


class AutoRepository(AutoRepositoryInterface):
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create(self, nuevo_auto: AutoCreate) -> Auto:
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
        try:
            consulta = select(Auto).where(Auto.id == auto_id)
            return self.db_session.exec(consulta).first()
        except Exception as error:
            raise handle_database_error(error)
    
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Auto]:
        try:
            consulta = select(Auto).offset(skip).limit(limit).order_by(Auto.id)
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def update(self, auto_id: int, datos_actualizacion: AutoUpdate) -> Optional[Auto]:
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
        try:
            consulta = select(Auto).where(Auto.numero_chasis == numero_chasis.upper())
            return self.db_session.exec(consulta).first()
        except Exception as error:
            raise handle_database_error(error)
    
    def search(self, filtros: AutoSearchParams, skip: int = 0, limit: int = 10) -> List[Auto]:
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
        try:
            consulta = select(func.count(Auto.id))
            return self.db_session.exec(consulta).first() or 0
        except Exception as error:
            raise handle_database_error(error)
    
    def get_with_ventas(self, auto_id: int) -> Optional[Auto]:
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
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create(self, nueva_venta: VentaCreate) -> Venta:
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
        try:
            consulta = select(Venta).where(Venta.id == venta_id)
            return self.db_session.exec(consulta).first()
        except Exception as error:
            raise handle_database_error(error)
    
    def get_all(self, skip: int = 0, limit: int = 10) -> List[Venta]:
        try:
            consulta = select(Venta).offset(skip).limit(limit).order_by(Venta.fecha_venta.desc())
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def update(self, venta_id: int, datos_actualizacion: VentaUpdate) -> Optional[Venta]:
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
        try:
            consulta = select(Venta).where(Venta.auto_id == auto_id).order_by(Venta.fecha_venta.desc())
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def get_by_comprador(self, nombre: str) -> List[Venta]:
        try:
            consulta = select(Venta).where(
                Venta.nombre_comprador.ilike(f"%{nombre}%")
            ).order_by(Venta.fecha_venta.desc())
            return list(self.db_session.exec(consulta).all())
        except Exception as error:
            raise handle_database_error(error)
    
    def search(self, filtros: VentaSearchParams, skip: int = 0, limit: int = 10) -> List[Venta]:
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
        try:
            consulta = select(func.count(Venta.id))
            return self.db_session.exec(consulta).first() or 0
        except Exception as error:
            raise handle_database_error(error)
    
    def get_with_auto(self, venta_id: int) -> Optional[Venta]:
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
    
    @staticmethod
    def create_auto_repository(db_session: Session) -> AutoRepositoryInterface:
        return AutoRepository(db_session)
    
    @staticmethod
    def create_venta_repository(db_session: Session) -> VentaRepositoryInterface:
        return VentaRepository(db_session)


def get_auto_repository(db_session: Session):
    return RepositoryFactory.create_auto_repository(db_session)


def get_venta_repository(db_session: Session):
    return RepositoryFactory.create_venta_repository(db_session)
