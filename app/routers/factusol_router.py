"""
Router para lectura de datos de Factusol.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from app.auth import get_current_user
from app.models.user import User
from app.services import factusol_service

router = APIRouter(prefix="/api/factusol", tags=["factusol"])


@router.get("/invoices")
def list_invoices(
    serie: int = Query(..., description="Serie/TIPFAC de Factusol"),
    search: str = Query("", description="Buscar por nombre de cliente o nro"),
    date_filter: str = Query("all", description="Filtro fecha: all|today|yesterday|last7"),
    current_user: User = Depends(get_current_user),
):
    """Lista facturas de una serie. El usuario solo puede ver las series asignadas."""
    allowed_series = [pv.serie_factusol for pv in current_user.puntos_venta]
    if current_user.role != "admin" and serie not in allowed_series:
        raise HTTPException(status_code=403, detail="No tiene acceso a esta serie")

    try:
        invoices = factusol_service.get_invoices(serie, search=search, date_filter=date_filter)
        return {"invoices": invoices, "total": len(invoices)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer Factusol: {str(e)}")



@router.get("/invoices/{tipfac}/{codfac}")
def get_invoice_detail(
    tipfac: int,
    codfac: int,
    current_user: User = Depends(get_current_user),
):
    """Detalle completo de una factura: header + líneas + cliente."""
    allowed_series = [pv.serie_factusol for pv in current_user.puntos_venta]
    if current_user.role != "admin" and tipfac not in allowed_series:
        raise HTTPException(status_code=403, detail="No tiene acceso a esta serie")

    try:
        detail = factusol_service.get_invoice_detail(tipfac, codfac)
        if not detail:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer Factusol: {str(e)}")


@router.get("/customers")
def list_customers(
    search: str = Query(""),
    current_user: User = Depends(get_current_user),
):
    try:
        return factusol_service.get_customers(search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles")
def list_articles(
    search: str = Query(""),
    current_user: User = Depends(get_current_user),
):
    try:
        return factusol_service.get_articles(search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-connection")
def test_connection(current_user: User = Depends(get_current_user)):
    """Prueba la conexión a la base de datos Factusol."""
    return factusol_service.test_connection()
