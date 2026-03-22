"""
Monitor de Factusol - Modo Automático.
Detecta nuevas facturas guardadas en Factusol y dispara la obtención de CAE.
"""
import os
import time
import logging
import threading
import datetime
from typing import Callable, Optional, Set
from pathlib import Path

log = logging.getLogger(__name__)


class FactusolMonitor:
    """
    Monitorea la base de datos de Factusol buscando facturas nuevas sin CAE.

    Estrategia dual:
      1. Polling de la BD cada N segundos buscando facturas sin CAE (principal).
      2. Detección de modificación del archivo .MDB por timestamp (secundaria).

    Cuando detecta una factura nueva → llama a callback_nueva_factura(factura).
    """

    def __init__(
        self,
        mdb_path: str,
        poll_interval: int,
        callback_nueva_factura: Callable,
        callback_estado: Optional[Callable] = None,
    ):
        """
        Args:
            mdb_path: Ruta al archivo .MDB de Factusol.
            poll_interval: Segundos entre cada revisión.
            callback_nueva_factura: Función a llamar con cada FacturaFactusol nueva.
            callback_estado: Función para reportar mensajes de estado (opcional).
        """
        self.mdb_path   = mdb_path
        self.poll_interval = poll_interval
        self.callback   = callback_nueva_factura
        self.cb_estado  = callback_estado or (lambda msg, nivel="info": None)

        self._running   = False
        self._thread: Optional[threading.Thread] = None
        self._ids_procesados: Set[int] = set()
        self._ultimo_mtime: float = 0.0
        self._lock = threading.Lock()

    # ──────────────────────────────────────────────────────────────────────────
    # Control del monitor
    # ──────────────────────────────────────────────────────────────────────────

    def iniciar(self):
        """Inicia el monitor en un hilo background."""
        if self._running:
            log.warning("Monitor ya está corriendo")
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._loop,
            name="FactusolMonitor",
            daemon=True,
        )
        self._thread.start()
        log.info("Monitor Factusol iniciado (intervalo: %ds)", self.poll_interval)
        self.cb_estado(
            f"Monitor iniciado. Revisando cada {self.poll_interval}s...",
            "info"
        )

    def detener(self):
        """Detiene el monitor."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.poll_interval + 2)
        log.info("Monitor Factusol detenido")
        self.cb_estado("Monitor detenido.", "warning")

    @property
    def corriendo(self) -> bool:
        return self._running and (self._thread is not None and self._thread.is_alive())

    def marcar_procesado(self, id_factura: int):
        """Marca una factura como procesada para no re-procesarla."""
        with self._lock:
            self._ids_procesados.add(id_factura)

    def limpiar_procesados(self):
        """Limpia el set de IDs procesados (útil para re-procesar si falla)."""
        with self._lock:
            self._ids_procesados.clear()

    # ──────────────────────────────────────────────────────────────────────────
    # Loop principal
    # ──────────────────────────────────────────────────────────────────────────

    def _loop(self):
        """Loop principal del monitor."""
        from factusol.db import FactusolDB, FactusolDBError

        log.info("Loop monitor iniciado")
        db = FactusolDB(self.mdb_path)

        while self._running:
            try:
                # Detectar cambio en el archivo MDB
                mtime_actual = self._get_mtime()
                if mtime_actual != self._ultimo_mtime:
                    self._ultimo_mtime = mtime_actual
                    log.debug("Cambio detectado en MDB, consultando BD...")

                # Siempre consultar BD (el polling es la fuente de verdad)
                try:
                    facturas_pendientes = db.obtener_facturas_pendientes()
                except FactusolDBError as e:
                    log.error("Error consultando BD Factusol: %s", e)
                    self.cb_estado(f"Error BD: {e}", "error")
                    # Intentar reconectar
                    try:
                        db.disconnect()
                    except Exception:
                        pass
                    time.sleep(self.poll_interval)
                    continue

                # Filtrar las que ya procesamos
                with self._lock:
                    nuevas = [
                        f for f in facturas_pendientes
                        if f.id_factura not in self._ids_procesados
                    ]

                if nuevas:
                    log.info("Detectadas %d facturas nuevas sin CAE", len(nuevas))
                    self.cb_estado(
                        f"Detectadas {len(nuevas)} facturas pendientes de CAE",
                        "info"
                    )
                    for factura in nuevas:
                        if not self._running:
                            break
                        # Pre-marcar como procesada (evitar doble procesamiento)
                        self.marcar_procesado(factura.id_factura)
                        try:
                            self.callback(factura)
                        except Exception as e:
                            log.error("Error en callback factura %d: %s", factura.id_factura, e)
                            self.cb_estado(f"Error procesando factura {factura.id_factura}: {e}", "error")
                            # Desmarcar para que se reintente
                            with self._lock:
                                self._ids_procesados.discard(factura.id_factura)

            except Exception as e:
                log.error("Error inesperado en monitor: %s", e, exc_info=True)
                self.cb_estado(f"Error inesperado: {e}", "error")

            # Esperar hasta el próximo ciclo
            self._sleep_interruptible(self.poll_interval)

        log.info("Loop monitor finalizado")

    def _get_mtime(self) -> float:
        """Retorna el tiempo de modificación del MDB, o 0 si no existe."""
        try:
            return Path(self.mdb_path).stat().st_mtime
        except (FileNotFoundError, OSError):
            return 0.0

    def _sleep_interruptible(self, seconds: float):
        """Sleep interruptible: verifica _running cada segundo."""
        elapsed = 0.0
        step = 1.0
        while elapsed < seconds and self._running:
            time.sleep(min(step, seconds - elapsed))
            elapsed += step
