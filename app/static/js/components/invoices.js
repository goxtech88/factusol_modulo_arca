/**
 * Invoices Component
 * - Filtros de fecha: Todos / Hoy / Ayer / Últimos 7 días
 * - Botón Actualizar (refresh desde Factusol)
 * - Ordenamiento por columna (click en header)
 * - Modal de detalle + Consulta Padrón ARCA
 */
const InvoicesComponent = {
    currentPv: null,
    _padronCache: {},
    _allInvoices: [],       // datos cacheados del último fetch
    _caeStatuses: {},       // caché de status CAE por "TIPFAC-CODFAC"
    _sortCol: 'CODFAC',
    _sortAsc: false,
    _dateFilter: 'all',     // all | today | yesterday | last7

    // ── Columnas ordenables ──────────────────────────────────────────────
    COLS: [
        { key: 'CODFAC',   label: 'Nro',     sortable: true  },
        { key: 'FECFAC',   label: 'Fecha',   sortable: true  },
        { key: 'CNOFAC',   label: 'Cliente', sortable: true  },
        { key: 'TOTFAC',   label: 'Total',   sortable: true  },
        { key: 'ESTFAC',   label: 'Estado',  sortable: true  },
        { key: '_cae',     label: 'CAE',     sortable: false },
        { key: '_actions', label: '',        sortable: false },
    ],

    init() {
        document.getElementById('invoice-pv-select')
            .addEventListener('change', () => this.loadInvoices());

        document.getElementById('invoice-search')
            .addEventListener('input', App.debounce(() => this.loadInvoices(), 400));

        // Modal close
        document.querySelectorAll('#invoice-modal .modal-close, #invoice-modal .modal-overlay')
            .forEach(el => el.addEventListener('click', () => this.closeModal()));
    },

    loadPuntosVenta() {
        const select = document.getElementById('invoice-pv-select');
        const pvs = Auth.getPuntosVenta();
        select.innerHTML = pvs.length === 0
            ? '<option value="">Sin puntos de venta</option>'
            : pvs.map(pv =>
                `<option value="${pv.id}" data-serie="${pv.serie_factusol}">
                    ${pv.nombre} (Serie ${pv.serie_factusol} → PV ${pv.punto_venta})
                </option>`).join('');

        if (pvs.length > 0) {
            this.currentPv = pvs[0];
            this.loadInvoices();
        }

        // Sincronizar estado del auto-validate toggle
        this._syncAutoToggle();
    },

    async _syncAutoToggle() {
        try {
            const status = await API.get('/api/arca/auto-validate/status');
            const sw = document.getElementById('invoices-auto-switch');
            if (sw) sw.checked = status.enabled;
        } catch { /* ignore */ }
    },

    async toggleAutoValidate(enabled) {
        try {
            await API.post(`/api/arca/auto-validate/toggle?enabled=${enabled}`);
            App.toast(enabled ? '🤖 Auto-validación activada' : 'Auto-validación desactivada', 'success');
        } catch (err) {
            App.toast(err.message, 'error');
            // Revertir toggle
            const sw = document.getElementById('invoices-auto-switch');
            if (sw) sw.checked = !enabled;
        }
    },


    // ── Cambiar filtro de fecha ──────────────────────────────────────────
    setDateFilter(filter) {
        this._dateFilter = filter;
        document.querySelectorAll('.date-pill').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        this.loadInvoices();
    },

    // ── Refresh manual ───────────────────────────────────────────────────
    refresh() {
        this._caeStatuses = {};   // limpiar caché de CAE
        this.loadInvoices(true);
    },

    // ── Fetch de facturas ────────────────────────────────────────────────
    async loadInvoices(forceRefresh = false) {
        const select = document.getElementById('invoice-pv-select');
        const selectedOpt = select.options[select.selectedIndex];
        if (!selectedOpt) return;

        const serie = selectedOpt.dataset.serie;
        const search = document.getElementById('invoice-search').value.trim();
        const pvs = Auth.getPuntosVenta();
        this.currentPv = pvs.find(pv => pv.id == select.value);

        // Mostrar spinner en botón refresh
        const btnRefresh = document.getElementById('btn-refresh-invoices');
        if (btnRefresh) {
            btnRefresh.classList.add('spinning');
            btnRefresh.disabled = true;
        }

        document.getElementById('invoices-tbody').innerHTML = '';
        document.getElementById('invoices-empty').classList.add('hidden');
        document.getElementById('invoices-loading').classList.remove('hidden');

        try {
            const url = `/api/factusol/invoices?serie=${serie}`
                + `&search=${encodeURIComponent(search)}`
                + `&date_filter=${this._dateFilter}`;

            const data = await API.get(url);
            this._allInvoices = data.invoices || [];

            document.getElementById('invoices-loading').classList.add('hidden');
            this._updateCounter(this._allInvoices.length);

            if (this._allInvoices.length === 0) {
                document.getElementById('invoices-empty').classList.remove('hidden');
                return;
            }

            // Verificar estado CAE (sólo los que no tienen cached)
            for (const inv of this._allInvoices.slice(0, 50)) {
                const key = `${inv.TIPFAC}-${inv.CODFAC}`;
                if (forceRefresh || !this._caeStatuses[key]) {
                    try {
                        const st = await API.get(`/api/arca/status/${inv.TIPFAC}/${inv.CODFAC}`);
                        this._caeStatuses[key] = st;
                    } catch { this._caeStatuses[key] = { validated: false }; }
                }
            }

            this._renderTable();
        } catch (err) {
            document.getElementById('invoices-loading').classList.add('hidden');
            App.toast(err.message, 'error');
        } finally {
            if (btnRefresh) {
                btnRefresh.classList.remove('spinning');
                btnRefresh.disabled = false;
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
        }
    },

    _updateCounter(count) {
        const el = document.getElementById('invoice-count-badge');
        if (el) el.textContent = count;
    },

    // ── Sort ─────────────────────────────────────────────────────────────
    sortBy(col) {
        if (this._sortCol === col) {
            this._sortAsc = !this._sortAsc;
        } else {
            this._sortCol = col;
            this._sortAsc = col !== 'CODFAC';  // numérico: desc por defecto
        }
        this._renderTable();
    },

    _sortedInvoices() {
        const col = this._sortCol;
        const asc = this._sortAsc;
        return [...this._allInvoices].sort((a, b) => {
            let va = a[col] ?? '';
            let vb = b[col] ?? '';
            // Fechas
            if (col === 'FECFAC') {
                va = va ? new Date(va).getTime() : 0;
                vb = vb ? new Date(vb).getTime() : 0;
            }
            // Numéricos
            if (col === 'CODFAC' || col === 'TOTFAC' || col === 'ESTFAC') {
                va = Number(va) || 0;
                vb = Number(vb) || 0;
            }
            if (va < vb) return asc ? -1 : 1;
            if (va > vb) return asc ? 1 : -1;
            return 0;
        });
    },

    // ── Render tabla ─────────────────────────────────────────────────────
    _renderTable() {
        // Actualizar indicadores en headers
        this.COLS.forEach(c => {
            const th = document.getElementById(`th-${c.key}`);
            if (!th || !c.sortable) return;
            th.classList.toggle('sort-active', this._sortCol === c.key);
            const arrow = th.querySelector('.sort-arrow');
            if (arrow) {
                arrow.textContent = this._sortCol === c.key
                    ? (this._sortAsc ? ' ↑' : ' ↓')
                    : ' ⇅';
            }
        });

        const sorted = this._sortedInvoices();
        const tbody = document.getElementById('invoices-tbody');
        tbody.innerHTML = sorted.map(inv => {
            const key = `${inv.TIPFAC}-${inv.CODFAC}`;
            const cae = this._caeStatuses[key];
            const validated = cae?.validated;

            const estadoMap = { 0: ['Pendiente', 'warning'], 2: ['Cobrada', 'success'], 4: ['Anulada', 'danger'] };
            const [estadoLabel, estadoClass] = estadoMap[inv.ESTFAC] ?? ['Pendiente', 'info'];
            const fecha = this.formatDate(inv.FECFAC);
            const hasCaeLocal = inv.BNOFAC && String(inv.BNOFAC).length > 3;

            return `<tr class="${validated || hasCaeLocal ? 'row-validated' : ''}">
                <td><strong>${inv.TIPFAC}-${inv.CODFAC}</strong></td>
                <td>${fecha}</td>
                <td class="td-cliente">${inv.CNOFAC || '-'}</td>
                <td class="td-num">$ ${(inv.TOTFAC || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
                <td><span class="badge badge-${estadoClass}">${estadoLabel}</span></td>
                <td>
                    ${validated
                        ? `<span class="badge badge-success cae-mini" title="CAE: ${cae.cae}">CAE</span>`
                        : hasCaeLocal
                            ? `<span class="badge badge-success cae-mini" title="CAE: ${inv.BNOFAC}">CAE</span>`
                            : `<span class="badge badge-light">Pendiente</span>`}
                </td>
                <td class="td-actions">
                    <button class="btn btn-sm btn-secondary" title="Ver detalle"
                        onclick="InvoicesComponent.viewDetail(${inv.TIPFAC}, ${inv.CODFAC})">
                        <i data-lucide="eye"></i>
                    </button>
                    ${!validated && !hasCaeLocal
                        ? `<button class="btn btn-sm btn-success" title="Validar en ARCA"
                               onclick="InvoicesComponent.validateInvoice(${inv.TIPFAC}, ${inv.CODFAC})">
                               <i data-lucide="check-check"></i> CAE
                           </button>`
                        : ''}
                </td>
            </tr>`;
        }).join('');

        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    // ── Modal detalle ─────────────────────────────────────────────────────
    async viewDetail(tipfac, codfac) {
        try {
            const data = await API.get(`/api/factusol/invoices/${tipfac}/${codfac}`);
            const h = data.header;
            const fecha = this.formatDate(h.FECFAC);
            const cuit = data.cliente?.NIFCLI || '';

            document.getElementById('modal-invoice-title').textContent = `Factura ${h.TIPFAC}-${h.CODFAC}`;

            // Condicion IVA del cliente
            const ivaMap = { 0: 'Resp. Inscripto', 1: 'Monotributista', 3: 'Exento', 4: 'Consumidor Final' };
            const condIva = data.cliente ? (ivaMap[data.cliente.IVACLI] || `Tipo ${data.cliente.IVACLI}`) : '-';

            let html = `<div class="invoice-header-grid">
                <div class="invoice-field"><label>Nro</label>${h.TIPFAC}-${h.CODFAC}</div>
                <div class="invoice-field"><label>Fecha</label>${fecha}</div>
                <div class="invoice-field"><label>Cliente</label>${h.CNOFAC || '-'}</div>
                <div class="invoice-field"><label>Cod. Cliente</label>${h.CLIFAC || '-'}</div>
                <div class="invoice-field"><label>Cond. IVA</label>${condIva}</div>
                <div class="invoice-field"><label>Estado</label>${h.ESTFAC == 1 ? 'Cobrada' : 'Pendiente'}</div>
            </div>`;

            // ── CAE ya grabado en Factusol ──
            const hasCaeFactusol = h.BNOFAC && String(h.BNOFAC).trim().length > 3;
            if (hasCaeFactusol) {
                html += `<div class="cae-factusol-block">
                    <div class="cae-factusol-header">
                        <i data-lucide="shield-check"></i> <strong>Comprobante Validado en ARCA</strong>
                    </div>
                    <div class="invoice-header-grid">
                        <div class="invoice-field"><label>CAE</label><strong>${h.BNOFAC}</strong></div>
                        <div class="invoice-field"><label>Vto CAE</label>${h.BNUFAC || '-'}</div>
                        <div class="invoice-field"><label>Nro Cbte ARCA</label>${h.PEDFAC || '-'}</div>
                    </div>
                </div>`;
            }

            if (data.cliente) {
                html += `<div class="invoice-cliente-block">
                    <div class="invoice-cliente-header">
                        <span class="invoice-cliente-title"><i data-lucide="user"></i> Datos del Cliente en Factusol</span>
                        ${cuit
                            ? `<button class="btn btn-sm btn-padron" id="btn-consultar-padron"
                                onclick="InvoicesComponent.consultarPadron('${cuit}', '${(h.CNOFAC||'').replace(/'/g,"\\'")}')">`
                                + `<i data-lucide="search"></i> Consultar ARCA</button>`
                            : `<span class="padron-no-cuit"><i data-lucide="alert-circle"></i> Sin CUIT</span>`}
                    </div>
                    <div class="invoice-header-grid">
                        <div class="invoice-field"><label>CUIT/DNI</label>${cuit || '-'}</div>
                        <div class="invoice-field"><label>Domicilio</label>${data.cliente.DOMCLI || '-'}</div>
                        <div class="invoice-field"><label>Localidad</label>${data.cliente.POBCLI || '-'}</div>
                        <div class="invoice-field"><label>Teléfono</label>${data.cliente.TELCLI || '-'}</div>
                    </div>
                </div>`;
            }

            html += `<div id="padron-panel" class="padron-panel hidden"></div>`;

            // Líneas
            html += `<div class="invoice-lines-table"><table><thead><tr>
                <th>Pos</th><th>Articulo</th><th>Descripcion</th><th>Cant</th><th>Precio</th><th>IVA%</th><th>Total</th>
            </tr></thead><tbody>`;
            for (const l of data.lines) {
                html += `<tr>
                    <td>${l.POSLFA}</td><td>${l.ARTLFA || ''}</td><td>${l.DESLFA || ''}</td>
                    <td>${l.CANLFA || 0}</td>
                    <td>$ ${(l.PRELFA || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
                    <td>${l.PIVLFA || 0}%</td>
                    <td>$ ${(l.TOTLFA || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
                </tr>`;
            }
            html += `</tbody></table></div>`;

            // ── Subtotales fiscales ──
            html += `<div class="invoice-totals-grid">`;
            for (let i = 1; i <= 3; i++) {
                const base = parseFloat(h[`BAS${i}FAC`] || 0);
                const iiva = parseFloat(h[`IIVA${i}FAC`] || 0);
                const piva = parseFloat(h[`PIVA${i}FAC`] || 0);
                if (base > 0) {
                    html += `<div class="invoice-total-row">
                        <span>Base IVA ${piva}%</span>
                        <span>$ ${base.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                    </div>
                    <div class="invoice-total-row">
                        <span>IVA ${piva}%</span>
                        <span>$ ${iiva.toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
                    </div>`;
                }
            }
            html += `<div class="invoice-total-row invoice-total-final">
                <span>Total</span>
                <span>$ ${parseFloat(h.TOTFAC || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</span>
            </div>`;
            html += `</div>`;

            // CAE en log local (si no hay en Factusol)
            const caeStatus = await API.get(`/api/arca/status/${tipfac}/${codfac}`).catch(() => ({ validated: false }));
            if (caeStatus.validated && !hasCaeFactusol) {
                html += `<div class="cae-factusol-block">
                    <div class="cae-factusol-header">
                        <i data-lucide="shield-check"></i> <strong>Comprobante Validado en ARCA</strong>
                    </div>
                    <div class="invoice-header-grid">
                        <div class="invoice-field"><label>CAE</label><strong>${caeStatus.cae}</strong></div>
                        <div class="invoice-field"><label>Vto CAE</label>${caeStatus.cae_vto}</div>
                        <div class="invoice-field"><label>Nro Cbte ARCA</label>#${caeStatus.voucher_number} — PV ${caeStatus.punto_venta}</div>
                    </div>
                </div>`;
            }

            document.getElementById('modal-invoice-body').innerHTML = html;

            const footer = document.getElementById('modal-invoice-footer');
            const yaValidada = caeStatus.validated || hasCaeFactusol;

            if (!yaValidada && this.currentPv) {
                footer.innerHTML = `
                    <button class="btn btn-secondary modal-close">Cerrar</button>
                    <button class="btn btn-success" onclick="InvoicesComponent.validateInvoice(${tipfac}, ${codfac})">
                        <i data-lucide="check-check"></i> Validar en ARCA
                    </button>`;
            } else {
                footer.innerHTML = '<button class="btn btn-secondary modal-close">Cerrar</button>';
            }
            footer.querySelectorAll('.modal-close').forEach(el => el.addEventListener('click', () => this.closeModal()));

            document.getElementById('invoice-modal').classList.remove('hidden');
            if (typeof lucide !== 'undefined') lucide.createIcons();

            if (cuit && this._padronCache[cuit]) {
                this._renderPadronPanel(this._padronCache[cuit]);
            }
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    // ── Padrón ARCA ───────────────────────────────────────────────────────
    async consultarPadron(cuit, nombreActual) {
        const btn = document.getElementById('btn-consultar-padron');
        if (btn) { btn.disabled = true; btn.innerHTML = '<i data-lucide="loader-2" class="spin-icon"></i> Consultando...'; if (typeof lucide !== 'undefined') lucide.createIcons(); }
        const panel = document.getElementById('padron-panel');
        if (panel) {
            panel.classList.remove('hidden');
            panel.innerHTML = `<div class="padron-loading"><i data-lucide="loader-2" class="spin-icon"></i><span>Consultando Padron ARCA para CUIT ${cuit}...</span></div>`;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }

        this._logClear();
        this._logLine(`Consultando padron ARCA para CUIT ${cuit}...`, 'info');
        this._logLine(`Autenticando con WSAA (ws_sr_padron_a4)...`, 'info');

        try {
            const data = await API.get(`/api/arca/padron/${cuit}`);
            this._padronCache[cuit] = data;
            this._logLine(`Padron OK: ${data.razon_social || data.apellido || ''} - ${data.estado_cuit || 'N/D'}`, 'ok');
            this._renderPadronPanel(data, nombreActual);
        } catch (err) {
            this._logLine(`ERROR: ${err.message}`, 'error');
            if (panel) { panel.innerHTML = `<div class="padron-error"><i data-lucide="alert-triangle"></i><span>Error: ${err.message}</span></div>`; if (typeof lucide !== 'undefined') lucide.createIcons(); }
            App.toast(`Padron ARCA: ${err.message}`, 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = '<i data-lucide="search"></i> Consultar ARCA'; if (typeof lucide !== 'undefined') lucide.createIcons(); }
        }
    },


    _renderPadronPanel(data, nombreActual) {
        const panel = document.getElementById('padron-panel');
        if (!panel) return;
        panel.classList.remove('hidden');
        const estadoClass = data.estado_cuit === 'ACTIVO' ? 'padron-estado-activo' : data.estado_cuit === 'INACTIVO' ? 'padron-estado-inactivo' : 'padron-estado-nd';
        const nombreCompleto = data.tipo_persona === 'FISICA' ? `${data.apellido || ''} ${data.nombre || ''}`.trim() : data.razon_social || '';
        const dom = data.domicilio_fiscal || {};
        const domStr = [dom.calle, dom.numero, dom.piso, dom.depto].filter(Boolean).join(' ');
        const locStr = [dom.localidad, dom.provincia, dom.cp].filter(Boolean).join(' · ');
        const hasDiff = nombreActual && nombreCompleto && nombreActual.trim().toLowerCase() !== nombreCompleto.toLowerCase();

        panel.innerHTML = `<div class="padron-result">
            <div class="padron-result-header">
                <div class="padron-result-title"><i data-lucide="shield-check"></i><span>Datos en el Padron ARCA</span></div>
                <span class="padron-estado ${estadoClass}">${data.estado_cuit || 'N/D'}</span>
            </div>
            <div class="padron-data-grid">
                <div class="padron-field"><label>CUIT</label><span class="padron-value">${this._formatCuit(data.cuit)}</span></div>
                <div class="padron-field"><label>Tipo Persona</label><span class="padron-value">${data.tipo_persona || '-'}</span></div>
                <div class="padron-field padron-field-wide"><label>Razon Social / Nombre</label>
                    <span class="padron-value padron-nombre ${hasDiff ? 'padron-diff' : ''}">
                        ${nombreCompleto || data.razon_social || '-'}
                        ${hasDiff ? '<span class="padron-diff-badge">Difiere de Factusol</span>' : ''}
                    </span></div>
                <div class="padron-field padron-field-wide"><label>Condicion IVA</label><span class="padron-value">${data.condicion_iva || '-'}</span></div>
                ${domStr ? `<div class="padron-field padron-field-wide"><label>Domicilio Fiscal</label><span class="padron-value">${domStr}</span></div>` : ''}
                ${locStr ? `<div class="padron-field padron-field-wide"><label>Localidad / CP</label><span class="padron-value">${locStr}</span></div>` : ''}
            </div>
            ${hasDiff ? `<div class="padron-diff-alert"><i data-lucide="alert-circle"></i><span>El nombre en Factusol (<strong>${nombreActual}</strong>) difiere del Padron (<strong>${nombreCompleto}</strong>).</span></div>` : ''}
            <div class="padron-footer-note"><i data-lucide="info"></i>Datos en tiempo real del Padron ARCA. Actualizar en Factusol manualmente.</div>
        </div>`;
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    _formatCuit(cuit) {
        if (!cuit || cuit.length !== 11) return cuit || '-';
        return `${cuit.slice(0,2)}-${cuit.slice(2,10)}-${cuit.slice(10)}`;
    },

    // ── Mini-terminal helpers ─────────────────────────────────────────────
    _logClear() {
        const log = document.getElementById('arca-log');
        const lines = document.getElementById('arca-log-lines');
        if (log) { log.classList.remove('hidden'); }
        if (lines) { lines.innerHTML = ''; }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    _logLine(text, type = 'info') {
        const lines = document.getElementById('arca-log-lines');
        if (!lines) return;
        const now = new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const line = document.createElement('div');
        line.className = `arca-log-line log-${type}`;
        line.innerHTML = `<span class="log-time">${now}</span><span>${text}</span>`;
        lines.appendChild(line);
        lines.scrollTop = lines.scrollHeight;
    },

    _logHide() {
        const log = document.getElementById('arca-log');
        if (log) log.classList.add('hidden');
    },

    // ── Validar en ARCA ───────────────────────────────────────────────────
    async validateInvoice(tipfac, codfac) {
        if (!this.currentPv) {
            App.toast('No tiene un punto de venta seleccionado', 'error');
            return;
        }
        if (!confirm(
            `Validar factura ${tipfac}-${codfac} en ARCA?\n` +
            `Punto de Venta: ${this.currentPv.punto_venta}\n` +
            `Esta accion solicitara un CAE a AFIP.`
        )) return;

        this._logClear();
        this._logLine(`Iniciando validacion factura ${tipfac}-${codfac}...`, 'info');
        this._logLine(`PV: ${this.currentPv.punto_venta} | Autenticando con WSAA...`, 'info');

        try {
            const result = await API.post(`/api/arca/validate/${tipfac}/${codfac}?pv_id=${this.currentPv.id}`);

            if (result.status === 'ok') {
                this._logLine(`CAE obtenido: ${result.cae}`, 'ok');
                App.toast(`CAE obtenido: ${result.cae}`, 'success');
            } else if (result.status === 'already_validated') {
                this._logLine(`Factura ya validada. CAE: ${result.cae}`, 'warn');
                App.toast(`Factura ya validada. CAE: ${result.cae}`, 'info');
            } else {
                this._logLine(result.message || 'Respuesta inesperada', 'warn');
                App.toast(result.message || 'Respuesta inesperada de ARCA', 'warning');
            }

            setTimeout(() => {
                this.closeModal();
                this.refresh();
            }, 2000);
        } catch (err) {
            const msg = err.message || 'Error desconocido';
            this._logLine(`ERROR: ${msg}`, 'error');
            App.toast(`Error ARCA: ${msg}`, 'error');
            console.error('[ARCA] Error en validateInvoice:', msg);
        }
    },


    closeModal() {
        this._logHide();
        document.getElementById('invoice-modal').classList.add('hidden');
    },


    formatDate(d) {
        if (!d) return '-';
        if (typeof d === 'string') {
            if (d.includes('1900')) return '-';
            const m = d.match(/(\d{4})-(\d{2})-(\d{2})/);
            if (m) return `${m[3]}/${m[2]}/${m[1]}`;
            return d;
        }
        try {
            const dt = new Date(d);
            if (dt.getFullYear() <= 1900) return '-';
            return dt.toLocaleDateString('es-AR');
        } catch { return '-'; }
    },
};
