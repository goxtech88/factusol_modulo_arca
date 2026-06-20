"""
Router para validación de facturas en ARCA (AFIP).
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User, UserPuntoVenta
from app.models.cae_log import CAELog
from app.services import factusol_service, arca_service, rg1361_service

router = APIRouter(prefix="/api/arca", tags=["arca"])


# Letra del comprobante segun tipo AFIP, para armar el Nro Cbte estilo Factusol
# (ej: "B-0002-00006486").
_LETRA_CBTE = {
    1: "A", 6: "B", 11: "C",
    2: "NDA", 7: "NDB", 12: "NDC",
    3: "NCA", 8: "NCB", 13: "NCC",
}


def _build_pedfac_and_barcode(tipo_comprobante, punto_venta, voucher_number, cae, cae_vto):
    """Arma el Nro de comprobante (PEDFAC) y el codigo de barras AFIP (AATFAC)."""
    from app.config import get_config

    letra = _LETRA_CBTE.get(tipo_comprobante, "X")
    pedfac = f"{letra}-{str(punto_venta).zfill(4)}-{str(voucher_number).zfill(8)}"

    cuit_bc = str(get_config().get("empresa", {}).get("cuit", "")).replace("-", "").strip().zfill(11)
    vto_bc = str(cae_vto or "").replace("-", "")[:8]
    # CUIT(11) + TipoCbte(3) + PV(5) + CAE(14) + VtoCae(8)
    barcode = (
        f"{cuit_bc}{str(tipo_comprobante).zfill(3)}{str(punto_venta).zfill(5)}"
        f"{str(cae).zfill(14)}{vto_bc}"
    )
    return pedfac, barcode


def _grabar_cae_en_factusol(detail, tipfac, codfac, punto_venta, tipo_comprobante,
                            voucher_number, cae, cae_vto):
    """
    Genera el QR AFIP, arma el Nro de comprobante y el codigo de barras, y graba
    todo en F_FAC de Factusol. Reutilizado tanto al validar como al re-grabar
    manualmente cuando el CAE quedo en el log pero no llego a Factusol.

    Retorna dict con pedfac, barcode y qr_path.
    """
    from app.config import get_config
    from datetime import datetime as _dt

    cuit = str(get_config().get("empresa", {}).get("cuit", "")).replace("-", "").strip()

    voucher_data = arca_service.build_voucher_data(
        detail["header"], detail["lines"], detail.get("cliente"),
        punto_venta, tipo_comprobante,
    )

    fecha_raw = detail["header"].get("FECFAC", "")
    if hasattr(fecha_raw, "strftime"):
        fecha_str = fecha_raw.strftime("%Y-%m-%d")
    elif isinstance(fecha_raw, str) and len(fecha_raw) >= 8:
        fecha_str = fecha_raw[:10]
    else:
        fecha_str = _dt.now().strftime("%Y-%m-%d")

    qr_path = arca_service.generate_afip_qr(
        cuit_emisor=cuit,
        punto_venta=punto_venta,
        voucher_number=voucher_number,
        fecha_cbte=fecha_str,
        tipo_comprobante=tipo_comprobante,
        tipo_doc_receptor=voucher_data["tipo_doc"],
        nro_doc_receptor=voucher_data["nro_doc"],
        imp_total=voucher_data["imp_total"],
        cae=cae,
        cae_vto=cae_vto,
        tipfac=tipfac,
        codfac=codfac,
    )

    pedfac, barcode = _build_pedfac_and_barcode(
        tipo_comprobante, punto_venta, voucher_number, cae, cae_vto,
    )

    factusol_service.write_cae_to_factura(
        tipfac=tipfac,
        codfac=codfac,
        cae=cae,
        voucher_number=pedfac,
        cae_vto=cae_vto,
        qr_img_path=qr_path,
        barcode=barcode,
    )

    return {"pedfac": pedfac, "barcode": barcode, "qr_path": qr_path}


@router.post("/validate/{tipfac}/{codfac}")
def validate_invoice(
    tipfac: int,
    codfac: int,
    pv_id: int = None,
    usar_fecha_hoy: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Valida una factura de Factusol en ARCA y obtiene el CAE.
    pv_id: ID del punto de venta del usuario a utilizar.
    usar_fecha_hoy: si es True, el comprobante se valida en ARCA con la fecha de
        HOY en lugar de la fecha del comprobante de Factusol. La fecha original
        en F_FAC NO se modifica (se preserva la trazabilidad de la operacion).
        Pensado para clientes que cargan facturas en Factusol con la fecha real
        de la operacion pero validan en ARCA periodicamente.
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

    # ── Fecha del comprobante que se manda a ARCA ──
    fecha_orig = detail.get("header", {}).get("FECFAC")

    if usar_fecha_hoy:
        # El usuario eligio el tilde "Usar fecha hoy": el comprobante se valida en
        # ARCA con la fecha de HOY (fecha de la validacion fiscal), NO con la fecha
        # del comprobante de Factusol. Para clientes que cargan la factura con la
        # fecha real de la operacion pero validan en ARCA periodicamente.
        #
        # IMPORTANTE: se cambia FECFAC SOLO en memoria (para armar el voucher y el
        # QR con la fecha de hoy). NO se reescribe FECFAC en F_FAC, asi la fecha
        # original en Factusol queda intacta y no se pierde la trazabilidad.
        from datetime import date as _date
        hoy = _date.today()
        fecha_orig_parse = arca_service._parse_fecha(fecha_orig)
        detail["header"]["FECFAC"] = hoy
        was_adjusted = True
        ajuste_msg = (
            f"Validada con fecha de HOY {hoy.strftime('%d/%m/%Y')}; "
            f"la fecha en Factusol "
            f"({fecha_orig_parse.strftime('%d/%m/%Y') if fecha_orig_parse else fecha_orig}) "
            f"NO se modifico."
        )
        ajuste_info = {
            "usar_fecha_hoy": True,
            "fecha_enviada": hoy.isoformat(),
            "fecha_factusol": fecha_orig_parse.isoformat() if fecha_orig_parse else str(fecha_orig),
            "factusol_modificado": False,
        }
        print(f"[FECHA HOY] {tipfac}-{codfac}: {ajuste_msg}")
    else:
        # ── Auto-ajuste de fecha del comprobante (rango AFIP) ──
        # AFIP rechaza con error 10016 si la fecha esta > 5 dias (productos) o > 10
        # (servicios) respecto del actual. En vez de bloquear, ajustamos la fecha
        # al limite valido mas cercano y actualizamos F_FAC para que Factusol quede
        # sincronizado con la fecha que efectivamente se mando a AFIP.
        fecha_final, was_adjusted, ajuste_msg, ajuste_info = arca_service.auto_adjust_invoice_date(fecha_orig, concepto=1)
        if was_adjusted:
            try:
                factusol_service.update_invoice_date(tipfac, codfac, fecha_final)
                # Refrescar detail con la nueva fecha para que el voucher se arme con ella
                detail["header"]["FECFAC"] = fecha_final
                print(f"[FECHA AJUSTADA] {tipfac}-{codfac}: {ajuste_msg}")
            except Exception as _e:
                print(f"[FECHA] WARN: no pude actualizar FECFAC en F_FAC: {_e}")
                # Sigo de todos modos: pyafipws recibe la fecha ajustada del header

    # Filtrar lineas-leyenda (cantidad=0 Y precio=0): Factusol las acepta como
    # texto descriptivo dentro del listado de items, pero no son items reales.
    # Si las dejamos pueden bloquear la validacion en ARCA (algunos validadores
    # rechazan items con todo en cero). Las omitimos pero la factura sigue OK.
    raw_lines = detail.get("lines") or []
    filtered_lines = arca_service.filter_real_lines(raw_lines)
    n_legends = len(raw_lines) - len(filtered_lines)
    if n_legends > 0:
        print(f"[LINEAS LEYENDA] {tipfac}-{codfac}: omitidas {n_legends} de {len(raw_lines)} (cant=0 precio=0)")
    detail["lines"] = filtered_lines

    # Auto-enriquecimiento de padron desactivado (v1.5.1) — genera errores
    # al no ser datos oficiales. El CFECLI debe configurarse en Factusol.
    cliente = detail.get("cliente") or {}

    # Determinar tipo de comprobante
    from app.services.arca_service import determine_tipo_comprobante
    from app.config import get_config
    config = get_config()
    cond_emisor = config.get("empresa", {}).get("condicion_iva", "Responsable Inscripto")
    mono_como_a = bool(config.get("empresa", {}).get("facturar_mono_como_a", True))
    # CFECLI: 0=no config, 1=CF, 2=RI, 3=Mono, 4=Exento
    cfecli = detail.get("cliente", {}).get("CFECLI", 0) or 0

    # NIF limpio para determinar tipo de comprobante
    nifcli_clean = str(detail.get("cliente", {}).get("NIFCLI", "") or "").replace("-", "").strip()

    # Si el PV tiene tipo_comprobante fijo (!=0), usarlo; sino calcular por CFECLI + NIF
    if pv_config.tipo_comprobante and pv_config.tipo_comprobante != 0:
        tipo_comprobante = pv_config.tipo_comprobante
        print(f"[TIPO CBTE] {tipfac}-{codfac}: PV {pv_config.punto_venta} TIENE TIPO FIJO = {tipo_comprobante} (override, ignora CFECLI)")
    else:
        tipo_comprobante, decision_info = determine_tipo_comprobante(
            cfecli, cond_emisor, nifcli_clean, mono_como_a, explain=True,
        )
        print(
            f"[TIPO CBTE] {tipfac}-{codfac}: cfecli={cfecli} ({decision_info.get('cfecli_label', '?')}) "
            f"nif='{nifcli_clean}' mono_como_a={mono_como_a} → tipo={tipo_comprobante}. "
            f"Razon: {decision_info.get('razon', '?')}"
        )



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

    # Verificar que no tenga NC emitida (no se puede re-validar una factura anulada)
    nc_tipos = [3, 8, 13]
    existing_nc = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
        CAELog.tipo_comprobante.in_(nc_tipos),
    ).first()
    if existing_nc:
        raise HTTPException(
            status_code=400,
            detail="Esta factura tiene una NC emitida. No se puede volver a validar.",
        )

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

    # Fecha realmente enviada a ARCA (= FECFAC en memoria: hoy si usar_fecha_hoy,
    # la ajustada si se autoajusto, o la original). El export RG 1361 la prefiere
    # sobre la FECFAC de Factusol para que el duplicado coincida con AFIP.
    _fch_arca = arca_service._parse_fecha(detail["header"].get("FECFAC"))
    _fecha_cbte_str = _fch_arca.isoformat() if _fch_arca else None

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
        fecha_cbte=_fecha_cbte_str,
        imp_total=detail["header"].get("TOTFAC"),
        imp_neto=sum(float(detail["header"].get(f"BAS{i}FAC") or 0) for i in range(1, 5)),
        imp_iva=sum(float(detail["header"].get(f"IIVA{i}FAC") or 0) for i in range(1, 5)),
        cliente_nombre=detail["header"].get("CNOFAC"),
        cliente_doc=detail.get("cliente", {}).get("NIFCLI") if detail.get("cliente") else None,
    )
    db.add(cae_log)
    db.commit()

    # ── Grabar datos CAE (QR + Nro Cbte + codigo de barras) en F_FAC ──────
    qr_path = ""
    factusol_grabado = True
    factusol_error = None
    try:
        _info = _grabar_cae_en_factusol(
            detail=detail,
            tipfac=tipfac,
            codfac=codfac,
            punto_venta=pv_config.punto_venta,
            tipo_comprobante=tipo_comprobante,
            voucher_number=result.get("voucher_number", 0),
            cae=result.get("CAE", ""),
            cae_vto=result.get("CAEFchVto", ""),
        )
        qr_path = _info["qr_path"]
    except Exception as _write_err:
        # No falla la respuesta si el write-back a Access falla: el CAE ya quedo
        # en el log y el usuario puede re-grabarlo con el boton "Grabar en Factusol".
        factusol_grabado = False
        factusol_error = str(_write_err)
        print(f"⚠️ No se pudo grabar CAE en Factusol F_FAC: {_write_err}")


    msg_resp = "Factura validada exitosamente en ARCA"
    if was_adjusted:
        msg_resp += f" - {ajuste_msg}"
    if not factusol_grabado:
        msg_resp += " (CAE obtenido, pero NO se grabo en Factusol: use 'Grabar en Factusol')"

    return {
        "status": "ok",
        "cae": result.get("CAE"),
        "cae_vto": result.get("CAEFchVto"),
        "voucher_number": result.get("voucher_number"),
        "tipo_comprobante": tipo_comprobante,
        "resultado": result.get("resultado"),
        "qr_path": qr_path,
        "factusol_grabado": factusol_grabado,
        "factusol_error": factusol_error,
        "fecha_ajustada": was_adjusted,
        "fecha_ajuste_info": ajuste_info if was_adjusted else None,
        "usar_fecha_hoy": usar_fecha_hoy,
        "message": msg_resp,
    }



@router.post("/write-factusol/{tipfac}/{codfac}")
def write_factusol(
    tipfac: int,
    codfac: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Re-graba en Factusol (F_FAC) los datos del CAE ya emitido: Nro de
    comprobante, vencimiento, QR y codigo de barras AFIP.

    Util cuando el CAE se obtuvo correctamente en ARCA (quedo en el log) pero la
    escritura a Factusol fallo en su momento, o para re-sincronizar si hay alguna
    diferencia entre lo emitido y lo que figura en Factusol.
    """
    # Buscar el CAE de la factura (excluyendo NC: la NC es un comprobante aparte)
    nc_tipos = [3, 8, 13]
    cae_log = (
        db.query(CAELog)
        .filter(
            CAELog.tipfac == tipfac,
            CAELog.codfac == codfac,
            CAELog.tipo_comprobante.notin_(nc_tipos),
        )
        .order_by(CAELog.created_at.desc())
        .first()
    )

    if not cae_log:
        raise HTTPException(
            status_code=404,
            detail="Esta factura no tiene CAE emitido. Primero obtenga el CAE en ARCA.",
        )

    # Obtener datos de Factusol para reconstruir el QR/codigo de barras
    try:
        detail = factusol_service.get_invoice_detail(tipfac, codfac)
        if not detail:
            raise HTTPException(status_code=404, detail="Factura no encontrada en Factusol")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer Factusol: {str(e)}")

    detail["lines"] = arca_service.filter_real_lines(detail.get("lines") or [])

    try:
        info = _grabar_cae_en_factusol(
            detail=detail,
            tipfac=tipfac,
            codfac=codfac,
            punto_venta=cae_log.punto_venta,
            tipo_comprobante=cae_log.tipo_comprobante,
            voucher_number=cae_log.voucher_number,
            cae=cae_log.cae,
            cae_vto=cae_log.cae_vto,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudieron grabar los datos en Factusol: {str(e)}",
        )

    return {
        "status": "ok",
        "cae": cae_log.cae,
        "cae_vto": cae_log.cae_vto,
        "voucher_number": cae_log.voucher_number,
        "comprobante_nro": info["pedfac"],
        "tipo_comprobante": cae_log.tipo_comprobante,
        "qr_path": info["qr_path"],
        "message": f"Datos grabados en Factusol: CAE {cae_log.cae} — {info['pedfac']}",
    }


@router.post("/credit-note/{tipfac}/{codfac}")
def create_credit_note(
    tipfac: int,
    codfac: int,
    pv_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Emite una Nota de Crédito en ARCA para anular una factura ya validada.
    Requiere que la factura tenga CAE previamente asignado.
    """
    from app.config import get_config
    from datetime import datetime

    # Buscar el CAE original de la factura
    cae_original = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
    ).first()

    if not cae_original:
        raise HTTPException(
            status_code=400,
            detail="La factura no tiene CAE. Solo se pueden anular facturas ya validadas en ARCA.",
        )

    # Verificar que no se haya emitido ya una NC para esta factura
    nc_tipos = [3, 8, 13]  # NC A, NC B, NC C
    existing_nc = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
        CAELog.tipo_comprobante.in_(nc_tipos),
    ).first()
    if existing_nc:
        return {
            "status": "already_exists",
            "cae": existing_nc.cae,
            "cae_vto": existing_nc.cae_vto,
            "voucher_number": existing_nc.voucher_number,
            "tipo_comprobante": existing_nc.tipo_comprobante,
            "message": "Ya existe una Nota de Crédito para esta factura",
        }

    # Buscar config de punto de venta
    if pv_id:
        pv_config = db.query(UserPuntoVenta).filter(
            UserPuntoVenta.id == pv_id,
            UserPuntoVenta.user_id == current_user.id,
        ).first()
    else:
        pv_config = db.query(UserPuntoVenta).filter(
            UserPuntoVenta.user_id == current_user.id,
            UserPuntoVenta.serie_factusol == tipfac,
        ).first()

    if not pv_config:
        raise HTTPException(
            status_code=400,
            detail="No tiene un punto de venta configurado para esta serie",
        )

    # Obtener datos de Factusol
    try:
        detail = factusol_service.get_invoice_detail(tipfac, codfac)
        if not detail:
            raise HTTPException(status_code=404, detail="Factura no encontrada en Factusol")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer Factusol: {str(e)}")

    # Filtrar lineas-leyenda (igual que en validate_invoice)
    detail["lines"] = arca_service.filter_real_lines(detail.get("lines") or [])

    # Emitir NC en ARCA
    tipo_cbte_original = cae_original.tipo_comprobante
    try:
        result = arca_service.validate_credit_note(
            invoice_header=detail["header"],
            invoice_lines=detail["lines"],
            cliente=detail["cliente"],
            punto_venta=pv_config.punto_venta,
            tipo_comprobante_original=tipo_cbte_original,
            voucher_number_original=cae_original.voucher_number,
            punto_venta_original=cae_original.punto_venta,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en ARCA al emitir NC: {str(e)}")

    tipo_nc = result.get("tipo_nc", arca_service.tipo_factura_to_nota_credito(tipo_cbte_original))

    # Guardar log de la NC
    nc_log = CAELog(
        user_id=current_user.id,
        tipfac=tipfac,
        codfac=codfac,
        punto_venta=pv_config.punto_venta,
        tipo_comprobante=tipo_nc,
        voucher_number=result.get("voucher_number", 0),
        cae=result.get("CAE", ""),
        cae_vto=result.get("CAEFchVto", ""),
        imp_total=detail["header"].get("TOTFAC"),
        imp_neto=sum(float(detail["header"].get(f"BAS{i}FAC") or 0) for i in range(1, 5)),
        imp_iva=sum(float(detail["header"].get(f"IIVA{i}FAC") or 0) for i in range(1, 5)),
        cliente_nombre=detail["header"].get("CNOFAC"),
        cliente_doc=detail.get("cliente", {}).get("NIFCLI") if detail.get("cliente") else None,
        # Relacion con la factura que anula: imprescindible para que la NC indique
        # de que comprobante es (AFIP comprobante asociado + impresion de la NC).
        motivo="Anulacion",
        cmp_asoc_tipo=tipo_cbte_original,
        cmp_asoc_pv=cae_original.punto_venta,
        cmp_asoc_nro=cae_original.voucher_number,
    )
    db.add(nc_log)
    db.commit()

    # Nombres legibles
    nc_nombres = {3: "NC A", 8: "NC B", 13: "NC C"}
    nc_nombre = nc_nombres.get(tipo_nc, f"NC Tipo {tipo_nc}")

    _letra_map = {3: "NCA", 8: "NCB", 13: "NCC"}
    _letra = _letra_map.get(tipo_nc, "NC")
    _pv_str = str(pv_config.punto_venta).zfill(4)
    _cbte_str = str(result.get("voucher_number", 0)).zfill(8)
    _pedfac = f"{_letra}-{_pv_str}-{_cbte_str}"

    return {
        "status": "ok",
        "cae": result.get("CAE"),
        "cae_vto": result.get("CAEFchVto"),
        "voucher_number": result.get("voucher_number"),
        "tipo_comprobante": tipo_nc,
        "tipo_nombre": nc_nombre,
        "comprobante_nro": _pedfac,
        "resultado": result.get("resultado"),
        "message": f"{nc_nombre} emitida exitosamente - {_pedfac}",
    }


@router.get("/status/{tipfac}/{codfac}")
def check_cae_status(
    tipfac: int,
    codfac: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifica si una factura ya tiene CAE asignado y si tiene NC emitida."""
    # Buscar factura original (tipo 1, 6, 11)
    nc_tipos = [3, 8, 13]
    factura_log = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
        CAELog.tipo_comprobante.notin_(nc_tipos),
    ).first()

    # Buscar NC asociada
    nc_log = db.query(CAELog).filter(
        CAELog.tipfac == tipfac,
        CAELog.codfac == codfac,
        CAELog.tipo_comprobante.in_(nc_tipos),
    ).first()

    if factura_log:
        return {
            "validated": True,
            "cae": factura_log.cae,
            "cae_vto": factura_log.cae_vto,
            "voucher_number": factura_log.voucher_number,
            "punto_venta": factura_log.punto_venta,
            "tipo_comprobante": factura_log.tipo_comprobante,
            "created_at": factura_log.created_at.isoformat() if factura_log.created_at else None,
            "has_nc": nc_log is not None,
            "nc_cae": nc_log.cae if nc_log else None,
        }
    return {"validated": False, "has_nc": False}


@router.get("/logs")
def list_cae_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los CAE emitidos por el usuario actual."""
    if current_user.role == "admin":
        logs = db.query(CAELog).order_by(CAELog.created_at.desc()).limit(500).all()
    else:
        logs = db.query(CAELog).filter(
            CAELog.user_id == current_user.id
        ).order_by(CAELog.created_at.desc()).limit(500).all()

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
            "imp_neto": l.imp_neto,
            "imp_iva": l.imp_iva,
            "cliente_nombre": l.cliente_nombre,
            "cliente_doc": l.cliente_doc,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


@router.get("/diagnostic")
def diagnostic(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint de diagnostico para CAE Emitidos. Devuelve:
      - Datos del usuario actual (id, username, role, full_name)
      - Total de logs CAE en la DB (global vs los visibles para el user)
      - Ultimos 5 CAE (id, fecha, factura, PV, CAE, cliente)
      - Path de la DB SQLite
      - Version de la app

    Util cuando "CAE Emitidos" aparece vacio: dice si el problema es de
    permisos (rol no admin), de filtro (mes), o si la tabla esta vacia.
    """
    from app.database import engine
    import sys
    from app.main import app as fastapi_app

    total = db.query(CAELog).count()

    if current_user.role == "admin":
        visible = total
        recent = db.query(CAELog).order_by(CAELog.created_at.desc()).limit(5).all()
    else:
        visible = db.query(CAELog).filter(CAELog.user_id == current_user.id).count()
        recent = (
            db.query(CAELog)
            .filter(CAELog.user_id == current_user.id)
            .order_by(CAELog.created_at.desc())
            .limit(5)
            .all()
        )

    return {
        "version": fastapi_app.version,
        "frozen": bool(getattr(sys, "frozen", False)),
        "current_user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_admin": current_user.role == "admin",
        },
        "cae_logs": {
            "total_en_db": total,
            "visibles_para_este_user": visible,
            "ultimos_5": [
                {
                    "id": l.id,
                    "tipfac_codfac": f"{l.tipfac}-{l.codfac}",
                    "punto_venta": l.punto_venta,
                    "tipo_comprobante": l.tipo_comprobante,
                    "voucher_number": l.voucher_number,
                    "cae": l.cae,
                    "cliente_nombre": l.cliente_nombre,
                    "imp_total": l.imp_total,
                    "user_id": l.user_id,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in recent
            ],
        },
        "db_url": str(engine.url).replace("///", "/// "),  # sanitizar para que se vea
    }


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
    Consulta datos fiscales de un CUIT usando cuitonline.com.

    Retorna razón social, tipo persona, condición IVA y domicilio fiscal.
    Útil para actualizar los datos de un cliente en Factusol desde la UI.
    """
    try:
        data = arca_service.consultar_cuit_online(cuit)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar datos del CUIT: {str(e)}")


# ── Enriquecer cliente desde CUIT ─────────────────────────────────────────────

@router.post("/enrich-customer/{codcli}/{cuit}")
def enrich_customer(
    codcli: int,
    cuit: str,
    current_user: User = Depends(get_current_user),
):
    """
    Consulta datos fiscales del CUIT y actualiza el cliente en Factusol.
    Un solo endpoint que hace lookup + update.
    """
    from app.services import factusol_service

    try:
        data = arca_service.consultar_cuit_online(cuit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar CUIT: {str(e)}")

    # Mapear condición IVA a CFECLI de Factusol
    cfecli = 0
    cond = (data.get("condicion_iva") or "").lower()
    if "consumidor final" in cond:
        cfecli = 1
    elif "responsable inscripto" in cond or "iva inscripto" in cond:
        cfecli = 2
    elif "monotributo" in cond:
        cfecli = 3
    elif "exento" in cond:
        cfecli = 4

    # Preparar datos para Factusol
    update = {}
    if data.get("razon_social"):
        update["NOFCLI"] = data["razon_social"]
    dom = data.get("domicilio_fiscal") or {}
    dom_parts = [dom.get("calle", ""), dom.get("numero", "")].copy()
    dom_str = " ".join(p for p in dom_parts if p).strip()
    if dom_str:
        update["DOMCLI"] = dom_str
    if dom.get("localidad"):
        update["POBCLI"] = dom["localidad"]
    if dom.get("cp"):
        update["CPOCLI"] = dom["cp"]
    if dom.get("provincia"):
        update["PROCLI"] = dom["provincia"]
    if cfecli:
        update["CFECLI"] = cfecli

    if update:
        try:
            factusol_service.update_customer_fiscal(codcli, update)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar cliente: {str(e)}")

    return {
        "status": "ok",
        "razon_social": data.get("razon_social", ""),
        "condicion_iva": data.get("condicion_iva", ""),
        "cfecli": cfecli,
        "updated_fields": list(update.keys()),
        "source": data.get("source", "cuitonline.com"),
    }


# ── Auto-validación ──────────────────────────────────────────────────────────

@router.get("/auto-validate/status")
def auto_validate_status(current_user: User = Depends(get_current_user)):
    """Estado del auto-validador."""
    from app.services import auto_validate
    return auto_validate.get_status()


@router.post("/auto-validate/toggle")
async def auto_validate_toggle(
    enabled: bool,
    current_user: User = Depends(get_current_user),
):
    """Activa/desactiva la auto-validación. Disponible para admin y usuarios."""
    from app.services import auto_validate
    return auto_validate.toggle(enabled)


@router.post("/auto-validate/interval")
def auto_validate_interval(
    seconds: int,
    current_user: User = Depends(get_current_user),
):
    """Cambia el intervalo de chequeo (30-600 segundos)."""
    from app.services import auto_validate
    return auto_validate.set_interval(seconds)


@router.post("/auto-validate/payment-filters")
def auto_validate_payment_filters(
    body: dict,
    current_user: User = Depends(get_current_user),
):
    """Guarda las formas de pago permitidas para auto-validación.
    body: { fopfac_codes: ["1", "2", ...] }  — vacío = todas permitidas.
    """
    from app.services import auto_validate
    codes = body.get("fopfac_codes", [])
    return auto_validate.set_payment_filters(codes)


@router.get("/auto-validate/payment-filters")
def get_auto_validate_payment_filters(
    current_user: User = Depends(get_current_user),
):
    """Devuelve las formas de pago configuradas para auto-validación."""
    from app.services import auto_validate
    return auto_validate.get_payment_filters()


# ── RG 1361 - Duplicado Electrónico ──────────────────────────────────────────

@router.get("/rg1361/export")
def export_rg1361(
    year: int,
    month: int,
    pv: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Genera y descarga un ZIP con CABECERA_AAAAMM.txt y DETALLE_AAAAMM.txt
    según el formato de la RG (AFIP) 1361/2002 - Anexo II - Régimen de
    Almacenamiento Electrónico de Registraciones (Duplicado Electrónico).

    - year/month: período fiscal a exportar.
    - pv: opcional, filtra por punto de venta (todos si se omite).
    - admin ve todos los CAE; usuario ve solo los suyos.
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Mes inválido (1-12)")
    if not (2000 <= year <= 2100):
        raise HTTPException(status_code=400, detail="Año inválido")

    user_filter = None if current_user.role == "admin" else current_user.id

    try:
        zip_bytes, filename, count = rg1361_service.generate_zip(
            db, year=year, month=month, pv=pv, user_id=user_filter,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar archivos RG 1361: {str(e)}")

    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No hay comprobantes con CAE para {year:04d}-{month:02d}" + (f" (PV {pv})" if pv else ""),
        )

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Comprobantes-Count": str(count),
        },
    )


@router.get("/rg1361/export-pami")
def export_pami_ace(
    year: int,
    month: int,
    pv: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Genera y descarga un ZIP con los TXT POR COMPROBANTE en el formato que exige
    el portal PAMI ACE. Cada comprobante produce 3 archivos nombrados con su
    clave fiscal:
        {CUIT}_{TIPO}_{PV}_{NRO}_CABECERA.txt
        {CUIT}_{TIPO}_{PV}_{NRO}_DETALLE.txt
        {CUIT}_{TIPO}_{PV}_{NRO}_VENTAS.txt
    (el PDF lo aporta Factusol con el mismo nombre base + ".pdf").

    - year/month: período fiscal a exportar.
    - pv: opcional, filtra por punto de venta.
    - admin ve todos los CAE; usuario ve solo los suyos.
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Mes inválido (1-12)")
    if not (2000 <= year <= 2100):
        raise HTTPException(status_code=400, detail="Año inválido")

    user_filter = None if current_user.role == "admin" else current_user.id

    try:
        zip_bytes, filename, count, skipped = rg1361_service.generate_pami_zip(
            db, year=year, month=month, pv=pv, user_id=user_filter,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar archivos PAMI ACE: {str(e)}")

    if count == 0:
        msg = f"No hay comprobantes con CAE para {year:04d}-{month:02d}" + (f" (PV {pv})" if pv else "")
        if skipped > 0:
            msg += f" emitidos a INSSJP (CUIT {rg1361_service.PAMI_INSSJP_CUIT}). Se omitieron {skipped} comprobante(s) con otro receptor."
        raise HTTPException(status_code=404, detail=msg)

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Comprobantes-Count": str(count),
            "X-Comprobantes-Skipped": str(skipped),
        },
    )
