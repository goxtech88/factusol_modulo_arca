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


_NC_LETRA = {3: "A", 8: "B", 13: "C"}

# Condicion frente al IVA del receptor segun CFECLI de Factusol.
_CFECLI_COND = {
    0: "", 1: "Consumidor Final", 2: "Responsable Inscripto",
    3: "Monotributista", 4: "Exento", 5: "No Responsable",
}


def _doc_receptor(doc_raw: str):
    """Calcula (tipo_doc AFIP, nro_doc) a partir del NIF/CUIT/DNI del cliente."""
    s = str(doc_raw or "").replace("-", "").strip()
    if not s or not s.isdigit():
        return 99, 0          # sin identificar
    if len(s) < 11:
        return 96, int(s)     # DNI
    return 80, int(s)         # CUIT


@router.get("/{nc_id}/comprobante")
def get_nc_comprobante(
    nc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Devuelve los datos fiscales minimos de una NC para imprimir su PDF, y
    genera el QR AFIP del comprobante. El QR se guarda con un nombre propio
    (`nc-<pv>-<nro>.png`) para no pisar el QR de la factura original.
    """
    from app.config import get_config

    nc = db.query(CAELog).filter(CAELog.id == nc_id).first()
    if not nc or nc.tipo_comprobante not in NC_TIPOS:
        raise HTTPException(status_code=404, detail="Nota de credito no encontrada")
    if current_user.role != "admin" and nc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta NC")

    # ── Comprobante asociado (la factura que anula la NC) ────────────────────
    # Usamos los campos cmp_asoc si estan guardados; si no (NC viejas creadas por
    # el boton inline que no los guardaba), los reconstruimos buscando la factura
    # original: comparte tipfac/codfac con la NC y es de tipo no-NC.
    asoc_tipo = nc.cmp_asoc_tipo
    asoc_pv = nc.cmp_asoc_pv
    asoc_nro = nc.cmp_asoc_nro
    if not asoc_nro:
        orig = (
            db.query(CAELog)
            .filter(
                CAELog.tipfac == nc.tipfac,
                CAELog.codfac == nc.codfac,
                CAELog.tipo_comprobante.notin_(NC_TIPOS),
            )
            .order_by(CAELog.created_at.asc())
            .first()
        )
        if orig:
            asoc_tipo = orig.tipo_comprobante
            asoc_pv = orig.punto_venta
            asoc_nro = orig.voucher_number

    empresa = get_config().get("empresa", {}) or {}
    cuit_emisor = str(empresa.get("cuit", "")).replace("-", "").strip()

    tipo_doc, nro_doc = _doc_receptor(nc.cliente_doc)

    fecha_dt = nc.created_at or datetime.now()
    fecha_str = fecha_dt.strftime("%Y-%m-%d")

    # Generar QR AFIP del comprobante (nombre propio para no pisar el de la factura)
    qr_filename = f"nc-{nc.punto_venta}-{nc.voucher_number}.png"
    qr_url = ""
    try:
        path = arca_service.generate_afip_qr(
            cuit_emisor=cuit_emisor,
            punto_venta=nc.punto_venta,
            voucher_number=nc.voucher_number,
            fecha_cbte=fecha_str,
            tipo_comprobante=nc.tipo_comprobante,
            tipo_doc_receptor=tipo_doc,
            nro_doc_receptor=nro_doc,
            imp_total=float(nc.imp_total or 0),
            cae=nc.cae or "",
            cae_vto=nc.cae_vto or "",
            tipfac=nc.tipfac,
            codfac=nc.codfac,
            filename=qr_filename,
        )
        if path:
            qr_url = f"/static/qr/{qr_filename}"
    except Exception:
        qr_url = ""

    # Enriquecer datos del receptor desde Factusol (condicion IVA + domicilio).
    # Si Factusol no esta disponible, seguimos con lo que hay en el log.
    cliente_cond = ""
    cliente_dom = ""
    try:
        detail = factusol_service.get_invoice_detail(nc.tipfac, nc.codfac)
        cli = (detail or {}).get("cliente") or {}
        cliente_cond = _CFECLI_COND.get(cli.get("CFECLI"), "")
        dom_parts = [cli.get("DOMCLI") or "", cli.get("POBCLI") or "", cli.get("PROCLI") or ""]
        cliente_dom = ", ".join(p for p in dom_parts if p)
    except Exception:
        pass

    return {
        "id": nc.id,
        "tipo_comprobante": nc.tipo_comprobante,
        "tipo_nombre": _TIPO_NOMBRE.get(nc.tipo_comprobante, "Nota de Credito"),
        "letra": _NC_LETRA.get(nc.tipo_comprobante, ""),
        "codigo_afip": nc.tipo_comprobante,
        "punto_venta": nc.punto_venta,
        "voucher_number": nc.voucher_number,
        "comprobante_nro": f"{str(nc.punto_venta).zfill(4)}-{str(nc.voucher_number).zfill(8)}",
        "fecha": fecha_str,
        "cae": nc.cae,
        "cae_vto": nc.cae_vto,
        "imp_neto": nc.imp_neto,
        "imp_iva": nc.imp_iva,
        "imp_total": nc.imp_total,
        "motivo": nc.motivo,
        # Numero de factura en Factusol (serie-numero): siempre disponible, es lo
        # que el usuario reconoce como "la factura" en su Factusol.
        "factura_origen": f"{nc.tipfac}-{nc.codfac}",
        "cmp_asoc": {
            "tipo": asoc_tipo,
            "tipo_nombre": _TIPO_NOMBRE.get(asoc_tipo, "Factura") if asoc_tipo else "",
            "nro_fmt": (
                f"{str(asoc_pv or 0).zfill(4)}-{str(asoc_nro or 0).zfill(8)}"
                if asoc_nro else ""
            ),
        },
        "cliente": {
            "nombre": nc.cliente_nombre,
            "doc": nc.cliente_doc,
            "tipo_doc": tipo_doc,
            "condicion_iva": cliente_cond,
            "domicilio": cliente_dom,
        },
        "emisor": {
            "razon_social": empresa.get("razon_social", ""),
            "cuit": cuit_emisor,
            "domicilio": empresa.get("domicilio", ""),
            "condicion_iva": empresa.get("condicion_iva", ""),
            "inicio_actividades": empresa.get("inicio_actividades", ""),
        },
        "qr_url": qr_url,
    }


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
