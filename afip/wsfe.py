"""
WSFE v1 - Web Service de Facturación Electrónica de AFIP/ARCA
Obtención de CAE (Código de Autorización Electrónico).
"""
import logging
from dataclasses import dataclass, field
from typing import Optional
import datetime

import zeep
import zeep.helpers

log = logging.getLogger(__name__)


class WSFEError(Exception):
    pass


@dataclass
class ResultadoCAE:
    """Resultado de la solicitud de CAE a AFIP."""
    # Datos del comprobante
    tipo_cbte: int
    punto_venta: int
    nro_desde: int
    nro_hasta: int
    # Resultado
    cae: str
    cae_fecha_vto: str         # AAAAMMDD
    resultado: str              # "A" aprobado, "R" rechazado
    observaciones: list = field(default_factory=list)
    errores: list = field(default_factory=list)
    aprobado: bool = False

    def __str__(self):
        if self.aprobado:
            return (
                f"CAE: {self.cae} | Vto: {self.cae_fecha_vto} | "
                f"Cbte: {self.tipo_cbte}-{self.punto_venta:05d}-{self.nro_desde:08d}"
            )
        return f"RECHAZADO | Errores: {'; '.join(self.errores)}"


@dataclass
class Factura:
    """Datos de una factura para enviar a AFIP."""
    tipo_cbte: int              # 1=FA, 6=FB, 11=FC ...
    punto_venta: int
    tipo_doc_receptor: int      # 80=CUIT, 96=DNI, 99=CF
    nro_doc_receptor: int       # CUIT/DNI del receptor
    imp_total: float
    imp_neto: float
    imp_iva: float
    imp_op_ex: float = 0.0      # Operaciones exentas
    imp_trib: float = 0.0       # Otros tributos
    imp_tot_conc: float = 0.0   # No gravado
    fecha_cbte: Optional[str] = None   # AAAAMMDD, default hoy
    concepto: int = 1           # 1=Productos, 2=Servicios, 3=Ambos
    moneda_id: str = "PES"      # PES = pesos
    moneda_ctz: float = 1.0
    nro_cbte: Optional[int] = None     # Si es None, el WS asigna el siguiente
    # Para notas de crédito/débito
    cbtes_asoc: list = field(default_factory=list)
    # Alícuotas IVA
    iva: list = field(default_factory=list)
    # Tributos adicionales
    tributos: list = field(default_factory=list)
    # Para conceptos 2 y 3 (servicios)
    fecha_serv_desde: Optional[str] = None
    fecha_serv_hasta: Optional[str] = None
    fecha_vto_pago: Optional[str] = None


class WSFE:
    """
    Cliente del Web Service de Facturación Electrónica v1 (WSFEv1).
    """

    def __init__(self, token: str, sign: str, cuit: str, wsdl_url: str):
        self.token  = token
        self.sign   = sign
        self.cuit   = str(cuit).replace("-", "").strip()
        self.wsdl_url = wsdl_url
        self._client = None

    def _get_client(self) -> zeep.Client:
        if self._client is None:
            self._client = zeep.Client(self.wsdl_url)
        return self._client

    def _auth(self) -> dict:
        return {
            "Token": self.token,
            "Sign":  self.sign,
            "Cuit":  int(self.cuit),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Operaciones públicas
    # ──────────────────────────────────────────────────────────────────────────

    def ultimo_numero(self, tipo_cbte: int, punto_venta: int) -> int:
        """Retorna el último número de comprobante autorizado."""
        client = self._get_client()
        result = client.service.FECompUltimoAutorizado(
            Auth=self._auth(),
            PtoVta=punto_venta,
            CbteTipo=tipo_cbte,
        )
        if result.Errors:
            errs = [e.Msg for e in result.Errors.Err]
            raise WSFEError(f"Error FECompUltimoAutorizado: {'; '.join(errs)}")
        return result.CbteNro

    def solicitar_cae(self, factura: Factura) -> ResultadoCAE:
        """
        Solicita el CAE para una factura.
        Si factura.nro_cbte es None, obtiene el siguiente número automáticamente.
        """
        if factura.nro_cbte is None:
            ultimo = self.ultimo_numero(factura.tipo_cbte, factura.punto_venta)
            factura.nro_cbte = ultimo + 1
            log.info("Próximo número comprobante: %d", factura.nro_cbte)

        fecha = factura.fecha_cbte or datetime.date.today().strftime("%Y%m%d")

        # ── Construir detalle del comprobante ──────────────────────────────────
        cbte_detalle = {
            "Concepto":      factura.concepto,
            "DocTipo":       factura.tipo_doc_receptor,
            "DocNro":        factura.nro_doc_receptor,
            "CbteDesde":     factura.nro_cbte,
            "CbteHasta":     factura.nro_cbte,
            "CbteFch":       fecha,
            "ImpTotal":      round(factura.imp_total, 2),
            "ImpTotConc":    round(factura.imp_tot_conc, 2),
            "ImpNeto":       round(factura.imp_neto, 2),
            "ImpOpEx":       round(factura.imp_op_ex, 2),
            "ImpTrib":       round(factura.imp_trib, 2),
            "ImpIVA":        round(factura.imp_iva, 2),
            "FchServDesde":  factura.fecha_serv_desde,
            "FchServHasta":  factura.fecha_serv_hasta,
            "FchVtoPago":    factura.fecha_vto_pago,
            "MonId":         factura.moneda_id,
            "MonCotiz":      factura.moneda_ctz,
        }

        # ── Comprobantes asociados (NC/ND) ─────────────────────────────────────
        if factura.cbtes_asoc:
            cbte_detalle["CbtesAsoc"] = {
                "CbteAsoc": [
                    {
                        "Tipo":   a["tipo"],
                        "PtoVta": a["punto_venta"],
                        "Nro":    a["nro"],
                    }
                    for a in factura.cbtes_asoc
                ]
            }

        # ── Alícuotas IVA ─────────────────────────────────────────────────────
        if factura.iva:
            cbte_detalle["Iva"] = {
                "AlicIva": [
                    {"Id": i["id"], "BaseImp": round(i["base_imp"], 2), "Importe": round(i["importe"], 2)}
                    for i in factura.iva
                ]
            }

        # ── Tributos ──────────────────────────────────────────────────────────
        if factura.tributos:
            cbte_detalle["Tributos"] = {
                "Tributo": [
                    {
                        "Id":      t["id"],
                        "Desc":    t.get("desc", ""),
                        "BaseImp": round(t["base_imp"], 2),
                        "Alic":    round(t["alic"], 2),
                        "Importe": round(t["importe"], 2),
                    }
                    for t in factura.tributos
                ]
            }

        # ── Llamada al WS ──────────────────────────────────────────────────────
        client = self._get_client()
        try:
            result = client.service.FECAESolicitar(
                Auth=self._auth(),
                FeCAEReq={
                    "FeCabReq": {
                        "CantReg":  1,
                        "PtoVta":   factura.punto_venta,
                        "CbteTipo": factura.tipo_cbte,
                    },
                    "FeDetReq": {
                        "FECAEDetRequest": cbte_detalle,
                    },
                },
            )
        except zeep.exceptions.Fault as e:
            raise WSFEError(f"Error SOAP FECAESolicitar: {e}") from e

        return self._parse_resultado(result, factura.tipo_cbte, factura.punto_venta)

    def consultar_comprobante(self, tipo_cbte: int, punto_venta: int, nro_cbte: int) -> dict:
        """Consulta los datos de un comprobante ya emitido."""
        client = self._get_client()
        result = client.service.FECompConsultar(
            Auth=self._auth(),
            FeCompConsReq={
                "CbteTipo": tipo_cbte,
                "PtoVta":   punto_venta,
                "CbteNro":  nro_cbte,
            },
        )
        return zeep.helpers.serialize_object(result)

    def verificar_servidor(self) -> bool:
        """Verifica conectividad con el servidor WSFE."""
        try:
            client = self._get_client()
            result = client.service.FEDummy()
            return (
                result.AppServer == "OK"
                and result.DbServer == "OK"
                and result.AuthServer == "OK"
            )
        except Exception as e:
            log.error("Error verificando servidor WSFE: %s", e)
            return False

    def tipos_cbte(self) -> list:
        """Retorna tipos de comprobante habilitados para el CUIT."""
        client = self._get_client()
        result = client.service.FEParamGetTiposCbte(Auth=self._auth())
        return zeep.helpers.serialize_object(result.ResultGet.CbteTipo)

    def puntos_venta(self) -> list:
        """Retorna puntos de venta habilitados para el CUIT."""
        client = self._get_client()
        result = client.service.FEParamGetPtosVenta(Auth=self._auth())
        pvs = result.ResultGet
        if pvs is None:
            return []
        return zeep.helpers.serialize_object(pvs.PtoVenta)

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers internos
    # ──────────────────────────────────────────────────────────────────────────

    def _parse_resultado(self, result, tipo_cbte: int, punto_venta: int) -> ResultadoCAE:
        """Parsea la respuesta de FECAESolicitar."""
        observaciones = []
        errores = []

        # Errores a nivel cabecera
        if result.Errors:
            for err in (result.Errors.Err or []):
                errores.append(f"[{err.Code}] {err.Msg}")

        # Detalle de la respuesta
        det = None
        if result.FeDetResp and result.FeDetResp.FECAEDetResponse:
            det = result.FeDetResp.FECAEDetResponse[0]

        if det is None:
            raise WSFEError(f"Sin respuesta de detalle. Errores: {'; '.join(errores)}")

        resultado = det.Resultado or "R"

        if det.Observaciones:
            for obs in (det.Observaciones.Obs or []):
                observaciones.append(f"[{obs.Code}] {obs.Msg}")

        if det.Errors:
            for err in (det.Errors.Err or []):
                errores.append(f"[{err.Code}] {err.Msg}")

        cae          = det.CAE or ""
        cae_fecha_vto = det.CAEFchVto or ""
        aprobado     = (resultado == "A") and bool(cae)

        if not aprobado:
            log.warning("CAE rechazado. Errores: %s | Obs: %s", errores, observaciones)
        else:
            log.info("CAE aprobado: %s (vto %s)", cae, cae_fecha_vto)

        return ResultadoCAE(
            tipo_cbte=tipo_cbte,
            punto_venta=punto_venta,
            nro_desde=det.CbteDesde,
            nro_hasta=det.CbteHasta,
            cae=cae,
            cae_fecha_vto=cae_fecha_vto,
            resultado=resultado,
            observaciones=observaciones,
            errores=errores,
            aprobado=aprobado,
        )
