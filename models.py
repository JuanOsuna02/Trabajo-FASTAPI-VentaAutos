from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
import re


class AutoBase(SQLModel):
    """Modelo base con los campos comunes de un vehiculo"""
    marca: str = Field(min_length=1, max_length=50, description="Marca del vehiculo")
    modelo: str = Field(min_length=1, max_length=50, description="Modelo del vehiculo")
    año: int = Field(ge=1900, le=datetime.now().year, description="Año de fabricacion")
    numero_chasis: str = Field(min_length=5, max_length=30, description="Numero unico de chasis")

    @field_validator('numero_chasis')
    @classmethod
    def validar_chasis(cls, valor: str) -> str:
        """Verifica que el numero de chasis sea alfanumerico"""
        if not re.match(r'^[A-Za-z0-9]+$', valor):
            raise ValueError('El numero de chasis debe ser alfanumerico')
        return valor.upper()

    @field_validator('marca', 'modelo')
    @classmethod
    def limpiar_texto(cls, valor: str) -> str:
        """Normaliza y limpia campos de texto"""
        return valor.strip().title()


class VentaBase(SQLModel):
    """Modelo base con los campos comunes de una venta"""
    nombre_comprador: str = Field(min_length=2, max_length=100, description="Nombre del comprador")
    precio: float = Field(gt=0, description="Precio de venta")
    fecha_venta: datetime = Field(description="Fecha y hora de la venta")
    auto_id: int = Field(foreign_key="auto.id", description="ID del auto vendido")

    @field_validator('precio')
    @classmethod
    def validar_precio(cls, valor: float) -> float:
        """Verifica que el precio sea positivo y redondea a 2 decimales"""
        if valor <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return round(valor, 2)

    @field_validator('fecha_venta')
    @classmethod
    def validar_fecha(cls, valor: datetime) -> datetime:
        """Verifica que la fecha no sea futura"""
        if valor > datetime.now():
            raise ValueError('La fecha de venta no puede ser futura')
        return valor

    @field_validator('nombre_comprador')
    @classmethod
    def limpiar_nombre(cls, valor: str) -> str:
        """Normaliza el nombre del comprador"""
        nombre_normalizado = valor.strip()
        if not nombre_normalizado:
            raise ValueError('El nombre del comprador no puede estar vacio')
        return nombre_normalizado.title()


class Auto(AutoBase, table=True):
    """Modelo de tabla para vehiculos"""
    id: Optional[int] = Field(default=None, primary_key=True)
    ventas: List["Venta"] = Relationship(back_populates="auto")


class Venta(VentaBase, table=True):
    """Modelo de tabla para ventas"""
    id: Optional[int] = Field(default=None, primary_key=True)
    auto: Optional[Auto] = Relationship(back_populates="ventas")


class AutoCreate(AutoBase):
    """Modelo para crear un nuevo vehiculo"""
    pass


class AutoUpdate(SQLModel):
    """Modelo para actualizar un vehiculo con campos opcionales"""
    marca: Optional[str] = Field(None, min_length=1, max_length=50)
    modelo: Optional[str] = Field(None, min_length=1, max_length=50)
    año: Optional[int] = Field(None, ge=1900, le=datetime.now().year)
    numero_chasis: Optional[str] = Field(None, min_length=5, max_length=30)

    @field_validator('numero_chasis')
    @classmethod
    def validar_chasis(cls, valor: Optional[str]) -> Optional[str]:
        """Verifica que el numero de chasis sea alfanumerico"""
        if valor is not None:
            if not re.match(r'^[A-Za-z0-9]+$', valor):
                raise ValueError('El numero de chasis debe ser alfanumerico')
            return valor.upper()
        return valor

    @field_validator('marca', 'modelo')
    @classmethod
    def limpiar_texto(cls, valor: Optional[str]) -> Optional[str]:
        """Normaliza y limpia campos de texto"""
        if valor is not None:
            return valor.strip().title()
        return valor


class VentaCreate(VentaBase):
    """Modelo para crear una nueva venta"""
    pass


class VentaUpdate(SQLModel):
    """Modelo para actualizar una venta con campos opcionales"""
    nombre_comprador: Optional[str] = Field(None, min_length=2, max_length=100)
    precio: Optional[float] = Field(None, gt=0)
    fecha_venta: Optional[datetime] = None
    auto_id: Optional[int] = None

    @field_validator('precio')
    @classmethod
    def validar_precio(cls, valor: Optional[float]) -> Optional[float]:
        """Verifica que el precio sea positivo y redondea a 2 decimales"""
        if valor is not None:
            if valor <= 0:
                raise ValueError('El precio debe ser mayor a 0')
            return round(valor, 2)
        return valor

    @field_validator('fecha_venta')
    @classmethod
    def validar_fecha(cls, valor: Optional[datetime]) -> Optional[datetime]:
        """Verifica que la fecha no sea futura"""
        if valor is not None and valor > datetime.now():
            raise ValueError('La fecha de venta no puede ser futura')
        return valor

    @field_validator('nombre_comprador')
    @classmethod
    def limpiar_nombre(cls, valor: Optional[str]) -> Optional[str]:
        """Normaliza el nombre del comprador"""
        if valor is not None:
            nombre_normalizado = valor.strip()
            if not nombre_normalizado:
                raise ValueError('El nombre del comprador no puede estar vacio')
            return nombre_normalizado.title()
        return valor


class AutoResponse(AutoBase):
    """Modelo de respuesta para vehiculos"""
    id: int


class AutoResponseWithVentas(AutoResponse):
    """Modelo de respuesta para vehiculos con sus ventas"""
    ventas: List["VentaResponse"] = []


class VentaResponse(VentaBase):
    """Modelo de respuesta para ventas"""
    id: int


class VentaResponseWithAuto(VentaResponse):
    """Modelo de respuesta para ventas con informacion del auto"""
    auto: Optional[AutoResponse] = None


class AutoSearchParams(SQLModel):
    """Parametros para buscar vehiculos"""
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año_min: Optional[int] = Field(None, ge=1900)
    año_max: Optional[int] = Field(None, le=datetime.now().year)


class VentaSearchParams(SQLModel):
    """Parametros para buscar ventas"""
    nombre_comprador: Optional[str] = None
    precio_min: Optional[float] = Field(None, gt=0)
    precio_max: Optional[float] = Field(None, gt=0)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    auto_id: Optional[int] = None

    @field_validator('precio_min', 'precio_max')
    @classmethod
    def validar_precios(cls, valor: Optional[float]) -> Optional[float]:
        """Verifica que los precios sean positivos"""
        if valor is not None and valor <= 0:
            raise ValueError('Los precios deben ser mayores a 0')
        return valor


class PaginationParams(SQLModel):
    """Parametros de paginacion"""
    skip: int = Field(default=0, ge=0, description="Registros a omitir")
    limit: int = Field(default=10, ge=1, le=100, description="Maximo de registros")


class PaginatedResponse(SQLModel):
    """Respuesta paginada generica"""
    total: int = Field(description="Total de registros")
    skip: int = Field(description="Registros omitidos")
    limit: int = Field(description="Limite por pagina")
    has_next: bool = Field(description="Indica si hay mas paginas")


class PaginatedAutosResponse(PaginatedResponse):
    """Respuesta paginada para vehiculos"""
    items: List[AutoResponse] = []


class PaginatedVentasResponse(PaginatedResponse):
    """Respuesta paginada para ventas"""
    items: List[VentaResponse] = []
