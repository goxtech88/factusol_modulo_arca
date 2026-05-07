"""
Router de Notas de Credito.

Expone un modulo dedicado para listar, buscar y emitir Notas de Credito (NC)
asociadas a facturas previamente validadas en ARCA. Las NC se persisten en
la misma tabla `cae_logs` con tipo_comprobante en (3, 8, 13) y referencian
a la factura original mediante cmp_asoc_tipo/pv/nro + motivo.
"""
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.cae_log import CAELog
from app.models.user import User, UserPuntoVenta
from app.services import arca_service, factusol_service

router = APIRouter(prefix="/api/credit-notes", tags=["credit-notes"])


NC_TIPOS = [3, 8, 13]          # NC A, NC B, NC C
FAC_TIPOS = [1, 6, 11]         # Factura A, B, C

_TIPO_NOMBRE = {
    1: "Factura A", 6: "Factura B", 11: "Factura C",
    3: "NC A", 8: "NC B", 13: "NC C",
}

_MOTIVOS_VALIDOS = {
    "Devolucion",
    "Descuento",
    "Anulacion",
    "Error de facturacion",
}


class CreditNoteCreate(BaseModel):
    cae_log_id_original: int
    motivo: str
    punto_venta: int
    importe: Optional[float] = None  # None = NC total


def _serialize(log: CAELog) -> dict:
    return {
        "id": log.id,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "tipo_comprobante": log.tipo_comprobante,
        "tipo_nombre": _TIPO_NOMBRE.get(log.tipo_comprobante, f"Tipo {log.tipo_comprobante}"),
        "punto_venta": log.punto_venta,
        "voucher_number": log.voucher_number,
        "cae": log.cae,
        "cae_vto": log.cae_vto,
        "imp_total": log.imp_total,
        "imp_neto": log.imp_neto,
        "imp_iva": log.imp_iva,
        "cliente_nombre": log.cliente_nombre,
        "cliente_doc": log.cliente_doc,
        "motivo": log.motivo,
        "cmp_asoc_tipo": log.cmp_asoc_tipo,
        "cmp_asoc_pv": log.cmp_asoc_pv,
        "cmp_asoc_nro": log.cmp_asoc_nro,
        "tipfac": log.tipfac,
        "codfac": log.codfac,
    }


@router.get("/")
def list_credit_notes(
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    cliente: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista las NC emitidas. Filtros opcionales por rango de fechas y cliente."""
    try:
        q = db.query(CAELog).filter(CAELog.tipo_comprobante.in_(NC_TIPOS))
        if current_user.role != "admin":
            q = q.filter(CAELog.user_id == current_user.id)

        if from_:
            try:
                d_from = datetime.fromisoformat(from_)
                q = q.filter(CAELog.created_at >= d_from)
            except ValueError:
                raise HTTPException(status_code=400, detail="Parametro 'from' invalido (use YYYY-MM-DD)")
        if to:
            try:
                # incluir el dia completo
                d_to = datetime.fromisoformat(to)
                d_to = datetime(d_to.year, d_to.month, d_to.day, 23, 59, 59)
                q = q.filter(CAELog.created_at <= d_to)
            except ValueError:
                raise HTTPException(status_code=400, detail="Parametro 'to' invalido (use YYYY-MM-DD)")
        if cliente:
            like = f"%{cliente}%"
            q = q.filter(CAELog.cliente_nombre.ilike(like))

        logs = q.order_by(CAELog.created_at.desc()).limit(500).all()
        return [_serialize(l) for l in logs]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar NC: {str(e)}")


@router.get("/search-invoice")
def search_original_invoice(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Busca facturas originales (tipo 1/6/11) por numero de comprobante o cliente.

    Utilizado por el modal de emision de NC para seleccionar el comprobante a anular.
    """
    try:
        query = db.query(CAELog).filter(CAELog.tipo_comprobante.in_(FAC_TIPOS))
        if current_user.role != "admin":
            query = query.filter(CAELog.user_id == current_user.id)

        like = f"%{q}%"
        # Buscar por voucher_number (como string) o por nombre de cliente
        try:
            n = int(q)
            query = query.filter(
                (CAELog.voucher_number == n) | (CAELog.cliente_nombre.ilike(like))
            )
        except ValueError:
            query = query.filter(CAELog.cliente_nombre.ilike(like))

        # Excluir facturas que ya tengan una NC emitida con mismo tipfac/codfac
        results = query.order_by(CAELog.created_at.desc()).limit(30).all()

        # Marcar si ya tiene NC
        output = []
        for log in results:
            existing_nc = db.query(CAELog).filter(
                CAELog.tipfac == log.tipfac,
                CAELog.codfac == log.codfac,
                CAELog.tipo_comprobante.in_(NC_TIPOS),
            ).first()
            data = _serialize(log)
            data["has_nc"] = existing_nc is not None
            output.append(data)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar facturas: {str(e)}")


@router.post("/")
def create_credit_note(
    payload: CreditNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Emite una NC (total o parcial) asociada a una factura original existente."""
    if payload.motivo not in _MOTIVOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Motivo invalido. Valores permitidos: {', '.join(sorted(_MOTIVOS_VALIDOS))}",
        )

    cae_original = db.query(CAELog).filter(CAELog.id == payload.cae_log_id_original).first()
    if not cae_original:
        raise HTTPException(status_code=404, detail="Factura original no encontrada")

    if current_user.role != "admin" and cae_original.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta factura")

    if cae_original.tipo_comprobante not in FAC_TIPOS:
        raise HTTPException(status_code=400, detail="Solo se puede emitir NC sobre Factura A/B/C")

    # Verificar que no tenga ya una NC
    existing_nc = db.query(CAELog).filter(
        CAELog.tipfac == cae_original.tipfac,
        CAELog.codfac == cae_original.codfac,
        CAELog.tipo_comprobante.in_(NC_TIPOS),
    ).first()
    if existing_nc:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe una NC ({_TIPO_NOMBRE.get(existing_nc.tipo_comprobante, 'NC')} nro {existing_nc.voucher_number}) para esta factura",
        )

    # Validar punto de venta pertenece al usuario
    pv_config = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.user_id == current_user.id,
        UserPuntoVenta.punto_venta == payload.punto_venta,
    ).first()
    if not pv_config:
        raise HTTPException(status_code=400, detail="El punto de venta no esta configurado para el usuario")

    # Leer detalle original desde Factusol
    try:
        detail = factusol_service.get_invoice_detail(cae_original.tipfac, cae_original.codfac)
        if not detail:
            raise HTTPException(status_code=404, detail="Factura no encontrada en Factusol")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer Factusol: {str(e)}")

    # Emitir NC en ARCA
    try:
        result = arca_service.validate_credit_note(
            invoice_header=detail["header"],
            invoice_lines=detail["lines"],
            cliente=detail["cliente"],
            punto_venta=payload.punto_venta,
            tipo_comprobante_original=cae_original.tipo_comprobante,
            voucher_number_original=cae_original.voucher_number,
            punto_venta_original=cae_original.punto_venta,
            importe_override=payload.importe,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en ARCA al emitir NC: {str(e)}")

    tipo_nc = result.get("tipo_nc", arca_service.tipo_factura_to_nota_credito(cae_original.tipo_comprobante))

    # Calcular montos guardados (si NC parcial, usar el override)
    imp_total_orig = float(detail["header"].get("TOTFAC") or 0)
    imp_neto_orig = sum(float(detail["header"].get(f"BAS{i}FAC") or 0) for i in range(1, 5))
    imp_iva_orig = sum(float(detail["header"].get(f"IIVA{i}FAC") or 0) for i in range(1, 5))
    if payload.importe and imp_total_orig > 0 and payload.importe < imp_total_orig:
        factor = payload.importe / imp_total_orig
        imp_total_nc = round(payload.importe, 2)
        imp_neto_nc = round(imp_neto_orig * factor, 2)
        imp_iva_nc = round(imp_iva_orig * factor, 2)
    else:
        imp_total_nc = imp_total_orig
        imp_neto_nc = imp_neto_orig
        imp_iva_nc = imp_iva_orig

    nc_log = CAELog(
        user_id=current_user.id,
        tipfac=cae_original.tipfac,
        codfac=cae_original.codfac,
        punto_venta=payload.punto_venta,
        tipo_comprobante=tipo_nc,
        voucher_number=result.get("voucher_number", 0),
        cae=result.get("CAE", ""),
        cae_vto=result.get("CAEFchVto", ""),
        imp_total=imp_total_nc,
        imp_neto=imp_neto_nc,
        imp_iva=imp_iva_nc,
        cliente_nombre=detail["header"].get("CNOFAC"),
        cliente_doc=(detail.get("cliente") or {}).get("NIFCLI"),
        motivo=payload.motivo,
        cmp_asoc_tipo=cae_original.tipo_comprobante,
        cmp_asoc_pv=cae_original.punto_venta,
        cmp_asoc_nro=cae_original.voucher_number,
    )
    db.add(nc_log)
    db.commit()
    db.refresh(nc_log)

    return {
        "status": "ok",
        "message": f"{_TIPO_NOMBRE.get(tipo_nc, 'NC')} emitida exitosamente",
        "nc": _serialize(nc_log),
    }
