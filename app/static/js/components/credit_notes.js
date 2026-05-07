/**
 * Credit Notes Component — Notas de Credito ARCA.
 *
 * Permite listar las NC emitidas, filtrar por fechas/cliente y emitir una NC
 * nueva (total o parcial) asociada a una factura original.
 */
const CreditNotesComponent = {
    _selectedInvoice: null,
    _searchTimer: null,
    _lastSearchResults: [],

    init() {
        // Cierre del modal
        document.querySelectorAll('#emit-nc-modal .modal-close, #emit-nc-modal .modal-overlay')
            .forEach(el => el.addEventListener('click', () => this._closeModal()));

        // Busqueda de facturas con debounce
        const searchInput = document.getElementById('nc-invoice-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this._searchTimer);
                const q = e.target.value.trim();
                this._searchTimer = setTimeout(() => this.searchInvoice(q), 300);
            });
        }

        // Filtro por cliente con debounce
        const clienteInput = document.getElementById('nc-filter-cliente');
        if (clienteInput) {
            clienteInput.addEventListener('input', App.debounce(() => this.load(), 400));
        }
    },

    async load() {
        try {
            const from = document.getElementById('nc-filter-from')?.value || '';
            const to = document.getElementById('nc-filter-to')?.value || '';
            const cliente = document.getElementById('nc-filter-cliente')?.value || '';
            const params = new URLSearchParams();
            if (from) params.set('from', from);
            if (to) params.set('to', to);
            if (cliente) params.set('cliente', cliente);
            const qs = params.toString();
            const url = '/api/credit-notes/' + (qs ? '?' + qs : '');
            const items = await API.get(url);
            this.renderList(items);
        } catch (err) {
            App.toast(err.message || 'Error al cargar NC', 'error');
        }
    },

    renderList(items) {
        const tbody = document.getElementById('credit-notes-tbody');
        const empty = document.getElementById('credit-notes-empty');
        if (!tbody) return;
        if (!items || items.length === 0) {
            tbody.innerHTML = '';
            empty?.classList.remove('hidden');
            return;
        }
        empty?.classList.add('hidden');
        tbody.innerHTML = items.map(nc => {
            const fecha = nc.created_at ? new Date(nc.created_at).toLocaleDateString('es-AR') : '-';
            const pvNro = `${String(nc.punto_venta).padStart(4, '0')}-${String(nc.voucher_number).padStart(8, '0')}`;
            const origen = (nc.cmp_asoc_tipo && nc.cmp_asoc_nro)
                ? `${String(nc.cmp_asoc_pv || 0).padStart(4, '0')}-${String(nc.cmp_asoc_nro).padStart(8, '0')}`
                : '-';
            const importe = nc.imp_total != null
                ? Number(nc.imp_total).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                : '-';
            return `<tr>
                <td>${fecha}</td>
                <td>${nc.tipo_nombre || ''}</td>
                <td>${pvNro}</td>
                <td>${nc.cliente_nombre || '-'}</td>
                <td>${origen}</td>
                <td>${nc.motivo || '-'}</td>
                <td style="text-align:right">${importe}</td>
                <td>${nc.cae || '-'}</td>
            </tr>`;
        }).join('');
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    showEmitModal() {
        this._selectedInvoice = null;
        const modal = document.getElementById('emit-nc-modal');
        if (!modal) return;
        modal.classList.remove('hidden');
        document.getElementById('nc-invoice-search').value = '';
        document.getElementById('nc-search-results').innerHTML = '';
        document.getElementById('nc-selected-invoice').classList.add('hidden');
        document.getElementById('nc-selected-invoice').innerHTML = '';
        document.getElementById('nc-motivo').value = 'Devolucion';
        document.getElementById('nc-total-check').checked = true;
        document.getElementById('nc-parcial-group').classList.add('hidden');
        document.getElementById('nc-importe').value = '';
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    _closeModal() {
        document.getElementById('emit-nc-modal')?.classList.add('hidden');
    },

    _toggleTotal(isTotal) {
        const group = document.getElementById('nc-parcial-group');
        if (!group) return;
        if (isTotal) {
            group.classList.add('hidden');
        } else {
            group.classList.remove('hidden');
        }
    },

    async searchInvoice(query) {
        const container = document.getElementById('nc-search-results');
        if (!container) return;
        if (!query) {
            container.innerHTML = '';
            return;
        }
        try {
            const results = await API.get('/api/credit-notes/search-invoice?q=' + encodeURIComponent(query));
            this._lastSearchResults = results;
            if (!results.length) {
                container.innerHTML = '<div class="nc-search-empty">Sin resultados</div>';
                return;
            }
            container.innerHTML = results.map(r => {
                const pvNro = `${String(r.punto_venta).padStart(4, '0')}-${String(r.voucher_number).padStart(8, '0')}`;
                const importe = r.imp_total != null
                    ? Number(r.imp_total).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                    : '-';
                const disabled = r.has_nc ? ' disabled' : '';
                const badge = r.has_nc ? ' <span style="color:var(--danger);font-size:11px">(ya tiene NC)</span>' : '';
                return `<div class="nc-search-item${disabled}" onclick="${r.has_nc ? '' : `CreditNotesComponent.selectInvoice(${r.id})`}">
                    <div><strong>${r.tipo_nombre}</strong> ${pvNro}${badge}</div>
                    <div style="font-size:12px;color:var(--text-muted)">${r.cliente_nombre || '-'} — $${importe}</div>
                </div>`;
            }).join('');
        } catch (err) {
            App.toast(err.message || 'Error al buscar facturas', 'error');
        }
    },

    selectInvoice(id) {
        try {
            const inv = (this._lastSearchResults || []).find(l => l.id === id);
            if (!inv) {
                App.toast('No se encontro la factura', 'error');
                return;
            }
            this._selectedInvoice = inv;
            const pvNro = `${String(inv.punto_venta).padStart(4, '0')}-${String(inv.voucher_number).padStart(8, '0')}`;
            const importe = inv.imp_total != null
                ? Number(inv.imp_total).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                : '-';
            const tipoNombre = { 1: 'Factura A', 6: 'Factura B', 11: 'Factura C' }[inv.tipo_comprobante] || 'Factura';
            const sel = document.getElementById('nc-selected-invoice');
            sel.classList.remove('hidden');
            sel.innerHTML = `
                <div class="nc-selected-card">
                    <div><strong>${tipoNombre}</strong> ${pvNro}</div>
                    <div>${inv.cliente_nombre || '-'}</div>
                    <div>Total: $${importe}</div>
                    <div style="font-size:11px;color:var(--text-muted)">CAE: ${inv.cae}</div>
                </div>`;
            document.getElementById('nc-search-results').innerHTML = '';
            document.getElementById('nc-invoice-search').value = '';
        } catch (err) {
            App.toast(err.message || 'Error al seleccionar factura', 'error');
        }
    },

    async submitNC() {
        if (!this._selectedInvoice) {
            App.toast('Seleccione una factura original', 'warning');
            return;
        }
        const motivo = document.getElementById('nc-motivo').value;
        const isTotal = document.getElementById('nc-total-check').checked;
        let importe = null;
        if (!isTotal) {
            const v = parseFloat(document.getElementById('nc-importe').value);
            if (!v || v <= 0) {
                App.toast('Ingrese un importe parcial valido', 'warning');
                return;
            }
            importe = v;
        }

        const btn = document.getElementById('btn-emit-nc');
        if (btn) { btn.disabled = true; btn.innerHTML = 'Emitiendo...'; }

        try {
            const payload = {
                cae_log_id_original: this._selectedInvoice.id,
                motivo,
                punto_venta: this._selectedInvoice.punto_venta,
                importe,
            };
            const res = await API.post('/api/credit-notes/', payload);
            App.toast(res.message || 'NC emitida', 'success');
            this._closeModal();
            this.load();
        } catch (err) {
            App.toast(err.message || 'Error al emitir NC', 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i data-lucide="file-minus"></i> Emitir NC';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
        }
    },
};
