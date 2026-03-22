"""
Consulta de Padrón AFIP - Verificación de CUIT y condición fiscal.
Usa servicios A4 (contribuyentes) y A13 (persona completa).
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

import zeep
import zeep.helpers

log = logging.getLogger(__name__)


class PadronError(Exception):
    pass


@dataclass
class PersonaFiscal:
    """Datos fiscales de una persona (física o jurídica) obtenidos del padrón AFIP."""
    cuit: str
    tipo_persona: str           # "FISICA" | "JURIDICA"
    nombre: str
    estado: str                 # "ACTIVO" | "INACTIVO" | etc.
    condicion_iva: str
    condicion_iva_codigo: int
    domicilio_fiscal: str
    actividades: list = field(default_factory=list)
    es_valido: bool = True
    error: Optional[str] = None

    def __str__(self):
        return (
            f"CUIT: {self.cuit} | {self.nombre} | "
            f"{self.condicion_iva} | Estado: {self.estado}"
        )


class PadronAFIP:
    """
    Cliente para consultar el Padrón AFIP (A4/A13).
    Verifica CUIT y obtiene condición fiscal.
    """

    # Mapa código AFIP → descripción condición IVA
    CONDICION_IVA_MAP = {
        1:  ("IVA Responsable Inscripto",      "RI"),
        2:  ("IVA Responsable no Inscripto",   "RNI"),
        3:  ("IVA no Responsable",             "NR"),
        4:  ("IVA Sujeto Exento",              "EX"),
        5:  ("Consumidor Final",               "CF"),
        6:  ("Responsable Monotributo",        "MT"),
        7:  ("Sujeto no Categorizado",         "NC"),
        8:  ("Importador del Exterior",        "IE"),
        9:  ("Cliente del Exterior",           "CE"),
        10: ("IVA Liberado – Ley 19.640",      "LL"),
        11: ("RI – Agente de Percepción",      "AP"),
        12: ("Pequeño Contribuyente Eventual", "PE"),
        13: ("Monotributista Social",          "MS"),
        14: ("Pequeño Contribuyente Eventual Social", "ES"),
    }

    def __init__(self, token: str, sign: str, cuit_emisor: str,
                 wsdl_url: str, service: str = "A13"):
        self.token       = token
        self.sign        = sign
        self.cuit_emisor = str(cuit_emisor).replace("-", "").strip()
        self.wsdl_url    = wsdl_url
        self.service     = service
        self._client     = None

    def _get_client(self) -> zeep.Client:
        if self._client is None:
            self._client = zeep.Client(self.wsdl_url)
        return self._client

    def _build_auth(self) -> dict:
        return {
            "token": self.token,
            "sign":  self.sign,
            "cuitRepresentada": int(self.cuit_emisor),
        }

    def consultar(self, cuit: str) -> PersonaFiscal:
        """
        Consulta los datos fiscales de un CUIT en el padrón AFIP.
        Retorna un objeto PersonaFiscal con todos los datos.
        """
        cuit_num = str(cuit).replace("-", "").strip()

        if not self._validar_cuit_formato(cuit_num):
            return PersonaFiscal(
                cuit=cuit_num, tipo_persona="", nombre="", estado="",
                condicion_iva="", condicion_iva_codigo=0, domicilio_fiscal="",
                es_valido=False, error=f"CUIT inválido (formato): {cuit}"
            )

        try:
            client = self._get_client()
            auth   = self._build_auth()

            if self.service == "A4":
                result = client.service.getPersona(auth=auth, idPersona=int(cuit_num))
                return self._parse_a4(result, cuit_num)
            else:
                result = client.service.getPersona(auth=auth, idPersona=int(cuit_num))
                return self._parse_a13(result, cuit_num)

        except zeep.exceptions.Fault as e:
            msg = str(e)
            if "no existe" in msg.lower() or "invalid" in msg.lower():
                return PersonaFiscal(
                    cuit=cuit_num, tipo_persona="", nombre="", estado="INEXISTENTE",
                    condicion_iva="No registrado en AFIP", condicion_iva_codigo=0,
                    domicilio_fiscal="", es_valido=False,
                    error=f"CUIT no encontrado en padrón AFIP"
                )
            raise PadronError(f"Error AFIP Padrón: {e}") from e
        except Exception as e:
            raise PadronError(f"Error consultando padrón: {e}") from e

    def _parse_a13(self, result, cuit: str) -> PersonaFiscal:
        """Parsea respuesta del servicio A13."""
        try:
            persona = result.persona
            if persona is None:
                return PersonaFiscal(
                    cuit=cuit, tipo_persona="", nombre="", estado="INEXISTENTE",
                    condicion_iva="No registrado", condicion_iva_codigo=0,
                    domicilio_fiscal="", es_valido=False,
                    error="CUIT no encontrado en padrón AFIP"
                )

            tipo = getattr(persona, "tipoPersona", "FISICA")
            estado = getattr(persona, "estadoClave", "DESCONOCIDO")

            # Nombre
            if tipo == "FISICA":
                nombre = f"{getattr(persona, 'apellido', '')} {getattr(persona, 'nombre', '')}".strip()
            else:
                nombre = getattr(persona, 'razonSocial', '') or ""

            # Condición IVA
            iva_cod = 0
            iva_desc = "Sin información"
            imp_list = getattr(persona, 'impuesto', None)
            if imp_list:
                for imp in (imp_list if isinstance(imp_list, list) else [imp_list]):
                    if getattr(imp, 'idImpuesto', None) == 30:  # IVA
                        iva_cod = getattr(imp, 'idConcepto', 0)
                        break
            if iva_cod and iva_cod in self.CONDICION_IVA_MAP:
                iva_desc = self.CONDICION_IVA_MAP[iva_cod][0]

            # Domicilio fiscal
            domicilio = ""
            dom = getattr(persona, 'domicilioFiscal', None)
            if dom:
                partes = [
                    getattr(dom, 'direccion', ''),
                    getattr(dom, 'localidad', ''),
                    getattr(dom, 'descripcionProvincia', ''),
                ]
                domicilio = ", ".join(p for p in partes if p)

            # Actividades
            acts = []
            act_list = getattr(persona, 'actividad', None)
            if act_list:
                for act in (act_list if isinstance(act_list, list) else [act_list]):
                    desc = getattr(act, 'descripcionActividad', '') or str(getattr(act, 'idActividad', ''))
                    acts.append(desc)

            return PersonaFiscal(
                cuit=cuit, tipo_persona=tipo, nombre=nombre,
                estado=estado, condicion_iva=iva_desc,
                condicion_iva_codigo=iva_cod, domicilio_fiscal=domicilio,
                actividades=acts, es_valido=(estado == "ACTIVO")
            )

        except Exception as e:
            log.warning("Error parseando respuesta A13: %s", e)
            raise PadronError(f"Error parseando respuesta padrón: {e}") from e

    def _parse_a4(self, result, cuit: str) -> PersonaFiscal:
        """Parsea respuesta del servicio A4 (más simple)."""
        try:
            data = zeep.helpers.serialize_object(result)
            persona = data.get("persona", {}) or {}

            tipo    = persona.get("tipoPersona", "FISICA")
            estado  = persona.get("estadoClave", "DESCONOCIDO")
            nombre  = persona.get("razonSocial") or (
                f"{persona.get('apellido', '')} {persona.get('nombre', '')}".strip()
            )

            categorias = persona.get("categoriasMonotributo", []) or []
            actividades = [str(c.get("idCategoriaMonotributo", "")) for c in categorias]

            imp_list = persona.get("impuestos", []) or []
            iva_cod  = 0
            for imp in imp_list:
                if imp.get("idImpuesto") == 30:
                    iva_cod = imp.get("idConcepto", 0)
                    break

            iva_desc = self.CONDICION_IVA_MAP.get(iva_cod, ("Sin información",))[0] if iva_cod else "Sin información"

            dom = persona.get("domicilioFiscal", {}) or {}
            domicilio = ", ".join(filter(None, [
                dom.get("direccion", ""),
                dom.get("localidad", ""),
                dom.get("descripcionProvincia", ""),
            ]))

            return PersonaFiscal(
                cuit=cuit, tipo_persona=tipo, nombre=nombre, estado=estado,
                condicion_iva=iva_desc, condicion_iva_codigo=iva_cod,
                domicilio_fiscal=domicilio, actividades=actividades,
                es_valido=(estado == "ACTIVO")
            )
        except Exception as e:
            raise PadronError(f"Error parseando respuesta A4: {e}") from e

    @staticmethod
    def _validar_cuit_formato(cuit: str) -> bool:
        """Valida el formato y dígito verificador del CUIT."""
        if not cuit.isdigit() or len(cuit) != 11:
            return False

        # Prefijos válidos
        prefijo = int(cuit[:2])
        if prefijo not in (20, 23, 24, 27, 30, 33, 34):
            return False

        # Dígito verificador
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        total = sum(int(cuit[i]) * factores[i] for i in range(10))
        resto = total % 11
        verificador = 11 - resto if resto not in (0, 1) else (0 if resto == 0 else 9)

        return verificador == int(cuit[10])
