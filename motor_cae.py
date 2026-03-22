"""
Motor de Facturación CAE - Pipeline completo.

Flujo por cada factura:
  1. Verificar formato CUIT receptor
  2. Consultar Padrón AFIP → condición fiscal
  3. Validar compatibilidad tipo comprobante ↔ condición IVA
  4. Solicitar CAE al WSFE
  5. Guardar CAE en Factusol
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

import config
from afip.wsaa import WSAA, WSAAError
from afip.wsfe import WSFE, WSFEError, Factura
from afip.padron import PadronAFIP, PadronError, PersonaFiscal
from afip.fecha_cbte import ajustar_fecha_cbte, describir_rango_valido
from factusol.db import FactusolDB, FacturaFactusol, FactusolDBError

log = logging.getLogger(__name__)


@dataclass
class ResultadoProcesamiento:
    """Resultado completo del procesamiento de una factura."""
    factura: FacturaFactusol
    cae: Optional[str] = None
    cae_fecha_vto: Optional[str] = None
    persona_fiscal: Optional[PersonaFiscal] = None
    exitoso: bool = False
    errores: list = field(default_factory=list)
    advertencias: list = field(default_factory=list)
    etapa_fallo: str = ""         # "cuit" | "padron" | "validacion" | "cae" | "guardado"

    def agregar_error(self, msg: str, etapa: str = ""):
        self.errores.append(msg)
        if etapa:
            self.etapa_fallo = etapa
        log.error("[%s] %s", etapa or "ERROR", msg)

    def agregar_advertencia(self, msg: str):
        self.advertencias.append(msg)
        log.warning("[ADVERTENCIA] %s", msg)

    def __str__(self):
        if self.exitoso:
            return f"✓ {self.factura} → CAE: {self.cae}"
        return f"✗ {self.factura} → FALLO en [{self.etapa_fallo}]: {'; '.join(self.errores)}"


# ── Mapa condición IVA Factusol → código AFIP ─────────────────────────────────
CONDICION_IVA_FACTUSOL_MAP = {
    # Cadenas que puede devolver Factusol
    "RESPONSABLE INSCRIPTO":         1,
    "RI":                            1,
    "RESPONSABLE NO INSCRIPTO":      2,
    "RNI":                           2,
    "NO RESPONSABLE":                3,
    "NR":                            3,
    "EXENTO":                        4,
    "EX":                            4,
    "CONSUMIDOR FINAL":              5,
    "CF":                            5,
    "MONOTRIBUTO":                   6,
    "MT":                            6,
    "MONOTRIBUTISTA":                6,
    "NO CATEGORIZADO":               7,
    "NC":                            7,
}

# ── Reglas: tipo comprobante → condición IVA receptores válidos ───────────────
REGLAS_TIPO_CBTE = {
    1:  [1, 2, 3, 4, 7, 8, 9, 10, 11],    # Factura A → RI y similares
    6:  [5, 6, 7, 12, 13, 14],             # Factura B → CF, Monotributo, etc.
    11: [1, 2, 3, 4, 5, 6, 7, 12, 13, 14], # Factura C → todos (monotributista)
    51: [1, 2, 3, 4, 7, 8, 9, 10, 11],    # Factura M → similar a A
    3:  [1, 2, 3, 4, 7, 8, 9, 10, 11],    # NC A
    8:  [5, 6, 7, 12, 13, 14],             # NC B
    13: [1, 2, 3, 4, 5, 6, 7, 12, 13, 14],# NC C
}


class MotorCAE:
    """
    Motor principal para procesar facturas y obtener el CAE de AFIP.
    Orquesta WSAA, WSFE, Padrón y Factusol DB.
    """

    def __init__(self, mdb_path: str):
        self.mdb_path = mdb_path
        self._wsaa_wsfe  = None
        self._wsaa_padron = None
        self._wsfe       = None
        self._padron     = None

    # ──────────────────────────────────────────────────────────────────────────
    # Inicialización lazy de clientes AFIP
    # ──────────────────────────────────────────────────────────────────────────

    def _get_wsaa_wsfe(self) -> WSAA:
        if self._wsaa_wsfe is None:
            self._wsaa_wsfe = WSAA(
                cert_path  = config.AFIP_CERT,
                key_path   = config.AFIP_KEY,
                wsaa_url   = config.WSAA_URLS[config.AFIP_ENV],
                cache_file = str(config.TOKEN_CACHE_FILE),
                service    = "wsfe",
            )
        return self._wsaa_wsfe

    def _get_wsaa_padron(self) -> WSAA:
        if self._wsaa_padron is None:
            svc = "sr_padron_a13" if config.PADRON_SERVICE == "A13" else "sr_padron_a4"
            self._wsaa_padron = WSAA(
                cert_path  = config.AFIP_CERT,
                key_path   = config.AFIP_KEY,
                wsaa_url   = config.WSAA_URLS[config.AFIP_ENV],
                cache_file = str(config.TOKEN_CACHE_PADRON_FILE),
                service    = svc,
            )
        return self._wsaa_padron

    def _get_wsfe(self) -> WSFE:
        if self._wsfe is None:
            wsaa = self._get_wsaa_wsfe()
            self._wsfe = WSFE(
                token    = wsaa.token,
                sign     = wsaa.sign,
                cuit     = config.AFIP_CUIT,
                wsdl_url = config.WSFE_URLS[config.AFIP_ENV],
            )
        # Refrescar token si cambió
        wsaa = self._get_wsaa_wsfe()
        self._wsfe.token = wsaa.token
        self._wsfe.sign  = wsaa.sign
        return self._wsfe

    def _get_padron(self) -> PadronAFIP:
        if self._padron is None:
            wsaa = self._get_wsaa_padron()
            url_map = (
                config.PADRON_A13_URLS if config.PADRON_SERVICE == "A13"
                else config.PADRON_A4_URLS
            )
            self._padron = PadronAFIP(
                token       = wsaa.token,
                sign        = wsaa.sign,
                cuit_emisor = config.AFIP_CUIT,
                wsdl_url    = url_map[config.AFIP_ENV],
                service     = config.PADRON_SERVICE,
            )
        # Refrescar token
        wsaa = self._get_wsaa_padron()
        self._padron.token = wsaa.token
        self._padron.sign  = wsaa.sign
        return self._padron

    # ──────────────────────────────────────────────────────────────────────────
    # Pipeline principal
    # ──────────────────────────────────────────────────────────────────────────

    def procesar_factura(self, factura: FacturaFactusol) -> ResultadoProcesamiento:
        """
        Ejecuta el pipeline completo para una factura:
        CUIT → Padrón → Validación → [Comprobante asoc. NC/ND] → CAE → Guardado
        """
        from factusol.db import TIPOS_CON_ASOC
        resultado = ResultadoProcesamiento(factura=factura)
        log.info("── Procesando: %s ──", factura)

        # ── 1. Verificar CUIT receptor ────────────────────────────────────────
        cuit_ok, cuit_limpio, tipo_doc, nro_doc = self._verificar_cuit(factura, resultado)
        if not cuit_ok:
            return resultado

        # ── 2. Consultar Padrón AFIP ──────────────────────────────────────────
        persona = self._consultar_padron(factura, cuit_limpio, resultado)
        if persona is None:
            if tipo_doc == 99:  # Consumidor Final
                resultado.agregar_advertencia("CF sin CUIT, se omite consulta padrón")
            else:
                return resultado
        else:
            resultado.persona_fiscal = persona

        # ── 3. Validar compatibilidad tipo comprobante ↔ condición IVA ────────
        if persona and not self._validar_tipo_comprobante(factura, persona, resultado):
            return resultado

        # ── 4. Validar comprobante asociado para NC/ND ────────────────────────
        if factura.tipo in TIPOS_CON_ASOC:
            if not self._validar_cbte_asoc(factura, resultado):
                return resultado

        # ── 5. Solicitar CAE a AFIP ───────────────────────────────────────────
        res_cae = self._solicitar_cae(factura, tipo_doc, nro_doc, resultado)
        if not res_cae:
            return resultado

        # ── 6. Guardar CAE en Factusol ────────────────────────────────────────
        self._guardar_cae(factura, res_cae.cae, res_cae.cae_fecha_vto, resultado)

        resultado.exitoso = True
        resultado.cae = res_cae.cae
        resultado.cae_fecha_vto = res_cae.cae_fecha_vto
        log.info("✓ Factura procesada: %s → CAE %s", factura.numero, res_cae.cae)
        return resultado

    # ──────────────────────────────────────────────────────────────────────────
    # Etapas individuales
    # ──────────────────────────────────────────────────────────────────────────

    def _verificar_cuit(self, factura: FacturaFactusol, resultado: ResultadoProcesamiento):
        """
        Determina tipo/nro documento y valida el CUIT si aplica.
        Retorna: (ok, cuit_limpio, tipo_doc_afip, nro_doc)
        """
        from afip.padron import PadronAFIP

        cuit = factura.cuit_receptor.replace("-", "").strip()
        tipo_cbte = config.TIPO_COMPROBANTE_MAP.get(factura.tipo, 0)

        # Consumidor Final o sin CUIT
        if not cuit or cuit in ("0", "00000000000"):
            if tipo_cbte in (6, 8, 11, 13):  # B o C → ok para CF
                return True, "", 99, 0  # tipo_doc=99 (sin identificar)
            else:
                resultado.agregar_error(
                    "Factura tipo A/M requiere CUIT del receptor",
                    "cuit"
                )
                return False, "", 0, 0

        # Validar formato y dígito verificador
        if not PadronAFIP._validar_cuit_formato(cuit):
            resultado.agregar_error(
                f"CUIT inválido (dígito verificador o formato): {cuit}",
                "cuit"
            )
            return False, "", 0, 0

        log.info("CUIT receptor verificado: %s", cuit)
        return True, cuit, 80, int(cuit)  # tipo_doc=80 (CUIT)

    def _consultar_padron(
        self, factura: FacturaFactusol, cuit: str,
        resultado: ResultadoProcesamiento
    ) -> Optional[PersonaFiscal]:
        """Consulta el padrón AFIP para obtener condición fiscal."""
        if not cuit:
            return None
        try:
            padron = self._get_padron()
            persona = padron.consultar(cuit)
            if not persona.es_valido:
                resultado.agregar_error(
                    f"CUIT {cuit} no válido en padrón AFIP: {persona.error or persona.estado}",
                    "padron"
                )
                return None
            log.info("Padrón OK: %s - %s", persona.nombre, persona.condicion_iva)
            return persona
        except PadronError as e:
            resultado.agregar_error(f"Error consultando padrón AFIP: {e}", "padron")
            return None
        except WSAAError as e:
            resultado.agregar_error(f"Error autenticación AFIP (padrón): {e}", "padron")
            return None

    def _validar_tipo_comprobante(
        self, factura: FacturaFactusol, persona: PersonaFiscal,
        resultado: ResultadoProcesamiento
    ) -> bool:
        """Valida que el tipo de comprobante sea compatible con la condición IVA del receptor."""
        tipo_cbte = config.TIPO_COMPROBANTE_MAP.get(factura.tipo, 0)
        if tipo_cbte == 0:
            resultado.agregar_error(
                f"Tipo de comprobante desconocido: '{factura.tipo}'",
                "validacion"
            )
            return False

        cod_iva = persona.condicion_iva_codigo
        reglas = REGLAS_TIPO_CBTE.get(tipo_cbte, [])

        if reglas and cod_iva and cod_iva not in reglas:
            resultado.agregar_advertencia(
                f"ADVERTENCIA: {factura.tipo} para receptor con condición IVA "
                f"'{persona.condicion_iva}' puede ser incorrecto. "
                f"Tipo cbte AFIP: {tipo_cbte}"
            )
            # Advertencia, no bloqueante (el usuario eligió ese tipo)

        return True

    def _validar_cbte_asoc(
        self, factura: FacturaFactusol,
        resultado: ResultadoProcesamiento
    ) -> bool:
        """
        Verifica que la NC/ND tenga referenciada la factura original que anula.
        Si no está en el dataclass, intenta buscarla en la BD de Factusol.
        """
        if factura.tiene_asoc:
            log.info(
                "Comprobante asociado: %s %04d-%08d (CAE: %s)",
                factura.asoc_tipo, factura.asoc_pv, factura.asoc_nro,
                factura.asoc_cae or "sin CAE"
            )
            return True

        resultado.agregar_error(
            f"{factura.tipo} {factura.numero} no tiene factura original asociada. "
            "Use el diálogo de 'Asignar factura original' antes de procesar.",
            "validacion"
        )
        return False

    def _solicitar_cae(
        self, factura: FacturaFactusol,
        tipo_doc: int, nro_doc: int,
        resultado: ResultadoProcesamiento
    ):
        """Solicita el CAE al WSFE de AFIP."""
        tipo_cbte = config.TIPO_COMPROBANTE_MAP.get(factura.tipo, 0)
        if tipo_cbte == 0:
            resultado.agregar_error(f"Tipo comprobante sin mapeo AFIP: {factura.tipo}", "cae")
            return None

        # ── Ajuste de fecha según reglas AFIP (±5 días) ────────────────────────
        fecha_original = factura.fecha or datetime.date.today()
        fecha_str, fue_ajustada, msg_ajuste = ajustar_fecha_cbte(fecha_original)
        if fue_ajustada:
            resultado.agregar_advertencia(f"Fecha ajustada: {msg_ajuste}")

        # Calcular IVA automáticamente si no está desglosado
        imp_neto = round(factura.imp_neto, 2)
        imp_iva  = round(factura.imp_iva, 2)
        imp_exento = round(factura.imp_exento, 2)
        imp_total = round(factura.imp_total, 2)

        # Determinar alícuotas IVA (simplificado: detectar por cociente)
        iva_items = []
        if imp_iva > 0 and imp_neto > 0:
            alic = round(imp_iva / imp_neto * 100)
            if alic <= 2:
                id_alicuota = 3    # 0%
            elif alic <= 11:
                id_alicuota = 4    # 10.5%
            else:
                id_alicuota = 5    # 21%

            iva_items = [{"id": id_alicuota, "base_imp": imp_neto, "importe": imp_iva}]

        # ── Comprobantes asociados (NC/ND) ────────────────────────────────────
        cbtes_asoc = []
        if factura.es_nota and factura.tiene_asoc:
            tipo_asoc_afip = config.TIPO_COMPROBANTE_MAP.get(factura.asoc_tipo, 0)
            if tipo_asoc_afip:
                cbtes_asoc = [{
                    "tipo":        tipo_asoc_afip,
                    "punto_venta": factura.asoc_pv,
                    "nro":         factura.asoc_nro,
                }]
                log.info(
                    "CbtesAsoc: tipo %d PV %04d Nro %08d",
                    tipo_asoc_afip, factura.asoc_pv, factura.asoc_nro
                )
            else:
                resultado.agregar_advertencia(
                    f"Tipo de comprobante asociado '{factura.asoc_tipo}' sin mapeo AFIP; "
                    "se omite CbtesAsoc (puede ser rechazado)"
                )

        fac = Factura(
            tipo_cbte          = tipo_cbte,
            punto_venta        = factura.punto_venta,
            tipo_doc_receptor  = tipo_doc,
            nro_doc_receptor   = nro_doc,
            imp_total          = imp_total,
            imp_neto           = imp_neto,
            imp_iva            = imp_iva,
            imp_op_ex          = imp_exento,
            imp_tot_conc       = 0.0,
            imp_trib           = 0.0,
            fecha_cbte         = fecha_str,
            concepto           = 1,
            nro_cbte           = factura.nro_comprobante if factura.nro_comprobante else None,
            iva                = iva_items,
            cbtes_asoc         = cbtes_asoc,
        )

        try:
            wsfe = self._get_wsfe()
            res  = wsfe.solicitar_cae(fac)

            if res.aprobado:
                return res
            else:
                errores = "; ".join(res.errores) if res.errores else "Sin detalle"
                obs     = "; ".join(res.observaciones) if res.observaciones else ""
                resultado.agregar_error(
                    f"CAE rechazado por AFIP: {errores}" + (f" | Obs: {obs}" if obs else ""),
                    "cae"
                )
                return None

        except WSFEError as e:
            resultado.agregar_error(f"Error WSFE: {e}", "cae")
            return None
        except WSAAError as e:
            resultado.agregar_error(f"Error autenticación AFIP (WSFE): {e}", "cae")
            return None

    def _guardar_cae(
        self, factura: FacturaFactusol,
        cae: str, cae_fecha_vto: str,
        resultado: ResultadoProcesamiento
    ):
        """Persiste el CAE en la base de datos de Factusol."""
        try:
            with FactusolDB(self.mdb_path) as db:
                db.guardar_cae(factura.id_factura, cae, cae_fecha_vto)
            factura.cae = cae
            factura.cae_fecha_vto = cae_fecha_vto
            factura.estado_cae = "APROBADO"
        except FactusolDBError as e:
            resultado.agregar_error(
                f"CAE obtenido ({cae}) pero no se pudo guardar en Factusol: {e}",
                "guardado"
            )
            # El CAE existe aunque no se guardó en BD
            resultado.cae = cae
            resultado.cae_fecha_vto = cae_fecha_vto

    # ──────────────────────────────────────────────────────────────────────────
    # Utilidades
    # ──────────────────────────────────────────────────────────────────────────

    def verificar_conexion_afip(self) -> tuple[bool, str]:
        """Verifica conectividad con los servidores AFIP."""
        try:
            wsfe = self._get_wsfe()
            ok = wsfe.verificar_servidor()
            return ok, "Servidores AFIP OK" if ok else "Servidores AFIP con problemas"
        except Exception as e:
            return False, f"Error conectando a AFIP: {e}"

    def obtener_ultimo_nro(self, tipo_cbte_str: str, punto_venta: int) -> Optional[int]:
        """Consulta el último número autorizado para un tipo de comprobante."""
        tipo_cbte = config.TIPO_COMPROBANTE_MAP.get(tipo_cbte_str.upper(), 0)
        if not tipo_cbte:
            return None
        try:
            return self._get_wsfe().ultimo_numero(tipo_cbte, punto_venta)
        except Exception as e:
            log.error("Error obteniendo último número: %s", e)
            return None
