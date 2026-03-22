"""
Validación y ajuste de fecha de comprobante según reglas AFIP/ARCA.

AFIP permite autorizar comprobantes con fecha de hasta 5 días corridos
hacia atrás o 5 días hacia adelante respecto de la fecha actual.

Si la fecha de la factura supera ese límite (ej: tiene 10 días de antigüedad),
se ajusta automáticamente al límite permitido (hoy - 5 días) y se informa
al usuario mediante una advertencia.
"""
import datetime
import logging

log = logging.getLogger(__name__)

DIAS_MARGEN = 5  # Días de margen permitidos por AFIP (antes y después)


def ajustar_fecha_cbte(fecha_factura: datetime.date) -> tuple[str, bool, str]:
    """
    Valida y ajusta la fecha del comprobante según las reglas de AFIP.

    Args:
        fecha_factura: Fecha original de la factura en Factusol.

    Returns:
        Tuple (fecha_afip_str, fue_ajustada, mensaje)
        - fecha_afip_str: Fecha a enviar a AFIP en formato AAAAMMDD
        - fue_ajustada: True si la fecha fue modificada respecto a la original
        - mensaje: Descripción del ajuste realizado (vacío si no hubo ajuste)
    """
    hoy = datetime.date.today()
    limite_pasado  = hoy - datetime.timedelta(days=DIAS_MARGEN)
    limite_futuro  = hoy + datetime.timedelta(days=DIAS_MARGEN)

    fecha_original = fecha_factura
    fue_ajustada   = False
    mensaje        = ""

    if fecha_factura < limite_pasado:
        # La factura es más antigua que el límite → ajustar al límite
        dias_atras = (hoy - fecha_factura).days
        fecha_factura = limite_pasado
        fue_ajustada = True
        mensaje = (
            f"Fecha original {fecha_original.strftime('%d/%m/%Y')} "
            f"({dias_atras} días de antigüedad) excede el límite AFIP de {DIAS_MARGEN} días. "
            f"Ajustada automáticamente a {fecha_factura.strftime('%d/%m/%Y')} "
            f"(hoy - {DIAS_MARGEN} días)."
        )
        log.warning("Fecha ajustada: %s → %s | %s", fecha_original, fecha_factura, mensaje)

    elif fecha_factura > limite_futuro:
        # Fecha futura fuera del margen → ajustar al límite futuro
        fecha_factura = limite_futuro
        fue_ajustada = True
        mensaje = (
            f"Fecha original {fecha_original.strftime('%d/%m/%Y')} excede el límite "
            f"futuro AFIP de {DIAS_MARGEN} días. "
            f"Ajustada a {fecha_factura.strftime('%d/%m/%Y')}."
        )
        log.warning("Fecha ajustada (futura): %s → %s", fecha_original, fecha_factura)

    return fecha_factura.strftime("%Y%m%d"), fue_ajustada, mensaje


def describir_rango_valido() -> str:
    """Retorna una descripción del rango de fechas actualmente válido para AFIP."""
    hoy = datetime.date.today()
    desde = hoy - datetime.timedelta(days=DIAS_MARGEN)
    hasta = hoy + datetime.timedelta(days=DIAS_MARGEN)
    return (
        f"Rango válido AFIP: {desde.strftime('%d/%m/%Y')} → {hasta.strftime('%d/%m/%Y')} "
        f"(hoy ± {DIAS_MARGEN} días)"
    )
