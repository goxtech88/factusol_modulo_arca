/**
 * Invoices Component
 * - Filtros de fecha: Todos / Hoy / Ayer / Últimos 7 días
 * - Botón Actualizar (refresh desde Factusol)
 * - Ordenamiento por columna (click en header)
 * - Modal de detalle + Consulta Padrón ARCA
 */
const InvoicesComponent = {
    currentPv: null,
    _allInvoices: [],       // datos cacheados del último fetch
    _caeStatuses: {},       // caché de status CAE por "TIPFAC-CODFAC"
    _sortCol: 'CODFAC',
    _sortAsc: false,
    _dateFilter: 'today',   // all | today | yesterday | last7 | this_week | this_month | last_month | this_year
    _fopfacFilters: new Set(),  // códigos de formas de pago seleccionadas (vacío = todas)
    _paymentMethods: [],        // cache de formas de pago
    _fopfacAllSelected: true,   // si todas están tildadas

    // ── Columnas ordenables ──────────────────────────────────────────────
    COLS: [
        { key: 'CODFAC',   label: 'Nro',     sortable: true  },
        { key: 'FECFAC',   label: 'Fecha',   sortable: true  },
        { key: 'CNOFAC',   label: 'Cliente', sortable: true  },
        { key: 'TOTFAC',   label: 'Total',   sortable: true  },
        { key: 'ESTFAC',   label: 'Estado',  sortable: true  },
        { key: 'DESFPA',   label: 'F. Pago', sortable: true  },
        { key: '_cae',     label: 'CAE',     sortable: false },
        { key: '_actions', label: '',        sortable: false },
    ],

    init() {
        document.getElementById('invoice-pv-select')
            .addEventListener('change', () => this.loadInvoices());

        document.getElementById('invoice-search')
            .addEventListener('input', App.debounce(() => this.loadInvoices(), 400));

        // Restaurar filtro de formas de pago guardado
        try {
            const saved = JSON.parse(localStorage.getItem('invoice_fopfac_filters') || 'null');
            if (Array.isArray(saved)) {
                this._fopfacFilters = new Set(saved);
                this._fopfacAllSelected = false;
            }
        } catch { /* use defaults */ }

        // Dropdown toggle
        const dropBtn = document.getElementById('fopfac-dropdown-btn');
        if (dropBtn) {
            dropBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this._toggleFopfacDropdown();
            });
        }
        // Close dropdown on outside click
        document.addEventListener('click', (e) => {
            const dd = document.getElementById('fopfac-dropdown');
            if (dd && !dd.contains(e.target)) {
                dd.classList.remove('open');
                document.getElementById('fopfac-dropdown-menu')?.classList.add('hidden');
            }
        });

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
            // Cargar formas de pago y luego facturas
            this.loadPaymentMethods().then(() => this.loadInvoices());
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

    // ── Cargar formas de pago (multi-select checkboxes) ────────────────────
    async loadPaymentMethods() {
        try {
            const data = await API.get('/api/factusol/payment-methods');
            this._paymentMethods = data || [];

            // Si no hay filtro guardado, seleccionar todas por defecto
            if (this._fopfacFilters.size === 0 && this._fopfacAllSelected) {
                this._fopfacFilters = new Set(this._paymentMethods.map(fp => String(fp.CODFPA)));
                this._fopfacAllSelected = true;
            }

            this._renderFopfacCheckboxes();
        } catch (err) {
            console.warn('No se pudieron cargar formas de pago:', err.message);
        }
    },

    _toggleFopfacDropdown() {
        const dd = document.getElementById('fopfac-dropdown');
        const menu = document.getElementById('fopfac-dropdown-menu');
        if (!dd || !menu) return;
        const isOpen = !menu.classList.contains('hidden');
        if (isOpen) {
            dd.classList.remove('open');
            menu.classList.add('hidden');
        } else {
            dd.classList.add('open');
            menu.classList.remove('hidden');
        }
    },

    _renderFopfacCheckboxes() {
        const list = document.getElementById('fopfac-checkbox-list');
        if (!list) return;
        list.innerHTML = this._paymentMethods.map(fp => {
            const code = String(fp.CODFPA);
            const checked = this._fopfacFilters.has(code) ? 'checked' : '';
            return `<div class="multiselect-item">
                <input type="checkbox" id="fopfac-cb-${code}" value="${code}" ${checked}
                    onchange="InvoicesComponent.toggleFopfac('${code}', this.checked)">
                <label for="fopfac-cb-${code}">${fp.DESFPA || code}</label>
            </div>`;
        }).join('');
        this._updateFopfacLabel();
    },

    toggleFopfac(code, checked) {
        if (checked) {
            this._fopfacFilters.add(code);
        } else {
            this._fopfacFilters.delete(code);
        }
        this._fopfacAllSelected = this._fopfacFilters.size === this._paymentMethods.length;
        this._saveFopfacFilters();
        this._updateFopfacLabel();
        this._applyClientFilter();
    },

    fopfacSelectAll() {
        this._fopfacFilters = new Set(this._paymentMethods.map(fp => String(fp.CODFPA)));
        this._fopfacAllSelected = true;
        this._renderFopfacCheckboxes();
        this._saveFopfacFilters();
        this._applyClientFilter();
    },

    fopfacSelectNone() {
        this._fopfacFilters.clear();
        this._fopfacAllSelected = false;
        this._renderFopfacCheckboxes();
        this._saveFopfacFilters();
        this._applyClientFilter();
    },

    _saveFopfacFilters() {
        if (this._fopfacAllSelected) {
            localStorage.removeItem('invoice_fopfac_filters');
        } else {
            localStorage.setItem('invoice_fopfac_filters', JSON.stringify([...this._fopfacFilters]));
        }
        // Guardar también en config del backend para auto-validación
        this._saveAutoValidateFopfac();
    },

    async _saveAutoValidateFopfac() {
        try {
            const codes = this._fopfacAllSelected ? [] : [...this._fopfacFilters];
            await API.post('/api/arca/auto-validate/payment-filters', { fopfac_codes: codes });
        } catch { /* silent */ }
    },

    _updateFopfacLabel() {
        const label = document.getElementById('fopfac-dropdown-label');
        if (!label) return;
        const total = this._paymentMethods.length;
        const selected = this._fopfacFilters.size;
        if (selected === 0) {
            label.innerHTML = 'Ninguna';
        } else if (selected === total) {
            label.innerHTML = 'Todas';
        } else {
            label.innerHTML = `F. Pago <span class="multiselect-badge">${selected}</span>`;
        }
    },

    /** Filtra _allInvoices en memoria y re-renderiza */
    _applyClientFilter() {
        this._renderTable();
        this._updateCounter(this._getFilteredInvoices().length);
    },

    /** Devuelve facturas filtradas por formas de pago seleccionadas */
    _getFilteredInvoices() {
        if (this._fopfacAllSelected || this._fopfacFilters.size === this._paymentMethods.length) {
            return this._allInvoices;
        }
        if (this._fopfacFilters.size === 0) return [];
        return this._allInvoices.filter(inv => this._fopfacFilters.has(String(inv.FOPFAC)));
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
            const filtered = this._getFilteredInvoices();
            this._updateCounter(filtered.length);

            if (filtered.length === 0) {
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
        return [...this._getFilteredInvoices()].sort((a, b) => {
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
                <td class="td-fpago">${inv.DESFPA || inv.FOPFAC || '-'}</td>
                <td>
                    ${validated
                        ? `<span class="badge badge-success cae-mini" title="CAE: ${cae.cae}">CAE</span>`
                        : hasCaeLocal
                            ? `<span class="badge badge-success cae-mini" title="CAE: ${inv.BNOFAC}">CAE</span>`
                            : `<span class="badge badge-light">Pendiente</span>`}
                </td>
                <td class="td-actions">
                    <button class="btn btn-sm btn-secondary" title="Ver detalle / Ver CAE"
                        onclick="InvoicesComponent.viewDetail(${inv.TIPFAC}, ${inv.CODFAC})">
                        <i data-lucide="eye"></i>
                    </button>
                    ${!validated && !hasCaeLocal
                        ? `<button class="btn btn-sm btn-success" title="Obtener CAE en ARCA"
                               onclick="InvoicesComponent.validateInvoice(${inv.TIPFAC}, ${inv.CODFAC})">
                               <i data-lucide="check-check"></i> CAE
                           </button>`
                        : ''}
                    ${validated && !hasCaeLocal
                        ? `<button class="btn btn-sm btn-warning" title="El CAE se obtuvo en ARCA pero no se grabo en Factusol. Grabar ahora."
                               onclick="InvoicesComponent.grabarFactusol(${inv.TIPFAC}, ${inv.CODFAC})">
                               <i data-lucide="save"></i> Grabar
                           </button>`
                        : ''}
                    ${(validated || hasCaeLocal)
                        ? (cae?.has_nc
                            ? `<span class="badge badge-warning" title="NC emitida: ${cae.nc_cae || ''}">NC</span>`
                            : `<button class="btn btn-sm btn-danger" title="Nota de Credito"
                                   onclick="InvoicesComponent.createCreditNote(${inv.TIPFAC}, ${inv.CODFAC})">
                                   <i data-lucide="file-minus"></i> NC
                               </button>`)
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

            // Condicion fiscal del cliente — usar CFECLI (no IVACLI).
            // IVACLI es un codigo interno de calculos de Factusol que por default
            // queda en 0 y se mapeaba mal a "Resp. Inscripto" para todos los clientes.
            // CFECLI refleja la condicion fiscal real del cliente:
            //   0=No configurado, 1=CF, 2=RI, 3=Mono, 4=Exento, 5=No Responsable
            const cfecliMapHeader = {
                0: 'Sin configurar',
                1: 'Consumidor Final',
                2: 'Resp. Inscripto',
                3: 'Monotributista',
                4: 'Exento',
                5: 'No Responsable',
            };
            const condIva = data.cliente
                ? (cfecliMapHeader[data.cliente.CFECLI] ?? `Tipo ${data.cliente.CFECLI}`)
                : '-';

            let html = `<div class="invoice-header-grid">
                <div class="invoice-field"><label>Nro</label>${h.TIPFAC}-${h.CODFAC}</div>
                <div class="invoice-field"><label>Fecha</label>${fecha}</div>
                <div class="invoice-field"><label>Cliente</label>${h.CNOFAC || '-'}</div>
                <div class="invoice-field"><label>Cod. Cliente</label>${h.CLIFAC || '-'}</div>
                <div class="invoice-field"><label>Cond. IVA</label>${condIva}</div>
                <div class="invoice-field"><label>Estado</label>${h.ESTFAC == 1 ? 'Cobrada' : 'Pendiente'}</div>
                <div class="invoice-field"><label>Forma de Pago</label>${h.DESFPA || h.FOPFAC || '-'}</div>
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
                const codcli = data.cliente.CODCLI || '';
                const cfecliMap = { 0: 'Sin configurar', 1: 'Consumidor Final', 2: 'Resp. Inscripto', 3: 'Monotributista', 4: 'Exento' };
                const cfecliLabel = cfecliMap[data.cliente.CFECLI] || `Tipo ${data.cliente.CFECLI}`;
                html += `<div class="invoice-cliente-block">
                    <div class="invoice-cliente-header">
                        <span class="invoice-cliente-title"><i data-lucide="user"></i> Datos del Cliente en Factusol</span>
                        ${cuit
                            ? `<button class="btn btn-sm btn-padron" id="btn-actualizar-cuit"
                                onclick="InvoicesComponent.actualizarDatosCuit(${codcli}, '${cuit}', '${tipfac}', '${codfac}')">`
                                + `<i data-lucide="refresh-cw"></i> Actualizar datos desde CUIT</button>`
                            : `<span class="padron-no-cuit"><i data-lucide="alert-circle"></i> Sin CUIT</span>`}
                    </div>
                    <div class="invoice-header-grid">
                        <div class="invoice-field"><label>Código</label>${codcli}</div>
                        <div class="invoice-field"><label>CUIT/DNI</label>${cuit || '-'}</div>
                        <div class="invoice-field"><label>Domicilio</label>${data.cliente.DOMCLI || '-'}</div>
                        <div class="invoice-field"><label>Localidad</label>${data.cliente.POBCLI || '-'}</div>
                        <div class="invoice-field"><label>Cond. Fiscal</label>${cfecliLabel}</div>
                        <div class="invoice-field"><label>Teléfono</label>${data.cliente.TELCLI || '-'}</div>
                    </div>
                </div>`;
            }


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
                    <div class="cae-warning-note">
                        <i data-lucide="alert-triangle"></i>
                        El CAE se obtuvo en ARCA pero <strong>aun no se grabo en Factusol</strong>.
                        Use el boton <strong>"Grabar datos en Factusol"</strong> para sincronizarlo.
                    </div>
                </div>`;
            }

            document.getElementById('modal-invoice-body').innerHTML = html;

            const footer = document.getElementById('modal-invoice-footer');
            const yaValidada = caeStatus.validated || hasCaeFactusol;
            // Discrepancia: el CAE existe en el log de ARCA pero NO esta grabado en Factusol.
            const discrepancia = caeStatus.validated && !hasCaeFactusol;

            if (!yaValidada && this.currentPv) {
                footer.innerHTML = `
                    <button class="btn btn-secondary modal-close">Cerrar</button>
                    <button class="btn btn-success" onclick="InvoicesComponent.validateInvoice(${tipfac}, ${codfac})">
                        <i data-lucide="check-check"></i> Obtener CAE
                    </button>`;
            } else if (yaValidada && this.currentPv) {
                // Solo se puede re-grabar si el CAE figura en el log de ARCA.
                const grabarBtn = caeStatus.validated
                    ? `<button class="btn ${discrepancia ? 'btn-warning' : 'btn-secondary'}"
                            title="Re-graba en Factusol el Nro de comprobante, vencimiento, QR y codigo de barras del CAE"
                            onclick="InvoicesComponent.grabarFactusol(${tipfac}, ${codfac})">
                            <i data-lucide="save"></i> Grabar datos en Factusol
                        </button>`
                    : '';
                footer.innerHTML = `
                    <button class="btn btn-secondary modal-close">Cerrar</button>
                    ${grabarBtn}
                    <button class="btn btn-danger" onclick="InvoicesComponent.createCreditNote(${tipfac}, ${codfac})">
                        <i data-lucide="file-minus"></i> Emitir Nota de Credito
                    </button>`;
            } else {
                footer.innerHTML = '<button class="btn btn-secondary modal-close">Cerrar</button>';
            }
            footer.querySelectorAll('.modal-close').forEach(el => el.addEventListener('click', () => this.closeModal()));

            document.getElementById('invoice-modal').classList.remove('hidden');
            if (typeof lucide !== 'undefined') lucide.createIcons();


        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    // ── Actualizar datos del cliente desde CUIT ────────────────────────────
    async actualizarDatosCuit(codcli, cuit, tipfac, codfac) {
        const btn = document.getElementById('btn-actualizar-cuit');
        if (btn) { btn.disabled = true; btn.innerHTML = '<i data-lucide="loader-2" class="spin-icon"></i> Actualizando...'; if (typeof lucide !== 'undefined') lucide.createIcons(); }

        try {
            const result = await API.post(`/api/arca/enrich-customer/${codcli}/${cuit}`);
            const fields = result.updated_fields || [];
            App.toast(`Cliente actualizado: ${result.razon_social || ''} — ${result.condicion_iva || 'N/D'} (${fields.length} campos)`, 'success');
            // Refrescar el modal con los datos actualizados
            this.viewDetail(tipfac, codfac);
        } catch (err) {
            App.toast(`Error al actualizar: ${err.message}`, 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = '<i data-lucide="refresh-cw"></i> Actualizar datos desde CUIT'; if (typeof lucide !== 'undefined') lucide.createIcons(); }
        }
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
                if (result.factusol_grabado === false) {
                    this._logLine('El CAE se obtuvo pero NO se grabo en Factusol. Use "Grabar datos en Factusol".', 'warn');
                    App.toast(`CAE obtenido (${result.cae}) pero NO se grabo en Factusol. Use el boton "Grabar datos en Factusol".`, 'warning');
                } else {
                    App.toast(`CAE obtenido: ${result.cae}`, 'success');
                }
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


    // ── Grabar datos del CAE en Factusol ─────────────────────────────────
    async grabarFactusol(tipfac, codfac) {
        if (!confirm(
            `Grabar los datos del CAE de la factura ${tipfac}-${codfac} en Factusol?\n\n` +
            `Se escribiran en F_FAC: Nro de comprobante, vencimiento del CAE, QR y codigo de barras AFIP.`
        )) return;

        this._logClear();
        this._logLine(`Grabando datos del CAE en Factusol para ${tipfac}-${codfac}...`, 'info');

        try {
            const result = await API.post(`/api/arca/write-factusol/${tipfac}/${codfac}`);

            if (result.status === 'ok') {
                this._logLine(`Grabado en Factusol: ${result.comprobante_nro} (CAE ${result.cae})`, 'ok');
                App.toast(result.message || 'Datos grabados en Factusol', 'success');
            } else {
                this._logLine(result.message || 'Respuesta inesperada', 'warn');
                App.toast(result.message || 'Respuesta inesperada', 'warning');
            }

            setTimeout(() => {
                this.closeModal();
                this.refresh();
            }, 2000);
        } catch (err) {
            const msg = err.message || 'Error desconocido';
            this._logLine(`ERROR: ${msg}`, 'error');
            App.toast(`Error al grabar en Factusol: ${msg}`, 'error');
        }
    },


    // ── Nota de Credito ─────────────────────────────────────────────────
    async createCreditNote(tipfac, codfac) {
        if (!this.currentPv) {
            App.toast('No tiene un punto de venta seleccionado', 'error');
            return;
        }
        // Verificar que tenga CAE y no tenga NC ya emitida
        const key = `${tipfac}-${codfac}`;
        const st = this._caeStatuses[key];
        if (!st?.validated) {
            App.toast('La factura no tiene CAE. Solo se pueden emitir NC de facturas validadas en ARCA.', 'error');
            return;
        }
        if (st?.has_nc) {
            App.toast('Ya existe una Nota de Credito para esta factura', 'warning');
            return;
        }
        if (!confirm(
            `ATENCION: Emitir NOTA DE CREDITO para anular factura ${tipfac}-${codfac}?\n\n` +
            `Punto de Venta: ${this.currentPv.punto_venta}\n` +
            `Esto generara una NC en AFIP con los mismos importes de la factura original.\n\n` +
            `Esta accion NO se puede deshacer.`
        )) return;

        this._logClear();
        this._logLine(`Emitiendo Nota de Credito para ${tipfac}-${codfac}...`, 'info');
        this._logLine(`PV: ${this.currentPv.punto_venta} | Conectando con ARCA...`, 'info');

        try {
            const result = await API.post(`/api/arca/credit-note/${tipfac}/${codfac}?pv_id=${this.currentPv.id}`);

            if (result.status === 'ok') {
                this._logLine(`${result.tipo_nombre} emitida: ${result.comprobante_nro}`, 'ok');
                this._logLine(`CAE: ${result.cae}`, 'ok');
                App.toast(`${result.message}`, 'success');
            } else if (result.status === 'already_exists') {
                this._logLine(`Ya existe NC para esta factura. CAE: ${result.cae}`, 'warn');
                App.toast(`Ya existe NC para esta factura`, 'info');
            } else {
                this._logLine(result.message || 'Respuesta inesperada', 'warn');
                App.toast(result.message || 'Respuesta inesperada', 'warning');
            }

            setTimeout(() => {
                this.closeModal();
                this.refresh();
            }, 2000);
        } catch (err) {
            const msg = err.message || 'Error desconocido';
            this._logLine(`ERROR: ${msg}`, 'error');
            App.toast(`Error al emitir NC: ${msg}`, 'error');
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
