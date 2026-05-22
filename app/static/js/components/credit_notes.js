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
                <td style="text-align:center">
                    <button class="btn btn-sm btn-secondary" title="Imprimir / PDF de la nota de credito"
                        onclick="CreditNotesComponent.printNC(${nc.id})">
                        <i data-lucide="printer"></i>
                    </button>
                </td>
            </tr>`;
        }).join('');
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    // ── Imprimir / PDF de la NC (informacion fiscal minima) ─────────────────
    async printNC(id) {
        let d;
        try {
            d = await API.get(`/api/credit-notes/${id}/comprobante`);
        } catch (err) {
            App.toast(err.message || 'No se pudieron obtener los datos de la NC', 'error');
            return;
        }

        const esc = (s) => String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const fmt = (n) => Number(n || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        const fmtCuit = (c) => (c && c.length === 11) ? `${c.slice(0,2)}-${c.slice(2,10)}-${c.slice(10)}` : (c || '-');
        const fmtFecha = (f) => {
            if (!f) return '-';
            const m = String(f).match(/(\d{4})-(\d{2})-(\d{2})/);
            return m ? `${m[3]}/${m[2]}/${m[1]}` : f;
        };

        const em = d.emisor || {};
        const cl = d.cliente || {};
        const asoc = d.cmp_asoc || {};
        const docLabel = cl.tipo_doc === 80 ? 'CUIT' : (cl.tipo_doc === 96 ? 'DNI' : 'Doc.');
        // La ventana de impresion es about:blank: el src debe ser absoluto (con origin)
        // para que el QR (servido desde /static/qr/) resuelva correctamente.
        const qrSrc = d.qr_url ? (window.location.origin + d.qr_url) : '';
        const qrImg = qrSrc
            ? `<img id="nc-qr" src="${esc(qrSrc)}" alt="QR AFIP" style="width:130px;height:130px">`
            : '<div style="font-size:11px;color:#900">QR no disponible</div>';

        const hayDiscrim = Number(d.imp_iva || 0) > 0;
        const importesRows = hayDiscrim
            ? `<div class="imp-row"><span>Neto Gravado</span><span>$ ${fmt(d.imp_neto)}</span></div>
               <div class="imp-row"><span>IVA</span><span>$ ${fmt(d.imp_iva)}</span></div>
               <div class="imp-row total"><span>TOTAL</span><span>$ ${fmt(d.imp_total)}</span></div>`
            : `<div class="imp-row total"><span>TOTAL</span><span>$ ${fmt(d.imp_total)}</span></div>`;

        const html = `<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>${esc(d.tipo_nombre)} ${esc(d.comprobante_nro)}</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: Arial, Helvetica, sans-serif; font-size:13px; color:#111; padding:24px; }
  .doc { border:1px solid #333; }
  .top { display:flex; border-bottom:1px solid #333; position:relative; }
  .top .col { flex:1; padding:12px 16px; }
  .top .col.left { border-right:0; }
  .letra-box { position:absolute; left:50%; top:0; transform:translateX(-50%);
    width:64px; border-left:1px solid #333; border-right:1px solid #333; border-bottom:1px solid #333;
    text-align:center; padding:6px 0; background:#fff; }
  .letra-box .letra { font-size:34px; font-weight:700; line-height:1; }
  .letra-box .cod { font-size:9px; }
  h1 { font-size:16px; margin-bottom:6px; }
  .muted { color:#444; font-size:12px; }
  .ot { text-align:right; }
  .ot .tit { font-size:18px; font-weight:700; }
  .ot .nro { font-size:14px; font-weight:700; margin-top:4px; }
  .section { padding:10px 16px; border-bottom:1px solid #333; }
  .row2 { display:flex; gap:24px; flex-wrap:wrap; }
  .row2 > div { font-size:12px; }
  .label { color:#555; }
  .imp { padding:10px 16px; display:flex; flex-direction:column; align-items:flex-end; gap:3px; border-bottom:1px solid #333; }
  .imp-row { display:flex; gap:24px; font-size:13px; min-width:240px; justify-content:space-between; }
  .imp-row span:last-child { font-family:Consolas,monospace; }
  .imp-row.total { border-top:2px solid #333; padding-top:5px; font-weight:700; font-size:15px; }
  .cae { display:flex; align-items:center; gap:18px; padding:12px 16px; }
  .cae .data { flex:1; font-size:13px; }
  .cae .data .big { font-size:15px; font-weight:700; }
  .foot { margin-top:10px; text-align:center; font-size:10px; color:#777; }
  @media print { body { padding:0; } @page { margin:12mm; } }
</style></head>
<body>
  <div class="doc">
    <div class="top">
      <div class="letra-box">
        <div class="letra">${esc(d.letra || 'X')}</div>
        <div class="cod">COD. ${String(d.codigo_afip || '').padStart(3,'0')}</div>
      </div>
      <div class="col left">
        <h1>${esc(em.razon_social || 'Empresa')}</h1>
        <div class="muted">${esc(em.domicilio || '')}</div>
        <div class="muted">CUIT: ${fmtCuit(em.cuit)}</div>
        <div class="muted">${esc(em.condicion_iva || '')}</div>
        ${em.inicio_actividades ? `<div class="muted">Inicio actividades: ${esc(em.inicio_actividades)}</div>` : ''}
      </div>
      <div class="col ot">
        <div class="tit">NOTA DE CRÉDITO ${esc(d.letra || '')}</div>
        <div class="nro">N° ${esc(d.comprobante_nro)}</div>
        <div class="muted">Fecha: ${fmtFecha(d.fecha)}</div>
      </div>
    </div>

    <div class="section">
      <div class="row2">
        <div><span class="label">Cliente:</span> <strong>${esc(cl.nombre || '-')}</strong></div>
        <div><span class="label">${docLabel}:</span> ${esc(cl.doc || '-')}</div>
        ${cl.condicion_iva ? `<div><span class="label">Cond. IVA:</span> ${esc(cl.condicion_iva)}</div>` : ''}
      </div>
      ${cl.domicilio ? `<div class="row2" style="margin-top:4px"><div><span class="label">Domicilio:</span> ${esc(cl.domicilio)}</div></div>` : ''}
    </div>

    <div class="section">
      <div class="row2">
        <div><span class="label">Comprobante asociado:</span> ${asoc.nro_fmt ? `${esc(asoc.tipo_nombre || 'Factura')} N° ${esc(asoc.nro_fmt)}` : esc(d.factura_origen || '-')}</div>
        <div><span class="label">Factura (Factusol):</span> <strong>${esc(d.factura_origen || '-')}</strong></div>
        ${d.motivo ? `<div><span class="label">Motivo:</span> ${esc(d.motivo)}</div>` : ''}
      </div>
    </div>

    <div class="imp">${importesRows}</div>

    <div class="cae">
      ${qrImg}
      <div class="data">
        <div class="big">CAE N°: ${esc(d.cae || '-')}</div>
        <div>Vto. CAE: ${fmtFecha(d.cae_vto)}</div>
      </div>
    </div>
  </div>
  <div class="foot">Comprobante autorizado por ARCA (AFIP) — Generado por Factusol ARCA Sync</div>

  <script>
    function go(){ try { window.print(); } catch(e){} }
    var qr = document.getElementById('nc-qr');
    if (!qr) { window.onload = go; }
    else if (qr.complete) { go(); }
    else { qr.onload = go; qr.onerror = go; setTimeout(go, 1500); }
  </script>
</body></html>`;

        const w = window.open('', '_blank');
        if (!w) {
            App.toast('Permití las ventanas emergentes para imprimir', 'warning');
            return;
        }
        w.document.write(html);
        w.document.close();
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
