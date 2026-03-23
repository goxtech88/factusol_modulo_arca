/**
 * Invoices Component - View, validate and consult padron for Factusol invoices.
 */
const InvoicesComponent = {
    currentPv: null,
    _padronCache: {},    // cuit → data del padrón

    init() {
        const select = document.getElementById('invoice-pv-select');
        select.addEventListener('change', () => this.loadInvoices());

        document.getElementById('invoice-search').addEventListener('input',
            App.debounce(() => this.loadInvoices(), 400)
        );

        // Modal close
        document.querySelectorAll('#invoice-modal .modal-close, #invoice-modal .modal-overlay').forEach(el => {
            el.addEventListener('click', () => this.closeModal());
        });
    },

    loadPuntosVenta() {
        const select = document.getElementById('invoice-pv-select');
        const pvs = Auth.getPuntosVenta();
        select.innerHTML = pvs.length === 0
            ? '<option value="">Sin puntos de venta</option>'
            : pvs.map(pv => `<option value="${pv.id}" data-serie="${pv.serie_factusol}">${pv.nombre} (Serie ${pv.serie_factusol} → PV ${pv.punto_venta})</option>`).join('');

        if (pvs.length > 0) {
            this.currentPv = pvs[0];
            this.loadInvoices();
        }
    },

    async loadInvoices() {
        const select = document.getElementById('invoice-pv-select');
        const selectedOpt = select.options[select.selectedIndex];
        if (!selectedOpt) return;

        const serie = selectedOpt.dataset.serie;
        const search = document.getElementById('invoice-search').value.trim();

        const pvs = Auth.getPuntosVenta();
        this.currentPv = pvs.find(pv => pv.id == select.value);

        document.getElementById('invoices-tbody').innerHTML = '';
        document.getElementById('invoices-empty').classList.add('hidden');
        document.getElementById('invoices-loading').classList.remove('hidden');

        try {
            const data = await API.get(`/api/factusol/invoices?serie=${serie}&search=${encodeURIComponent(search)}`);
            document.getElementById('invoices-loading').classList.add('hidden');

            if (data.invoices.length === 0) {
                document.getElementById('invoices-empty').classList.remove('hidden');
                return;
            }

            // Check CAE status (solo primeras 50 para no saturar)
            const caeStatuses = {};
            for (const inv of data.invoices.slice(0, 50)) {
                try {
                    const st = await API.get(`/api/arca/status/${inv.TIPFAC}/${inv.CODFAC}`);
                    if (st.validated) caeStatuses[`${inv.TIPFAC}-${inv.CODFAC}`] = st;
                } catch {}
            }

            const tbody = document.getElementById('invoices-tbody');
            tbody.innerHTML = data.invoices.map(inv => {
                const key = `${inv.TIPFAC}-${inv.CODFAC}`;
                const cae = caeStatuses[key];
                const estado = inv.ESTFAC === 0 ? 'Pendiente' : inv.ESTFAC === 1 ? 'Cobrada' : 'Anulada';
                const estadoClass = inv.ESTFAC === 0 ? 'warning' : inv.ESTFAC === 1 ? 'success' : 'danger';
                const fecha = InvoicesComponent.formatDate(inv.FECFAC);

                return `<tr>
                    <td><strong>${inv.TIPFAC}-${inv.CODFAC}</strong></td>
                    <td>${fecha}</td>
                    <td>${inv.CNOFAC || '-'}</td>
                    <td>$ ${(inv.TOTFAC || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
                    <td><span class="badge badge-${estadoClass}">${estado}</span></td>
                    <td>${cae ? `<span class="badge badge-success">${cae.cae}</span>` : '<span class="badge badge-info">Pendiente</span>'}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="InvoicesComponent.viewDetail(${inv.TIPFAC}, ${inv.CODFAC})">
                            <i data-lucide="eye"></i>
                        </button>
                        ${!cae ? `<button class="btn btn-sm btn-success" onclick="InvoicesComponent.validateInvoice(${inv.TIPFAC}, ${inv.CODFAC})">
                            <i data-lucide="check-check"></i> CAE
                        </button>` : ''}
                    </td>
                </tr>`;
            }).join('');
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } catch (err) {
            document.getElementById('invoices-loading').classList.add('hidden');
            App.toast(err.message, 'error');
        }
    },

    async viewDetail(tipfac, codfac) {
        try {
            const data = await API.get(`/api/factusol/invoices/${tipfac}/${codfac}`);
            const h = data.header;
            const fecha = this.formatDate(h.FECFAC);
            const cuit = data.cliente?.NIFCLI || '';

            document.getElementById('modal-invoice-title').textContent = `Factura ${h.TIPFAC}-${h.CODFAC}`;

            // ── Header info ──
            let html = `<div class="invoice-header-grid">
                <div class="invoice-field"><label>Nro</label>${h.TIPFAC}-${h.CODFAC}</div>
                <div class="invoice-field"><label>Fecha</label>${fecha}</div>
                <div class="invoice-field"><label>Cliente</label>${h.CNOFAC || '-'}</div>
                <div class="invoice-field"><label>Código Cliente</label>${h.CLIFAC || '-'}</div>
            </div>`;

            // ── Datos del cliente ──
            if (data.cliente) {
                html += `<div class="invoice-cliente-block">
                    <div class="invoice-cliente-header">
                        <span class="invoice-cliente-title"><i data-lucide="user"></i> Datos del Cliente en Factusol</span>
                        ${cuit ? `<button class="btn btn-sm btn-padron" id="btn-consultar-padron"
                            onclick="InvoicesComponent.consultarPadron('${cuit}', '${h.CNOFAC || ''}')">
                            <i data-lucide="search"></i> Consultar ARCA
                        </button>` : '<span class="padron-no-cuit"><i data-lucide="alert-circle"></i> Sin CUIT registrado</span>'}
                    </div>
                    <div class="invoice-header-grid">
                        <div class="invoice-field"><label>CUIT/DNI</label>${cuit || '-'}</div>
                        <div class="invoice-field"><label>Domicilio</label>${data.cliente.DOMCLI || '-'}</div>
                        <div class="invoice-field"><label>Localidad</label>${data.cliente.POBCLI || '-'}</div>
                        <div class="invoice-field"><label>Teléfono</label>${data.cliente.TELCLI || '-'}</div>
                    </div>
                </div>`;
            }

            // Placeholder del panel de padrón (se llena vía consultarPadron)
            html += `<div id="padron-panel" class="padron-panel hidden"></div>`;

            // ── Líneas ──
            html += `<div class="invoice-lines-table"><table><thead><tr>
                <th>Pos</th><th>Artículo</th><th>Descripción</th><th>Cant</th><th>Precio</th><th>IVA%</th><th>Total</th>
            </tr></thead><tbody>`;

            for (const l of data.lines) {
                html += `<tr>
                    <td>${l.POSLFA}</td>
                    <td>${l.ARTLFA || ''}</td>
                    <td>${l.DESLFA || ''}</td>
                    <td>${l.CANLFA || 0}</td>
                    <td>$ ${(l.PRELFA || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
                    <td>${l.PIVLFA || 0}%</td>
                    <td>$ ${(l.TOTLFA || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
                </tr>`;
            }

            html += `</tbody></table></div>`;
            html += `<div class="invoice-total">Total: $ ${(h.TOTFAC || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</div>`;

            // ── CAE status ──
            const caeStatus = await API.get(`/api/arca/status/${tipfac}/${codfac}`).catch(() => ({ validated: false }));
            if (caeStatus.validated) {
                html += `<div class="cae-validated-block">
                    <div class="badge badge-success cae-badge">
                        <i data-lucide="check-circle"></i> CAE: ${caeStatus.cae} | Vto: ${caeStatus.cae_vto}
                    </div>
                    <p class="cae-meta">Cbte ARCA #${caeStatus.voucher_number} — PV ${caeStatus.punto_venta}</p>
                </div>`;
            }

            document.getElementById('modal-invoice-body').innerHTML = html;

            // ── Footer ──
            const footer = document.getElementById('modal-invoice-footer');
            if (!caeStatus.validated && this.currentPv) {
                footer.innerHTML = `
                    <button class="btn btn-secondary modal-close">Cerrar</button>
                    <button class="btn btn-success" onclick="InvoicesComponent.validateInvoice(${tipfac}, ${codfac})">
                        <i data-lucide="check-check"></i> Validar en ARCA
                    </button>`;
            } else {
                footer.innerHTML = '<button class="btn btn-secondary modal-close">Cerrar</button>';
            }

            footer.querySelectorAll('.modal-close').forEach(el => {
                el.addEventListener('click', () => this.closeModal());
            });

            document.getElementById('invoice-modal').classList.remove('hidden');
            if (typeof lucide !== 'undefined') lucide.createIcons();

            // Si ya tenemos datos en caché, mostrarlos directamente
            if (cuit && this._padronCache[cuit]) {
                this._renderPadronPanel(this._padronCache[cuit]);
            }
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    async consultarPadron(cuit, nombreActual) {
        const btn = document.getElementById('btn-consultar-padron');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i data-lucide="loader-2" class="spin-icon"></i> Consultando...';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }

        const panel = document.getElementById('padron-panel');
        if (panel) {
            panel.classList.remove('hidden');
            panel.innerHTML = `<div class="padron-loading">
                <i data-lucide="loader-2" class="spin-icon"></i>
                <span>Consultando Padrón ARCA para CUIT ${cuit}...</span>
            </div>`;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }

        try {
            const data = await API.get(`/api/arca/padron/${cuit}`);
            this._padronCache[cuit] = data;
            this._renderPadronPanel(data, nombreActual);
        } catch (err) {
            if (panel) {
                panel.innerHTML = `<div class="padron-error">
                    <i data-lucide="alert-triangle"></i>
                    <span>Error al consultar padrón: ${err.message}</span>
                </div>`;
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
            App.toast(`No se pudo consultar el padrón ARCA: ${err.message}`, 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i data-lucide="search"></i> Consultar ARCA';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
        }
    },

    _renderPadronPanel(data, nombreActual) {
        const panel = document.getElementById('padron-panel');
        if (!panel) return;

        panel.classList.remove('hidden');

        // Determinar estado visual del CUIT
        const estadoClass = data.estado_cuit === 'ACTIVO' ? 'padron-estado-activo'
            : data.estado_cuit === 'INACTIVO' ? 'padron-estado-inactivo'
            : 'padron-estado-nd';

        // Armar nombre completo para persona física
        const nombreCompleto = data.tipo_persona === 'FISICA'
            ? `${data.apellido || ''} ${data.nombre || ''}`.trim()
            : data.razon_social || '';

        const dom = data.domicilio_fiscal || {};
        const domStr = [dom.calle, dom.numero, dom.piso, dom.depto].filter(Boolean).join(' ');
        const locStr = [dom.localidad, dom.provincia, dom.cp].filter(Boolean).join(' · ');

        // Detectar diferencias con lo que hay en Factusol
        const factNombre = (nombreActual || '').trim().toLowerCase();
        const arcaNombre = nombreCompleto.toLowerCase();
        const hasDiff = factNombre && arcaNombre && factNombre !== arcaNombre;

        panel.innerHTML = `
            <div class="padron-result">
                <div class="padron-result-header">
                    <div class="padron-result-title">
                        <i data-lucide="shield-check"></i>
                        <span>Datos en el Padrón ARCA</span>
                    </div>
                    <span class="padron-estado ${estadoClass}">
                        ${data.estado_cuit || 'N/D'}
                    </span>
                </div>

                <div class="padron-data-grid">
                    <div class="padron-field">
                        <label>CUIT</label>
                        <span class="padron-value">${this._formatCuit(data.cuit)}</span>
                    </div>
                    <div class="padron-field">
                        <label>Tipo Persona</label>
                        <span class="padron-value">${data.tipo_persona || '-'}</span>
                    </div>
                    <div class="padron-field padron-field-wide">
                        <label>Razón Social / Nombre</label>
                        <span class="padron-value padron-nombre ${hasDiff ? 'padron-diff' : ''}">
                            ${nombreCompleto || data.razon_social || '-'}
                            ${hasDiff ? '<span class="padron-diff-badge" title="Difiere del nombre en Factusol">≠ Factusol</span>' : ''}
                        </span>
                    </div>
                    <div class="padron-field padron-field-wide">
                        <label>Condición IVA</label>
                        <span class="padron-value">${data.condicion_iva || '-'}</span>
                    </div>
                    ${domStr ? `<div class="padron-field padron-field-wide">
                        <label>Domicilio Fiscal</label>
                        <span class="padron-value">${domStr}</span>
                    </div>` : ''}
                    ${locStr ? `<div class="padron-field padron-field-wide">
                        <label>Localidad · CP</label>
                        <span class="padron-value">${locStr}</span>
                    </div>` : ''}
                </div>

                ${hasDiff ? `<div class="padron-diff-alert">
                    <i data-lucide="alert-circle"></i>
                    <span>El nombre en Factusol (<strong>${nombreActual}</strong>) difiere del Padrón ARCA (<strong>${nombreCompleto}</strong>). Revisar en Factusol.</span>
                </div>` : ''}

                <div class="padron-footer-note">
                    <i data-lucide="info"></i>
                    Datos obtenidos en tiempo real del Padrón ARCA. La actualización en Factusol debe realizarse manualmente.
                </div>
            </div>`;

        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    _formatCuit(cuit) {
        if (!cuit || cuit.length !== 11) return cuit || '-';
        return `${cuit.slice(0,2)}-${cuit.slice(2,10)}-${cuit.slice(10)}`;
    },

    async validateInvoice(tipfac, codfac) {
        if (!this.currentPv) {
            App.toast('No tiene un punto de venta seleccionado', 'error');
            return;
        }

        if (!confirm(`¿Validar factura ${tipfac}-${codfac} en ARCA?\nPunto de Venta: ${this.currentPv.punto_venta}\nTipo: ${DashboardComponent.tipoComprobante(this.currentPv.tipo_comprobante)}`)) {
            return;
        }

        try {
            const result = await API.post(`/api/arca/validate/${tipfac}/${codfac}?pv_id=${this.currentPv.id}`);
            App.toast(result.message, result.status === 'ok' || result.status === 'already_validated' ? 'success' : 'info');

            this.closeModal();
            this.loadInvoices();
        } catch (err) {
            App.toast(`Error: ${err.message}`, 'error');
        }
    },

    closeModal() {
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
