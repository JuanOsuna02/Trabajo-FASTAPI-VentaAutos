from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from database import get_session
from repository import get_venta_repository, VentaRepositoryInterface
from models import (
    Venta, VentaCreate, VentaUpdate, VentaResponse, VentaResponseWithAuto,
    VentaSearchParams, PaginationParams, PaginatedVentasResponse
)


def obtener_repositorio_venta(db_session: Session = Depends(get_session)) -> VentaRepositoryInterface:
    """Crea una instancia del repositorio de ventas"""
    return get_venta_repository(db_session)


router = APIRouter(
    prefix="/ventas",
    tags=["ventas"],
    responses={404: {"description": "Venta no encontrada"}}
)


@router.post("/", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
async def crear_venta(
    nueva_venta: VentaCreate,
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Registra una nueva venta en el sistema"""
    try:
        venta_creada = repo.create(nueva_venta)
        return VentaResponse.model_validate(venta_creada)
    except Exception as error:
        mensaje_error = str(error).lower()
        if "auto" in mensaje_error and "existe" in mensaje_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El auto con ID {nueva_venta.auto_id} no existe"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear venta: {str(error)}"
        )


@router.get("/", response_model=PaginatedVentasResponse)
async def listar_ventas(
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Maximo de registros a retornar")
):
    """Lista todas las ventas con paginacion"""
    try:
        lista_ventas = repo.get_all(skip=skip, limit=limit)
        total_registros = repo.count_all()
        
        return PaginatedVentasResponse(
            items=[VentaResponse.model_validate(venta) for venta in lista_ventas],
            total=total_registros,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total_registros
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ventas: {str(error)}"
        )


@router.get("/{venta_id}", response_model=VentaResponse)
async def obtener_venta(
    venta_id: int,
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Obtiene una venta especifica por su identificador"""
    try:
        venta = repo.get_by_id(venta_id)
        if not venta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {venta_id} no encontrada"
            )
        return VentaResponse.model_validate(venta)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener venta: {str(error)}"
        )


@router.put("/{venta_id}", response_model=VentaResponse)
async def actualizar_venta(
    venta_id: int,
    datos_actualizacion: VentaUpdate,
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Actualiza los datos de una venta existente"""
    try:
        venta_actualizada = repo.update(venta_id, datos_actualizacion)
        if not venta_actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {venta_id} no encontrada"
            )
        return VentaResponse.model_validate(venta_actualizada)
    except HTTPException:
        raise
    except Exception as error:
        mensaje_error = str(error).lower()
        if "auto" in mensaje_error and "existe" in mensaje_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El auto especificado no existe"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar venta: {str(error)}"
        )


@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_venta(
    venta_id: int,
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Elimina una venta del sistema"""
    try:
        eliminado = repo.delete(venta_id)
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {venta_id} no encontrada"
            )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar venta: {str(error)}"
        )


@router.get("/auto/{auto_id}", response_model=List[VentaResponse])
async def obtener_ventas_por_auto(
    auto_id: int,
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Obtiene todas las ventas de un auto especifico"""
    try:
        ventas = repo.get_by_auto_id(auto_id)
        return [VentaResponse.model_validate(venta) for venta in ventas]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ventas del auto: {str(error)}"
        )


@router.get("/comprador/{nombre}", response_model=List[VentaResponse])
async def obtener_ventas_por_comprador(
    nombre: str,
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Obtiene todas las ventas de un comprador especifico"""
    try:
        ventas = repo.get_by_comprador(nombre)
        return [VentaResponse.model_validate(venta) for venta in ventas]
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ventas del comprador: {str(error)}"
        )


@router.get("/{venta_id}/with-auto", response_model=VentaResponseWithAuto)
async def obtener_venta_con_auto(
    venta_id: int,
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Obtiene una venta junto con la informacion del auto asociado"""
    try:
        venta = repo.get_with_auto(venta_id)
        if not venta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {venta_id} no encontrada"
            )
        return VentaResponseWithAuto.model_validate(venta)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener venta con auto: {str(error)}"
        )


@router.get("/search/", response_model=PaginatedVentasResponse)
async def buscar_ventas(
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta),
    nombre_comprador: Optional[str] = Query(None, description="Filtrar por nombre del comprador"),
    precio_min: Optional[float] = Query(None, gt=0, description="Precio minimo"),
    precio_max: Optional[float] = Query(None, gt=0, description="Precio maximo"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin"),
    auto_id: Optional[int] = Query(None, description="Filtrar por ID de auto"),
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Maximo de registros")
):
    """Busca ventas aplicando filtros avanzados"""
    try:
        if precio_min and precio_max and precio_min > precio_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio minimo no puede ser mayor al precio maximo"
            )
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin"
            )
        
        filtros = VentaSearchParams(
            nombre_comprador=nombre_comprador,
            precio_min=precio_min,
            precio_max=precio_max,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            auto_id=auto_id
        )
        
        resultados = repo.search(filtros, skip=skip, limit=limit)
        todos_filtrados = repo.search(filtros, skip=0, limit=1000)
        total = len(todos_filtrados)
        
        return PaginatedVentasResponse(
            items=[VentaResponse.model_validate(venta) for venta in resultados],
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar ventas: {str(error)}"
        )


@router.get("/stats/summary")
async def obtener_estadisticas_ventas(
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta)
):
    """Genera estadisticas generales sobre las ventas"""
    try:
        estadisticas = repo.get_sales_statistics()
        return estadisticas
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadisticas: {str(error)}"
        )


@router.get("/stats/monthly")
async def obtener_estadisticas_mensuales(
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta),
    año: Optional[int] = Query(None, ge=2000, le=2030, description="Año para filtrar")
):
    """Obtiene estadisticas de ventas agrupadas por mes"""
    try:
        filtros = VentaSearchParams()
        if año:
            filtros.fecha_inicio = datetime(año, 1, 1)
            filtros.fecha_fin = datetime(año, 12, 31, 23, 59, 59)
        
        ventas = repo.search(filtros, skip=0, limit=10000)
        
        estadisticas_mensuales = {}
        for venta in ventas:
            clave_mes = f"{venta.fecha_venta.year}-{venta.fecha_venta.month:02d}"
            if clave_mes not in estadisticas_mensuales:
                estadisticas_mensuales[clave_mes] = {
                    "año": venta.fecha_venta.year,
                    "mes": venta.fecha_venta.month,
                    "total_ventas": 0,
                    "total_ingresos": 0.0
                }
            
            estadisticas_mensuales[clave_mes]["total_ventas"] += 1
            estadisticas_mensuales[clave_mes]["total_ingresos"] += float(venta.precio)
        
        resultado = list(estadisticas_mensuales.values())
        resultado.sort(key=lambda x: (x["año"], x["mes"]))
        
        return {
            "año_filtro": año,
            "estadisticas_mensuales": resultado,
            "total_meses": len(resultado)
        }
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadisticas mensuales: {str(error)}"
        )


@router.get("/reports/top-buyers")
async def obtener_mejores_compradores(
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta),
    limit: int = Query(10, ge=1, le=50, description="Numero de compradores a retornar")
):
    """Obtiene los compradores que mas han gastado"""
    try:
        todas_las_ventas = repo.get_all(skip=0, limit=10000)
        
        compradores = {}
        for venta in todas_las_ventas:
            nombre = venta.nombre_comprador
            if nombre not in compradores:
                compradores[nombre] = {
                    "nombre_comprador": nombre,
                    "total_compras": 0,
                    "total_gastado": 0.0,
                    "precio_promedio": 0.0
                }
            
            compradores[nombre]["total_compras"] += 1
            compradores[nombre]["total_gastado"] += float(venta.precio)
        
        for stats in compradores.values():
            stats["precio_promedio"] = stats["total_gastado"] / stats["total_compras"]
        
        mejores = sorted(
            compradores.values(),
            key=lambda x: x["total_gastado"],
            reverse=True
        )[:limit]
        
        return {
            "mejores_compradores": mejores,
            "total_compradores_unicos": len(compradores)
        }
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mejores compradores: {str(error)}"
        )


@router.get("/reports/recent")
async def obtener_ventas_recientes(
    db_session: Session = Depends(get_session),
    repo: VentaRepositoryInterface = Depends(obtener_repositorio_venta),
    days: int = Query(7, ge=1, le=365, description="Numero de dias hacia atras")
):
    """Obtiene ventas recientes de los ultimos N dias"""
    try:
        fecha_limite = datetime.now() - timedelta(days=days)
        
        filtros = VentaSearchParams(
            fecha_inicio=fecha_limite
        )
        
        ventas_recientes = repo.search(filtros, skip=0, limit=1000)
        
        return {
            "periodo_dias": days,
            "fecha_desde": fecha_limite,
            "total_ventas": len(ventas_recientes),
            "ventas": [VentaResponse.model_validate(venta) for venta in ventas_recientes]
        }
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ventas recientes: {str(error)}"
        )
