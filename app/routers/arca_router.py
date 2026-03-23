"""
Router para validación de facturas en ARCA (AFIP).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User, UserPuntoVenta
from app.models.cae_log import CAELog
from app.services import factusol_service, arca_service

router = APIRouter(prefix="/api/arca", tags=["arca"])


@router.post("/validate/{tipfac}/{codfac}")
def validate_invoice(
    tipfac: int,
    codfac: int,
    pv_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Valida una factura de Factusol en ARCA y obtiene el CAE.
    pv_id: ID del punto de venta del usuario a utilizar.
    """
    # Buscar config de punto de venta
    if pv_id:
        pv_config = db.query(UserPuntoVenta).filter(
            UserPuntoVenta.id == pv_id,
            UserPuntoVenta.user_id == current_user.id,
        ).first()
    else:
        # Buscar automáticamente por la serie
        pv_config = db.query(UserPuntoVenta).filter(
            UserPuntoVenta.user_id == current_user.id,
            UserPuntoVenta.serie_factusol == tipfac,
        ).first()

    if not pv_config:
        raise HTTPException(
            status_code=400,
            detail="No tiene un punto de venta configurado para esta serie",
        )

    # Verificar que no esté ya validada
    existing = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
        CAELog.punto_venta == pv_config.punto_venta,
    ).first()
    if existing:
        return {
            "status": "already_validated",
            "cae": existing.cae,
            "cae_vto": existing.cae_vto,
            "voucher_number": existing.voucher_number,
            "message": "Esta factura ya fue validada en ARCA",
        }

    # Obtener datos de Factusol
    try:
        detail = factusol_service.get_invoice_detail(tipfac, codfac)
        if not detail:
            raise HTTPException(status_code=404, detail="Factura no encontrada en Factusol")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer Factusol: {str(e)}") 

    # Determinar tipo de comprobante
    from app.services.arca_service import determine_tipo_comprobante
    from app.config import get_config
    config = get_config()
    cond_emisor = config.get("empresa", {}).get("condicion_iva", "Responsable Inscripto")
    # CFECLI: 0=no config, 1=CF, 2=RI, 3=Mono, 4=Exento
    cfecli = detail.get("cliente", {}).get("CFECLI", 0) or 0

    # Si el PV tiene tipo_comprobante fijo (!=0), usarlo; sino calcular por CFECLI
    if pv_config.tipo_comprobante and pv_config.tipo_comprobante != 0:
        tipo_comprobante = pv_config.tipo_comprobante
    else:
        tipo_comprobante = determine_tipo_comprobante(cfecli, cond_emisor)



    # Verificar que no esté ya validada (con el tipo calculado)
    existing = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
        CAELog.punto_venta == pv_config.punto_venta,
    ).first()
    if existing:
        return {
            "status": "already_validated",
            "cae": existing.cae,
            "cae_vto": existing.cae_vto,
            "voucher_number": existing.voucher_number,
            "tipo_comprobante": existing.tipo_comprobante,
            "message": "Esta factura ya fue validada en ARCA",
        }

    # Mapear tipo de comprobante a nombre legible
    cbte_nombres = {1: "Factura A", 2: "ND A", 3: "NC A", 6: "Factura B", 7: "ND B",
                    8: "NC B", 11: "Factura C", 12: "ND C", 13: "NC C"}
    cbte_nombre = cbte_nombres.get(tipo_comprobante, f"Tipo {tipo_comprobante}")

    # Validar en ARCA
    try:
        result = arca_service.validate_invoice(
            invoice_header=detail["header"],
            invoice_lines=detail["lines"],
            cliente=detail["cliente"],
            punto_venta=pv_config.punto_venta,
            tipo_comprobante=tipo_comprobante,
        )
    except Exception as e:
        err_str = str(e)
        # Enriquecer error 10008 con contexto
        if "10008" in err_str:
            err_str += (
                f"\n\nDiagnostico: PV {pv_config.punto_venta} con {cbte_nombre} (tipo {tipo_comprobante})."
                f" Verifique en AFIP que el PV {pv_config.punto_venta} este habilitado para {cbte_nombre}."
                f" IVACLI cliente={raw_ivacli} -> {cbte_nombre}."
            )
        raise HTTPException(status_code=502, detail=f"Error en ARCA: {err_str}")

    # Guardar log
    cae_log = CAELog(
        user_id=current_user.id,
        tipfac=tipfac,
        codfac=codfac,
        punto_venta=pv_config.punto_venta,
        tipo_comprobante=tipo_comprobante,
        voucher_number=result.get("voucher_number", 0),
        cae=result.get("CAE", ""),
        cae_vto=result.get("CAEFchVto", ""),
        imp_total=detail["header"].get("TOTFAC"),
        cliente_nombre=detail["header"].get("CNOFAC"),
        cliente_doc=detail.get("cliente", {}).get("NIFCLI") if detail.get("cliente") else None,
    )
    db.add(cae_log)
    db.commit()

    # ── Generar QR AFIP ──────────────────────────────────────────────────
    from app.config import get_config
    _cfg = get_config()
    _cuit = str(_cfg.get("empresa", {}).get("cuit", "")).replace("-", "").strip()

    _voucher_data = arca_service.build_voucher_data(
        detail["header"], detail["lines"], detail["cliente"],
        pv_config.punto_venta, tipo_comprobante,
    )
    _fecha_raw = detail["header"].get("FECFAC", "")
    from datetime import datetime as _dt
    if hasattr(_fecha_raw, "strftime"):
        _fecha_str = _fecha_raw.strftime("%Y-%m-%d")
    elif isinstance(_fecha_raw, str) and len(_fecha_raw) >= 8:
        _fecha_str = _fecha_raw[:10]
    else:
        _fecha_str = _dt.now().strftime("%Y-%m-%d")

    qr_path = arca_service.generate_afip_qr(
        cuit_emisor=_cuit,
        punto_venta=pv_config.punto_venta,
        voucher_number=result.get("voucher_number", 0),
        fecha_cbte=_fecha_str,
        tipo_comprobante=tipo_comprobante,
        tipo_doc_receptor=_voucher_data["tipo_doc"],
        nro_doc_receptor=_voucher_data["nro_doc"],
        imp_total=_voucher_data["imp_total"],
        cae=result.get("CAE", ""),
        cae_vto=result.get("CAEFchVto", ""),
        tipfac=tipfac,
        codfac=codfac,
    )

    # ── Grabar datos CAE en F_FAC de Factusol ────────────────────────────
    # Formatear nro comprobante como Factusol: "A-0002-00006486"
    _letra_map = {1: "A", 6: "B", 11: "C", 2: "NDA", 3: "NCA", 7: "NDB", 8: "NCB"}
    _letra = _letra_map.get(tipo_comprobante, "X")
    _pv_str = str(pv_config.punto_venta).zfill(4)
    _cbte_str = str(result.get("voucher_number", 0)).zfill(8)
    _pedfac = f"{_letra}-{_pv_str}-{_cbte_str}"

    try:
        factusol_service.write_cae_to_factura(
            tipfac=tipfac,
            codfac=codfac,
            cae=result.get("CAE", ""),
            voucher_number=_pedfac,
            cae_vto=result.get("CAEFchVto", ""),
            qr_img_path=qr_path,
        )
    except Exception as _write_err:
        # No falla la respuesta si el write-back a Access falla
        print(f"⚠️ No se pudo grabar CAE en Factusol F_FAC: {_write_err}")


    return {
        "status": "ok",
        "cae": result.get("CAE"),
        "cae_vto": result.get("CAEFchVto"),
        "voucher_number": result.get("voucher_number"),
        "tipo_comprobante": tipo_comprobante,
        "resultado": result.get("resultado"),
        "qr_path": qr_path,
        "message": "Factura validada exitosamente en ARCA",
    }



@router.get("/status/{tipfac}/{codfac}")
def check_cae_status(
    tipfac: int,
    codfac: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifica si una factura ya tiene CAE asignado."""
    log = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
    ).first()

    if log:
        return {
            "validated": True,
            "cae": log.cae,
            "cae_vto": log.cae_vto,
            "voucher_number": log.voucher_number,
            "punto_venta": log.punto_venta,
            "tipo_comprobante": log.tipo_comprobante,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
    return {"validated": False}


@router.get("/logs")
def list_cae_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los CAE emitidos por el usuario actual."""
    if current_user.role == "admin":
        logs = db.query(CAELog).order_by(CAELog.created_at.desc()).limit(100).all()
    else:
        logs = db.query(CAELog).filter(
            CAELog.user_id == current_user.id
        ).order_by(CAELog.created_at.desc()).limit(100).all()

    return [
        {
            "id": l.id,
            "tipfac": l.tipfac,
            "codfac": l.codfac,
            "punto_venta": l.punto_venta,
            "tipo_comprobante": l.tipo_comprobante,
            "voucher_number": l.voucher_number,
            "cae": l.cae,
            "cae_vto": l.cae_vto,
            "imp_total": l.imp_total,
            "cliente_nombre": l.cliente_nombre,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


@router.get("/last-voucher/{pv_id}")
def get_last_voucher(
    pv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene el último número de comprobante en ARCA para un punto de venta."""
    pv = db.query(UserPuntoVenta).filter(
        UserPuntoVenta.id == pv_id,
        UserPuntoVenta.user_id == current_user.id,
    ).first()
    if not pv:
        raise HTTPException(status_code=404, detail="Punto de venta no encontrado")

    try:
        last = arca_service.get_last_voucher_number(pv.punto_venta, pv.tipo_comprobante)
        return {"punto_venta": pv.punto_venta, "tipo_comprobante": pv.tipo_comprobante, "last_voucher": last}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en ARCA: {str(e)}")


@router.get("/server-status")
def server_status(current_user: User = Depends(get_current_user)):
    """Verifica el estado detallado de los servidores ARCA (WSFEv1 Dummy)."""
    return arca_service.get_server_status()


@router.get("/server-monitor")
def server_monitor(current_user: User = Depends(get_current_user)):
    """
    Monitor completo: estado de servidores ARCA + último comprobante
    emitido por cada punto de venta configurado.
    """
    from datetime import datetime

    result = {
        "timestamp": datetime.now().isoformat(),
        "servers": {},
        "puntos_venta": [],
        "errors": [],
    }

    # 1) Estado de servidores WSFEv1
    try:
        status = arca_service.get_server_status()
        result["servers"] = status.get("detail", {})
        result["wsfe_ok"] = status.get("status") == "ok"
        if status.get("status") != "ok":
            result["errors"].append(status.get("message", "Error desconocido WSFEv1"))
    except Exception as e:
        result["wsfe_ok"] = False
        result["servers"] = {"AppServer": "N/D", "DbServer": "N/D", "AuthServer": "N/D"}
        result["errors"].append(f"WSFEv1: {str(e)}")

    # 2) Último comprobante por punto de venta del usuario
    for pv in current_user.puntos_venta:
        pv_info = {
            "nombre": pv.nombre,
            "punto_venta": pv.punto_venta,
            "serie_factusol": pv.serie_factusol,
            "tipo_comprobante": pv.tipo_comprobante,
            "ultimo_cbte": None,
            "error": None,
        }
        try:
            last = arca_service.get_last_voucher_number(pv.punto_venta, pv.tipo_comprobante)
            pv_info["ultimo_cbte"] = last
        except Exception as e:
            pv_info["error"] = str(e)
            result["errors"].append(f"PV {pv.punto_venta}: {str(e)}")

        result["puntos_venta"].append(pv_info)

    return result


@router.get("/padron/{cuit}")
def consultar_padron(
    cuit: str,
    current_user: User = Depends(get_current_user),
):
    """
    Consulta el Padrón ARCA (Alcance 4) para obtener datos fiscales de un CUIT.

    Retorna razón social, tipo persona, condición IVA y domicilio fiscal.
    Útil para actualizar los datos de un cliente en Factusol desde la UI.
    """
    try:
        data = arca_service.consultar_padron(cuit)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar padrón ARCA: {str(e)}")
