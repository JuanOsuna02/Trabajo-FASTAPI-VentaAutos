from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
import re


class AutoBase(SQLModel):
    marca: str = Field(min_length=1, max_length=50, description="Marca del vehiculo")
    modelo: str = Field(min_length=1, max_length=50, description="Modelo del vehiculo")
    año: int = Field(ge=1900, le=datetime.now().year, description="Año de fabricacion")
    numero_chasis: str = Field(min_length=5, max_length=30, description="Numero unico de chasis")

    @field_validator('numero_chasis')
    @classmethod
    def validar_chasis(cls, valor: str) -> str:
        if not re.match(r'^[A-Za-z0-9]+$', valor):
            raise ValueError('El numero de chasis debe ser alfanumerico')
        return valor.upper()

    @field_validator('marca', 'modelo')
    @classmethod
    def limpiar_texto(cls, valor: str) -> str:
        return valor.strip().title()


class VentaBase(SQLModel):
    nombre_comprador: str = Field(min_length=2, max_length=100, description="Nombre del comprador")
    precio: float = Field(gt=0, description="Precio de venta")
    fecha_venta: datetime = Field(description="Fecha y hora de la venta")
    auto_id: int = Field(foreign_key="auto.id", description="ID del auto vendido")

    @field_validator('precio')
    @classmethod
    def validar_precio(cls, valor: float) -> float:
        if valor <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return round(valor, 2)

    @field_validator('fecha_venta')
    @classmethod
    def validar_fecha(cls, valor: datetime) -> datetime:
        if valor > datetime.now():
            raise ValueError('La fecha de venta no puede ser futura')
        return valor

    @field_validator('nombre_comprador')
    @classmethod
    def limpiar_nombre(cls, valor: str) -> str:
        nombre_normalizado = valor.strip()
        if not nombre_normalizado:
            raise ValueError('El nombre del comprador no puede estar vacio')
        return nombre_normalizado.title()


class Auto(AutoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ventas: List["Venta"] = Relationship(back_populates="auto")


class Venta(VentaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    auto: Optional[Auto] = Relationship(back_populates="ventas")


class AutoCreate(AutoBase):
    pass


class AutoUpdate(SQLModel):
    marca: Optional[str] = Field(None, min_length=1, max_length=50)
    modelo: Optional[str] = Field(None, min_length=1, max_length=50)
    año: Optional[int] = Field(None, ge=1900, le=datetime.now().year)
    numero_chasis: Optional[str] = Field(None, min_length=5, max_length=30)

    @field_validator('numero_chasis')
    @classmethod
    def validar_chasis(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None:
            if not re.match(r'^[A-Za-z0-9]+$', valor):
                raise ValueError('El numero de chasis debe ser alfanumerico')
            return valor.upper()
        return valor

    @field_validator('marca', 'modelo')
    @classmethod
    def limpiar_texto(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None:
            return valor.strip().title()
        return valor


class VentaCreate(VentaBase):
    pass


class VentaUpdate(SQLModel):
    nombre_comprador: Optional[str] = Field(None, min_length=2, max_length=100)
    precio: Optional[float] = Field(None, gt=0)
    fecha_venta: Optional[datetime] = None
    auto_id: Optional[int] = None

    @field_validator('precio')
    @classmethod
    def validar_precio(cls, valor: Optional[float]) -> Optional[float]:
        if valor is not None:
            if valor <= 0:
                raise ValueError('El precio debe ser mayor a 0')
            return round(valor, 2)
        return valor

    @field_validator('fecha_venta')
    @classmethod
    def validar_fecha(cls, valor: Optional[datetime]) -> Optional[datetime]:
        if valor is not None and valor > datetime.now():
            raise ValueError('La fecha de venta no puede ser futura')
        return valor

    @field_validator('nombre_comprador')
    @classmethod
    def limpiar_nombre(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None:
            nombre_normalizado = valor.strip()
            if not nombre_normalizado:
                raise ValueError('El nombre del comprador no puede estar vacio')
            return nombre_normalizado.title()
        return valor


class AutoResponse(AutoBase):
    id: int


class AutoResponseWithVentas(AutoResponse):
    ventas: List["VentaResponse"] = []


class VentaResponse(VentaBase):
    id: int


class VentaResponseWithAuto(VentaResponse):
    auto: Optional[AutoResponse] = None


class AutoSearchParams(SQLModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año_min: Optional[int] = Field(None, ge=1900)
    año_max: Optional[int] = Field(None, le=datetime.now().year)


class VentaSearchParams(SQLModel):
    nombre_comprador: Optional[str] = None
    precio_min: Optional[float] = Field(None, gt=0)
    precio_max: Optional[float] = Field(None, gt=0)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    auto_id: Optional[int] = None

    @field_validator('precio_min', 'precio_max')
    @classmethod
    def validar_precios(cls, valor: Optional[float]) -> Optional[float]:
        if valor is not None and valor <= 0:
            raise ValueError('Los precios deben ser mayores a 0')
        return valor


class PaginationParams(SQLModel):
    skip: int = Field(default=0, ge=0, description="Registros a omitir")
    limit: int = Field(default=10, ge=1, le=100, description="Maximo de registros")


class PaginatedResponse(SQLModel):
    total: int = Field(description="Total de registros")
    skip: int = Field(description="Registros omitidos")
    limit: int = Field(description="Limite por pagina")
    has_next: bool = Field(description="Indica si hay mas paginas")


class PaginatedAutosResponse(PaginatedResponse):
    items: List[AutoResponse] = []


class PaginatedVentasResponse(PaginatedResponse):
    items: List[VentaResponse] = []
