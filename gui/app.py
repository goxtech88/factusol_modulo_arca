"""
GUI Principal - Módulo ARCA para Factusol
Tkinter: Modo Manual (por serie) y Modo Online (automático con ON/OFF).
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import datetime
import logging
import queue
from typing import Optional

import config
from afip.fecha_cbte import describir_rango_valido
from motor_cae import MotorCAE, ResultadoProcesamiento
from factusol.db import FactusolDB, FacturaFactusol, FactusolDBError
from factusol.monitor import FactusolMonitor

log = logging.getLogger(__name__)

# ── Paleta de colores ─────────────────────────────────────────────────────────
CLR_BG      = "#1e1e2e"
CLR_PANEL   = "#2a2a3e"
CLR_ACCENT  = "#7c5cbf"
CLR_GREEN   = "#50fa7b"
CLR_RED     = "#ff5555"
CLR_YELLOW  = "#f1fa8c"
CLR_CYAN    = "#8be9fd"
CLR_WHITE   = "#f8f8f2"
CLR_GRAY    = "#6272a4"
CLR_HEADER  = "#bd93f9"
CLR_ORANGE  = "#ffb86c"


class AppARCA(tk.Tk):
    """Ventana principal del módulo ARCA."""

    def __init__(self):
        super().__init__()
        self.title("ARCA - Facturación Electrónica AFIP | Factusol")
        self.geometry("1150x750")
        self.minsize(920, 620)
        self.configure(bg=CLR_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._queue: queue.Queue = queue.Queue()
        self._motor: Optional[MotorCAE] = None
        self._monitor: Optional[FactusolMonitor] = None
        self._modo_online_activo = False
        self._cnt_procesadas = 0
        self._cnt_aprobadas  = 0
        self._cnt_rechazadas = 0
        self._facturas_map: dict[str, FacturaFactusol] = {}

        self._build_ui()
        self._poll_queue()

    # ──────────────────────────────────────────────────────────────────────────
    # Construcción de la interfaz
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_config_bar()

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=CLR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CLR_PANEL, foreground=CLR_WHITE,
                        padding=[14, 7], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", CLR_ACCENT)])

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self._tab_manual = tk.Frame(self._notebook, bg=CLR_BG)
        self._tab_online = tk.Frame(self._notebook, bg=CLR_BG)
        self._tab_log    = tk.Frame(self._notebook, bg=CLR_BG)

        self._notebook.add(self._tab_manual, text="  Manual  ")
        self._notebook.add(self._tab_online, text="  Online (Automático)  ")
        self._notebook.add(self._tab_log,    text="  Log  ")

        self._build_tab_manual()
        self._build_tab_online()
        self._build_tab_log()
        self._build_status_bar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=CLR_ACCENT, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(
            hdr, text="  ARCA · Facturación Electrónica AFIP",
            font=("Segoe UI", 15, "bold"), bg=CLR_ACCENT, fg=CLR_WHITE
        ).pack(side=tk.LEFT, padx=16)

        self._lbl_env = tk.Label(
            hdr,
            text=f"[ {config.AFIP_ENV.upper()} ]",
            font=("Segoe UI", 11, "bold"), bg=CLR_ACCENT,
            fg=CLR_YELLOW if config.AFIP_ENV == "homo" else CLR_GREEN
        )
        self._lbl_env.pack(side=tk.RIGHT, padx=16)

        tk.Label(
            hdr, text=f"CUIT: {config.AFIP_CUIT or 'No configurado'}",
            font=("Segoe UI", 10), bg=CLR_ACCENT, fg=CLR_WHITE
        ).pack(side=tk.RIGHT, padx=8)

    def _build_config_bar(self):
        bar = tk.Frame(self, bg=CLR_PANEL, height=40)
        bar.pack(fill=tk.X, padx=10, pady=(6, 0))
        bar.pack_propagate(False)

        tk.Label(bar, text="BD Factusol (.accdb/.mdb):",
                 bg=CLR_PANEL, fg=CLR_GRAY, font=("Segoe UI", 9)
                 ).pack(side=tk.LEFT, padx=(10, 4), pady=8)

        self._var_mdb = tk.StringVar(value=config.FACTUSOL_MDB)
        ent = tk.Entry(bar, textvariable=self._var_mdb, width=52,
                       bg=CLR_BG, fg=CLR_WHITE, insertbackground=CLR_WHITE,
                       relief=tk.FLAT, font=("Consolas", 9))
        ent.pack(side=tk.LEFT, padx=4, pady=8)

        tk.Button(
            bar, text="...", bg=CLR_PANEL, fg=CLR_WHITE,
            relief=tk.FLAT, cursor="hand2",
            command=self._seleccionar_mdb
        ).pack(side=tk.LEFT, padx=2)

        # Indicador de conexión AFIP
        self._lbl_conexion = tk.Label(
            bar, text="●", bg=CLR_PANEL, fg=CLR_GRAY, font=("Segoe UI", 16)
        )
        self._lbl_conexion.pack(side=tk.RIGHT, padx=4)

        tk.Button(
            bar, text="Verificar AFIP", bg=CLR_ACCENT, fg=CLR_WHITE,
            relief=tk.FLAT, cursor="hand2", font=("Segoe UI", 9, "bold"),
            command=self._verificar_afip_async
        ).pack(side=tk.RIGHT, padx=(0, 6), pady=5)

        # Rango válido de fechas
        tk.Label(
            bar, text=describir_rango_valido(),
            bg=CLR_PANEL, fg=CLR_GRAY, font=("Segoe UI", 8)
        ).pack(side=tk.RIGHT, padx=20)

    # ── TAB MANUAL ─────────────────────────────────────────────────────────────

    def _build_tab_manual(self):
        frame = self._tab_manual

        # ── Selector de serie ─────────────────────────────────────────────────
        serie_frame = tk.Frame(frame, bg=CLR_PANEL)
        serie_frame.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(serie_frame, text="Serie:", bg=CLR_PANEL, fg=CLR_WHITE,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(10, 4), pady=6)

        self._var_tipo_serie = tk.StringVar(value="FA")
        tipos = ["FA", "FB", "FC", "FM", "NCA", "NCB", "NCC", "NDA", "NDB", "NDC"]
        cb_tipo = ttk.Combobox(serie_frame, textvariable=self._var_tipo_serie,
                               values=tipos, width=6, state="readonly",
                               font=("Segoe UI", 10))
        cb_tipo.pack(side=tk.LEFT, padx=4, pady=6)

        tk.Label(serie_frame, text="Pto. Venta:", bg=CLR_PANEL, fg=CLR_WHITE,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 4))

        self._var_pv_serie = tk.IntVar(value=1)
        spin = tk.Spinbox(serie_frame, from_=1, to=9999, textvariable=self._var_pv_serie,
                          width=5, bg=CLR_BG, fg=CLR_WHITE,
                          insertbackground=CLR_WHITE, relief=tk.FLAT,
                          font=("Segoe UI", 10), buttonbackground=CLR_PANEL)
        spin.pack(side=tk.LEFT, padx=4, pady=6)

        tk.Button(
            serie_frame, text="📋 Cargar serie",
            bg=CLR_ACCENT, fg=CLR_WHITE, relief=tk.FLAT,
            cursor="hand2", font=("Segoe UI", 10, "bold"),
            command=self._cargar_serie
        ).pack(side=tk.LEFT, padx=10, pady=6)

        tk.Button(
            serie_frame, text="🔄 Todas las pendientes",
            bg=CLR_PANEL, fg=CLR_CYAN, relief=tk.FLAT,
            cursor="hand2", font=("Segoe UI", 10),
            command=self._cargar_todas_pendientes
        ).pack(side=tk.LEFT, padx=4, pady=6)

        # ── Barra de acciones ─────────────────────────────────────────────────
        actions = tk.Frame(frame, bg=CLR_BG)
        actions.pack(fill=tk.X, padx=10, pady=(0, 4))

        tk.Button(
            actions, text="✓  CAE para seleccionadas",
            bg="#28a745", fg=CLR_WHITE, relief=tk.FLAT,
            cursor="hand2", font=("Segoe UI", 10, "bold"),
            command=self._procesar_seleccionadas
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            actions, text="✓  CAE para todas las cargadas",
            bg="#17a2b8", fg=CLR_WHITE, relief=tk.FLAT,
            cursor="hand2", font=("Segoe UI", 10, "bold"),
            command=self._procesar_todas
        ).pack(side=tk.LEFT, padx=4)

        self._lbl_cargadas = tk.Label(
            actions, text="", bg=CLR_BG, fg=CLR_GRAY, font=("Segoe UI", 9)
        )
        self._lbl_cargadas.pack(side=tk.RIGHT, padx=10)

        # ── Tabla de facturas ─────────────────────────────────────────────────
        cols = ("ID", "Tipo", "Número", "Fecha", "Receptor", "CUIT", "Cond. IVA", "Total $", "Estado CAE", "CAE")
        self._tree = ttk.Treeview(frame, columns=cols, show="headings",
                                   selectmode="extended", height=18)
        widths = (45, 55, 120, 85, 190, 115, 155, 95, 90, 155)
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, minwidth=35, anchor=tk.W)

        style = ttk.Style()
        style.configure("Treeview", background=CLR_PANEL, foreground=CLR_WHITE,
                        rowheight=24, fieldbackground=CLR_PANEL, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=CLR_ACCENT,
                        foreground=CLR_WHITE, font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#5a4a8a")])

        self._tree.tag_configure("pendiente",  foreground=CLR_YELLOW)
        self._tree.tag_configure("aprobado",   foreground=CLR_GREEN)
        self._tree.tag_configure("rechazado",  foreground=CLR_RED)
        self._tree.tag_configure("procesando", foreground=CLR_ORANGE)

        scrollbar_v = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self._tree.yview)
        scrollbar_h = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 0))
        scrollbar_v.pack(side=tk.LEFT, fill=tk.Y, pady=(0, 0))
        # Nota: scrollbar_h al pie, no en el pack lateral

    # ── TAB ONLINE (Automático) ────────────────────────────────────────────────

    def _build_tab_online(self):
        frame = self._tab_online

        # ── Panel ON/OFF principal ────────────────────────────────────────────
        toggle_frame = tk.LabelFrame(
            frame, text=" Modo Online — Monitoreo Automático ",
            bg=CLR_BG, fg=CLR_HEADER,
            font=("Segoe UI", 12, "bold"), pady=14, padx=16
        )
        toggle_frame.pack(fill=tk.X, padx=18, pady=18)

        # Indicador LED + estado
        led_row = tk.Frame(toggle_frame, bg=CLR_BG)
        led_row.pack(fill=tk.X, pady=(0, 10))

        self._canvas_led = tk.Canvas(led_row, width=28, height=28, bg=CLR_BG, highlightthickness=0)
        self._canvas_led.pack(side=tk.LEFT, padx=(0, 12))
        self._led = self._canvas_led.create_oval(4, 4, 24, 24, fill=CLR_GRAY, outline="")

        self._lbl_estado_online = tk.Label(
            led_row, text="● OFFLINE  —  Monitor detenido",
            bg=CLR_BG, fg=CLR_GRAY, font=("Segoe UI", 14, "bold")
        )
        self._lbl_estado_online.pack(side=tk.LEFT)

        # Configuración intervalo
        cfg_row = tk.Frame(toggle_frame, bg=CLR_BG)
        cfg_row.pack(fill=tk.X, pady=4)

        tk.Label(cfg_row, text="Revisar Factusol cada (seg):",
                 bg=CLR_BG, fg=CLR_WHITE, font=("Segoe UI", 10)
                 ).pack(side=tk.LEFT)

        self._var_intervalo = tk.IntVar(value=config.POLL_INTERVAL)
        tk.Spinbox(cfg_row, from_=5, to=600, textvariable=self._var_intervalo,
                   width=5, bg=CLR_PANEL, fg=CLR_WHITE,
                   insertbackground=CLR_WHITE, relief=tk.FLAT,
                   font=("Segoe UI", 10), buttonbackground=CLR_PANEL
                   ).pack(side=tk.LEFT, padx=10)

        # Botón ON/OFF grande
        self._btn_toggle = tk.Button(
            toggle_frame,
            text="▶  ACTIVAR MODO ONLINE",
            bg=CLR_GREEN, fg="#000000", relief=tk.FLAT,
            cursor="hand2", font=("Segoe UI", 13, "bold"),
            width=24,
            command=self._toggle_modo_online
        )
        self._btn_toggle.pack(pady=10)

        # Descripción
        tk.Label(
            frame,
            text=(
                "Cuando el modo online está ACTIVO:\n"
                "  • El módulo permanece en espera en segundo plano\n"
                "  • Apenas se graba una factura en Factusol → verifica CUIT → consulta padrón → valida condición fiscal → obtiene CAE → guarda en Factusol\n"
                "  • Fechas fuera del rango AFIP (±5 días) se ajustan automáticamente al límite y se notifica"
            ),
            bg=CLR_BG, fg=CLR_GRAY, font=("Segoe UI", 10), justify=tk.LEFT
        ).pack(padx=18, pady=4, anchor=tk.W)

        # Contadores
        self._var_contador = tk.StringVar(
            value="Procesadas: 0   |   Aprobadas: 0   |   Rechazadas: 0"
        )
        tk.Label(frame, textvariable=self._var_contador,
                 bg=CLR_BG, fg=CLR_CYAN, font=("Segoe UI", 11, "bold")
                 ).pack(padx=18, pady=6, anchor=tk.W)

        # Log de actividad online
        tk.Label(frame, text="Actividad del monitor:",
                 bg=CLR_BG, fg=CLR_GRAY, font=("Segoe UI", 9)
                 ).pack(padx=18, anchor=tk.W)

        self._txt_auto = scrolledtext.ScrolledText(
            frame, height=14, bg=CLR_PANEL, fg=CLR_WHITE,
            font=("Consolas", 9), state=tk.DISABLED, relief=tk.FLAT
        )
        self._txt_auto.pack(fill=tk.BOTH, expand=True, padx=18, pady=(2, 12))
        self._txt_auto.tag_configure("info",    foreground=CLR_WHITE)
        self._txt_auto.tag_configure("ok",      foreground=CLR_GREEN)
        self._txt_auto.tag_configure("error",   foreground=CLR_RED)
        self._txt_auto.tag_configure("warning", foreground=CLR_YELLOW)
        self._txt_auto.tag_configure("ts",      foreground=CLR_GRAY)

    # ── TAB LOG ────────────────────────────────────────────────────────────────

    def _build_tab_log(self):
        frame = self._tab_log

        tk.Button(
            frame, text="Limpiar", bg=CLR_PANEL, fg=CLR_WHITE,
            relief=tk.FLAT, cursor="hand2",
            command=self._limpiar_log
        ).pack(anchor=tk.E, padx=10, pady=6)

        self._txt_log = scrolledtext.ScrolledText(
            frame, bg=CLR_PANEL, fg=CLR_WHITE,
            font=("Consolas", 9), state=tk.DISABLED, relief=tk.FLAT
        )
        self._txt_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self._txt_log.tag_configure("INFO",    foreground=CLR_WHITE)
        self._txt_log.tag_configure("ERROR",   foreground=CLR_RED)
        self._txt_log.tag_configure("WARNING", foreground=CLR_YELLOW)
        self._txt_log.tag_configure("DEBUG",   foreground=CLR_GRAY)
        self._txt_log.tag_configure("ts",      foreground=CLR_GRAY)

    def _build_status_bar(self):
        self._status_bar = tk.Label(
            self, text="Listo", bg=CLR_PANEL, fg=CLR_GRAY,
            font=("Segoe UI", 9), anchor=tk.W, padx=10
        )
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ──────────────────────────────────────────────────────────────────────────
    # Acciones — Configuración
    # ──────────────────────────────────────────────────────────────────────────

    def _seleccionar_mdb(self):
        path = filedialog.askopenfilename(
            title="Seleccionar base de datos Factusol",
            filetypes=[
                ("Access Database", "*.accdb *.mdb"),
                ("Todos", "*.*")
            ]
        )
        if path:
            self._var_mdb.set(path)

    def _get_mdb(self) -> str:
        return self._var_mdb.get().strip()

    def _get_motor(self) -> MotorCAE:
        self._motor = MotorCAE(self._get_mdb())
        return self._motor

    # ──────────────────────────────────────────────────────────────────────────
    # Acciones — Modo Manual
    # ──────────────────────────────────────────────────────────────────────────

    def _cargar_serie(self):
        tipo = self._var_tipo_serie.get()
        pv   = self._var_pv_serie.get()
        self._status(f"Cargando serie {tipo} PV {pv:04d}...")
        threading.Thread(
            target=self._thr_cargar_serie, args=(pv, tipo), daemon=True
        ).start()

    def _cargar_todas_pendientes(self):
        self._status("Cargando todas las facturas pendientes...")
        threading.Thread(target=self._thr_cargar_todas, daemon=True).start()

    def _thr_cargar_serie(self, pv: int, tipo: str):
        try:
            with FactusolDB(self._get_mdb()) as db:
                facturas = db.obtener_facturas_por_serie(pv, tipo)
            self._queue.put(("load_facturas", (facturas, f"Serie {tipo} PV {pv:04d}")))
        except FactusolDBError as e:
            self._queue.put(("error_msg", f"Error cargando serie: {e}"))

    def _thr_cargar_todas(self):
        try:
            with FactusolDB(self._get_mdb()) as db:
                facturas = db.obtener_facturas_pendientes()
            self._queue.put(("load_facturas", (facturas, "Todas las pendientes")))
        except FactusolDBError as e:
            self._queue.put(("error_msg", f"Error cargando facturas: {e}"))

    def _mostrar_facturas(self, facturas: list, titulo: str = ""):
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._facturas_map.clear()

        for f in facturas:
            cae_str = f.cae or ""
            estado  = "Aprobado" if f.cae else "Pendiente"
            tag     = "aprobado" if f.cae else "pendiente"
            iid = self._tree.insert("", tk.END, values=(
                f.id_factura,
                f.tipo,
                f.numero,
                f.fecha.strftime("%d/%m/%Y") if f.fecha else "",
                f.nombre_receptor,
                f.cuit_receptor,
                f.condicion_iva_receptor,
                f"{f.imp_total:,.2f}",
                estado,
                cae_str,
            ), tags=(tag,))
            self._facturas_map[iid] = f

        n = len(facturas)
        self._lbl_cargadas.config(text=f"{titulo} — {n} factura(s) cargadas")
        self._status(f"{n} factura(s) cargadas" + (f" — {titulo}" if titulo else ""))

    def _procesar_seleccionadas(self):
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("Sin selección", "Seleccione al menos una factura de la lista")
            return
        facturas = [self._facturas_map[iid] for iid in selected if iid in self._facturas_map]
        self._iniciar_procesamiento(facturas)

    def _procesar_todas(self):
        facturas = list(self._facturas_map.values())
        if not facturas:
            messagebox.showinfo("Sin facturas", "No hay facturas cargadas en la tabla")
            return
        pendientes = [f for f in facturas if not f.cae]
        if not pendientes:
            messagebox.showinfo("Sin pendientes", "Todas las facturas ya tienen CAE")
            return
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Obtener CAE para las {len(pendientes)} facturas pendientes?"
        ):
            return
        self._iniciar_procesamiento(pendientes)

    def _iniciar_procesamiento(self, facturas: list):
        if not facturas:
            return
        self._status(f"Procesando {len(facturas)} factura(s)...")
        # Marcar como "Procesando" en la tabla
        for iid, f in self._facturas_map.items():
            if f in facturas:
                vals = list(self._tree.item(iid, "values"))
                vals[8] = "Procesando..."
                self._tree.item(iid, values=vals, tags=("procesando",))
        threading.Thread(
            target=self._thr_procesar, args=(facturas,), daemon=True
        ).start()

    def _thr_procesar(self, facturas: list):
        motor = self._get_motor()
        for factura in facturas:
            self._queue.put(("status", f"Procesando {factura.tipo} {factura.numero}..."))
            try:
                res = motor.procesar_factura(factura)
                self._queue.put(("resultado", res))
            except Exception as e:
                log.error("Error procesando %s: %s", factura.numero, e, exc_info=True)
                self._queue.put(("error_log", f"Error procesando {factura.numero}: {e}"))
        self._queue.put(("status", "Procesamiento manual finalizado"))

    # ──────────────────────────────────────────────────────────────────────────
    # Acciones — Modo Online
    # ──────────────────────────────────────────────────────────────────────────

    def _toggle_modo_online(self):
        if self._modo_online_activo:
            self._desactivar_online()
        else:
            self._activar_online()

    def _activar_online(self):
        mdb = self._get_mdb()
        if not mdb:
            messagebox.showerror("Error", "Configure la ruta de la base de datos Factusol")
            return
        if not config.AFIP_CUIT:
            messagebox.showerror("Error", "Configure el CUIT emisor en el archivo .env o config.py")
            return

        intervalo = self._var_intervalo.get()
        self._monitor = FactusolMonitor(
            mdb_path               = mdb,
            poll_interval          = intervalo,
            callback_nueva_factura = lambda f: self._queue.put(("auto_factura", f)),
            callback_estado        = lambda msg, nivel="info": self._queue.put(("auto_estado", (msg, nivel))),
        )
        self._monitor.iniciar()
        self._modo_online_activo = True

        # UI → ONLINE
        self._btn_toggle.config(
            text="■  DESACTIVAR MODO ONLINE",
            bg=CLR_RED, fg=CLR_WHITE
        )
        self._canvas_led.itemconfig(self._led, fill=CLR_GREEN)
        self._lbl_estado_online.config(
            text="● ONLINE  —  Esperando nuevas facturas...",
            fg=CLR_GREEN
        )
        self._log_auto("Modo Online activado. Esperando facturas en Factusol...", "info")
        self._status("Modo Online ACTIVO")
        self._parpadear_led()

    def _desactivar_online(self):
        if self._monitor:
            self._monitor.detener()
            self._monitor = None
        self._modo_online_activo = False

        # UI → OFFLINE
        self._btn_toggle.config(
            text="▶  ACTIVAR MODO ONLINE",
            bg=CLR_GREEN, fg="#000000"
        )
        self._canvas_led.itemconfig(self._led, fill=CLR_GRAY)
        self._lbl_estado_online.config(
            text="● OFFLINE  —  Monitor detenido",
            fg=CLR_GRAY
        )
        self._log_auto("Modo Online desactivado.", "warning")
        self._status("Modo Online INACTIVO")

    def _parpadear_led(self):
        if not self._modo_online_activo:
            self._canvas_led.itemconfig(self._led, fill=CLR_GRAY)
            return
        color = self._canvas_led.itemcget(self._led, "fill")
        self._canvas_led.itemconfig(self._led, fill=CLR_GREEN if color != CLR_GREEN else CLR_BG)
        self.after(900, self._parpadear_led)

    def _procesar_factura_online(self, factura: FacturaFactusol):
        """Procesa una factura detectada en modo online (en hilo separado)."""
        self._log_auto(
            f"Nueva: {factura.tipo} {factura.numero} — {factura.nombre_receptor} — ${factura.imp_total:,.2f}",
            "info"
        )
        try:
            motor = self._get_motor()
            res   = motor.procesar_factura(factura)

            self._cnt_procesadas += 1
            if res.exitoso:
                self._cnt_aprobadas += 1
                self._log_auto(f"✓ CAE: {res.cae}  (vto {res.cae_fecha_vto})", "ok")
                if res.advertencias:
                    for adv in res.advertencias:
                        self._log_auto(f"  ⚠ {adv}", "warning")
                if res.persona_fiscal:
                    self._log_auto(
                        f"  → {res.persona_fiscal.nombre} | {res.persona_fiscal.condicion_iva}",
                        "info"
                    )
            else:
                self._cnt_rechazadas += 1
                self._log_auto(
                    f"✗ FALLO [{res.etapa_fallo}]: {'; '.join(res.errores)}",
                    "error"
                )
                if res.advertencias:
                    for adv in res.advertencias:
                        self._log_auto(f"  ⚠ {adv}", "warning")

            self._queue.put(("actualizar_contador", None))

        except Exception as e:
            log.error("Error en procesamiento online: %s", e, exc_info=True)
            self._log_auto(f"✗ Error inesperado: {e}", "error")

    # ──────────────────────────────────────────────────────────────────────────
    # Verificación AFIP
    # ──────────────────────────────────────────────────────────────────────────

    def _verificar_afip_async(self):
        self._lbl_conexion.config(fg=CLR_YELLOW)
        self._status("Verificando conexión con AFIP...")
        threading.Thread(target=self._thr_verificar_afip, daemon=True).start()

    def _thr_verificar_afip(self):
        try:
            motor = self._get_motor()
            ok, msg = motor.verificar_conexion_afip()
            self._queue.put(("conexion_afip", (ok, msg)))
        except Exception as e:
            self._queue.put(("conexion_afip", (False, str(e))))

    # ──────────────────────────────────────────────────────────────────────────
    # Cola de mensajes (thread-safe)
    # ──────────────────────────────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                tipo, datos = self._queue.get_nowait()

                if tipo == "load_facturas":
                    facturas, titulo = datos
                    self._mostrar_facturas(facturas, titulo)

                elif tipo == "status":
                    self._status(datos)

                elif tipo == "error_msg":
                    self._status(f"Error: {datos}")
                    messagebox.showerror("Error", datos)

                elif tipo == "error_log":
                    self._log(datos, "ERROR")

                elif tipo == "resultado":
                    self._actualizar_fila(datos)

                elif tipo == "auto_factura":
                    threading.Thread(
                        target=self._procesar_factura_online,
                        args=(datos,), daemon=True
                    ).start()

                elif tipo == "auto_estado":
                    msg, nivel = datos
                    self._log_auto(msg, nivel)

                elif tipo == "conexion_afip":
                    ok, msg = datos
                    self._lbl_conexion.config(fg=CLR_GREEN if ok else CLR_RED)
                    self._status(msg)
                    self._log(msg, "INFO" if ok else "ERROR")

                elif tipo == "actualizar_contador":
                    self._var_contador.set(
                        f"Procesadas: {self._cnt_procesadas}   |   "
                        f"Aprobadas: {self._cnt_aprobadas}   |   "
                        f"Rechazadas: {self._cnt_rechazadas}"
                    )

        except queue.Empty:
            pass
        self.after(200, self._poll_queue)

    # ──────────────────────────────────────────────────────────────────────────
    # Actualización de UI
    # ──────────────────────────────────────────────────────────────────────────

    def _actualizar_fila(self, res: ResultadoProcesamiento):
        """Actualiza la fila del Treeview tras obtener el CAE."""
        for iid, f in self._facturas_map.items():
            if f.id_factura == res.factura.id_factura:
                vals = list(self._tree.item(iid, "values"))
                if res.exitoso:
                    vals[8] = "Aprobado"
                    vals[9] = res.cae
                    self._tree.item(iid, values=vals, tags=("aprobado",))
                    msg = f"✓ {f.tipo} {f.numero} → CAE {res.cae}"
                    self._log(msg, "INFO")
                    # Mostrar advertencias de fecha
                    for adv in res.advertencias:
                        self._log(f"  ⚠ {adv}", "WARNING")
                else:
                    vals[8] = "Rechazado"
                    self._tree.item(iid, values=vals, tags=("rechazado",))
                    self._log(
                        f"✗ {f.tipo} {f.numero} → {'; '.join(res.errores)}",
                        "ERROR"
                    )
                break

    def _status(self, msg: str):
        self._status_bar.config(text=f"  {msg}")

    def _log(self, msg: str, nivel: str = "INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._txt_log.config(state=tk.NORMAL)
        self._txt_log.insert(tk.END, f"[{ts}] ", "ts")
        self._txt_log.insert(tk.END, f"{msg}\n", nivel)
        self._txt_log.see(tk.END)
        self._txt_log.config(state=tk.DISABLED)

    def _log_auto(self, msg: str, nivel: str = "info"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._txt_auto.config(state=tk.NORMAL)
        self._txt_auto.insert(tk.END, f"[{ts}] ", "ts")
        self._txt_auto.insert(tk.END, f"{msg}\n", nivel)
        self._txt_auto.see(tk.END)
        self._txt_auto.config(state=tk.DISABLED)
        self._log(msg, nivel.upper())

    def _limpiar_log(self):
        self._txt_log.config(state=tk.NORMAL)
        self._txt_log.delete("1.0", tk.END)
        self._txt_log.config(state=tk.DISABLED)

    # ──────────────────────────────────────────────────────────────────────────
    # Cierre
    # ──────────────────────────────────────────────────────────────────────────

    def on_closing(self):
        if self._modo_online_activo:
            if not messagebox.askyesno(
                "Monitor activo",
                "El modo Online está activo. ¿Desea detenerlo y salir?"
            ):
                return
            if self._monitor:
                self._monitor.detener()
        self.destroy()
