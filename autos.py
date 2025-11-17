from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from database import get_session
from repository import get_auto_repository, AutoRepositoryInterface
from models import (
    Auto, AutoCreate, AutoUpdate, AutoResponse, AutoResponseWithVentas,
    AutoSearchParams, PaginationParams, PaginatedAutosResponse
)


def obtener_repositorio_auto(db_session: Session = Depends(get_session)) -> AutoRepositoryInterface:
    """Crea una instancia del repositorio de autos"""
    return get_auto_repository(db_session)


router = APIRouter(
    prefix="/autos",
    tags=["autos"],
    responses={404: {"description": "Auto no encontrado"}}
)


@router.post("/", response_model=AutoResponse, status_code=status.HTTP_201_CREATED)
async def crear_auto(
    nuevo_auto: AutoCreate,
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Crea un nuevo vehiculo en el inventario"""
    try:
        vehiculo_creado = repo.create(nuevo_auto)
        return AutoResponse.model_validate(vehiculo_creado)
    except Exception as error:
        mensaje_error = str(error).lower()
        if "chasis" in mensaje_error or "unique" in mensaje_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El numero de chasis ya existe: {nuevo_auto.numero_chasis}"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear auto: {str(error)}"
        )


@router.get("/", response_model=PaginatedAutosResponse)
async def listar_autos(
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Maximo de registros a retornar")
):
    """Lista todos los autos con paginacion"""
    try:
        lista_autos = repo.get_all(skip=skip, limit=limit)
        total_registros = repo.count_all()
        
        return PaginatedAutosResponse(
            items=[AutoResponse.model_validate(auto) for auto in lista_autos],
            total=total_registros,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total_registros
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener autos: {str(error)}"
        )


@router.get("/{auto_id}", response_model=AutoResponse)
async def obtener_auto(
    auto_id: int,
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Obtiene un auto especifico por su identificador"""
    try:
        vehiculo = repo.get_by_id(auto_id)
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Auto con ID {auto_id} no encontrado"
            )
        return AutoResponse.model_validate(vehiculo)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener auto: {str(error)}"
        )


@router.put("/{auto_id}", response_model=AutoResponse)
async def actualizar_auto(
    auto_id: int,
    datos_actualizacion: AutoUpdate,
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Actualiza los datos de un auto existente"""
    try:
        vehiculo_actualizado = repo.update(auto_id, datos_actualizacion)
        if not vehiculo_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Auto con ID {auto_id} no encontrado"
            )
        return AutoResponse.model_validate(vehiculo_actualizado)
    except HTTPException:
        raise
    except Exception as error:
        mensaje_error = str(error).lower()
        if "chasis" in mensaje_error or "unique" in mensaje_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El numero de chasis ya existe"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar auto: {str(error)}"
        )


@router.delete("/{auto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_auto(
    auto_id: int,
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Elimina un auto del inventario"""
    try:
        eliminado = repo.delete(auto_id)
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Auto con ID {auto_id} no encontrado"
            )
    except HTTPException:
        raise
    except Exception as error:
        mensaje_error = str(error).lower()
        if "venta" in mensaje_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el auto porque tiene ventas asociadas"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar auto: {str(error)}"
        )


@router.get("/chasis/{numero_chasis}", response_model=AutoResponse)
async def buscar_por_chasis(
    numero_chasis: str,
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Busca un auto por su numero de chasis"""
    try:
        vehiculo = repo.get_by_chasis(numero_chasis)
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Auto con numero de chasis '{numero_chasis}' no encontrado"
            )
        return AutoResponse.model_validate(vehiculo)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar auto: {str(error)}"
        )


@router.get("/{auto_id}/with-ventas", response_model=AutoResponseWithVentas)
async def obtener_auto_con_ventas(
    auto_id: int,
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Obtiene un auto junto con todas sus ventas asociadas"""
    try:
        vehiculo = repo.get_with_ventas(auto_id)
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Auto con ID {auto_id} no encontrado"
            )
        return AutoResponseWithVentas.model_validate(vehiculo)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener auto con ventas: {str(error)}"
        )


@router.get("/search/", response_model=PaginatedAutosResponse)
async def buscar_autos(
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto),
    marca: Optional[str] = Query(None, description="Filtrar por marca"),
    modelo: Optional[str] = Query(None, description="Filtrar por modelo"),
    año_min: Optional[int] = Query(None, ge=1900, description="Año minimo"),
    año_max: Optional[int] = Query(None, le=datetime.now().year, description="Año maximo"),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Maximo de registros")
):
    """Busca autos aplicando filtros avanzados"""
    try:
        filtros = AutoSearchParams(
            marca=marca,
            modelo=modelo,
            año_min=año_min,
            año_max=año_max
        )
        
        resultados = repo.search(filtros, skip=skip, limit=limit)
        todos_filtrados = repo.search(filtros, skip=0, limit=1000)
        total = len(todos_filtrados)
        
        return PaginatedAutosResponse(
            items=[AutoResponse.model_validate(auto) for auto in resultados],
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar autos: {str(error)}"
        )


@router.get("/stats/summary")
async def obtener_estadisticas_autos(
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Genera estadisticas generales sobre los autos registrados"""
    try:
        total = repo.count_all()
        todos_los_autos = repo.get_all(skip=0, limit=1000)
        
        conteo_marcas = {}
        conteo_años = {}
        
        for vehiculo in todos_los_autos:
            if vehiculo.marca in conteo_marcas:
                conteo_marcas[vehiculo.marca] += 1
            else:
                conteo_marcas[vehiculo.marca] = 1
            
            if vehiculo.año in conteo_años:
                conteo_años[vehiculo.año] += 1
            else:
                conteo_años[vehiculo.año] = 1
        
        marca_popular = max(conteo_marcas.items(), key=lambda x: x[1])[0] if conteo_marcas else None
        año_comun = max(conteo_años.items(), key=lambda x: x[1])[0] if conteo_años else None
        
        return {
            "total_autos": total,
            "distribucion_marcas": conteo_marcas,
            "distribucion_años": conteo_años,
            "marca_mas_popular": marca_popular,
            "año_mas_comun": año_comun
        }
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadisticas: {str(error)}"
        )


@router.get("/validate/chasis/{numero_chasis}")
async def validar_chasis_disponible(
    numero_chasis: str,
    db_session: Session = Depends(get_session),
    repo: AutoRepositoryInterface = Depends(obtener_repositorio_auto)
):
    """Verifica si un numero de chasis esta disponible"""
    try:
        auto_existente = repo.get_by_chasis(numero_chasis)
        
        return {
            "numero_chasis": numero_chasis.upper(),
            "disponible": auto_existente is None,
            "auto_existente": AutoResponse.model_validate(auto_existente) if auto_existente else None
        }
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar chasis: {str(error)}"
        )
