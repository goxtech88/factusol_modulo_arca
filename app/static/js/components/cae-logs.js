/**
 * CAE Logs Component — Comprobantes validados con filtro por mes, totales por PV, posición IVA.
 */
const CAELogsComponent = {
    _allLogs: [],
    _monthFilter: '',  // '' = todos, '2026-03' = mes específico

    init() {
        // Setear fecha de hoy en el date picker de Cierre Z
        const dateInput = document.getElementById('cae-cierre-date');
        if (dateInput) {
            dateInput.value = new Date().toISOString().slice(0, 10);
        }
    },

    async load() {
        try {
            const logs = await API.get('/api/arca/logs');
            this._allLogs = logs;
            this._renderMonthSelector(logs);
            this._render();
            App.toast(`${logs.length} comprobante(s) cargado(s)`, logs.length === 0 ? 'warning' : 'success');
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    /**
     * Diagnostico cuando CAE Emitidos aparece vacio: pregunta al backend
     * que hay en la DB, que user esta logueado, y muestra los ultimos 5 CAE.
     */
    async runDiagnostic() {
        try {
            const d = await API.get('/api/arca/diagnostic');
            const u = d.current_user || {};
            const c = d.cae_logs || {};
            const ult = (c.ultimos_5 || []).map((l, i) =>
                `  ${i + 1}. ${l.tipfac_codfac} | PV ${l.punto_venta} | nro ${l.voucher_number} | CAE ${l.cae} | ${l.cliente_nombre || '-'} | $${(l.imp_total || 0).toFixed(2)} | user_id=${l.user_id} | ${l.created_at}`
            ).join('\n') || '  (no hay CAE en la DB)';

            const msg =
`DIAGNOSTICO CAE EMITIDOS — app v${d.version}

USUARIO ACTUAL:
  - id: ${u.id}
  - username: ${u.username}
  - nombre: ${u.full_name || '-'}
  - rol: ${u.role} ${u.is_admin ? '(admin: ve todos los CAE)' : '(usuario: solo los suyos)'}

CAE EN LA BASE DE DATOS:
  - Total global: ${c.total_en_db}
  - Visibles para vos: ${c.visibles_para_este_user}

ULTIMOS 5 CAE EN DB:
${ult}

DB: ${d.db_url}
Empaquetado: ${d.frozen ? 'SI (ejecutable)' : 'NO (modo desarrollo)'}`;

            console.log('Diagnostic response:', d);
            alert(msg);
        } catch (err) {
            App.toast('Error al ejecutar diagnostico: ' + err.message, 'error');
        }
    },

    _renderMonthSelector(logs) {
        const container = document.getElementById('cae-month-filter');
        if (!container) return;

        // Extraer meses únicos
        const months = new Set();
        logs.forEach(l => {
            if (l.created_at) {
                const d = new Date(l.created_at);
                months.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
            }
        });

        const sorted = [...months].sort().reverse();
        const current = this._monthFilter;

        container.innerHTML = `
            <select id="cae-month-select" class="select-styled" onchange="CAELogsComponent.setMonth(this.value)">
                <option value="" ${!current ? 'selected' : ''}>Todos</option>
                ${sorted.map(m => {
                    const [y, mo] = m.split('-');
                    const label = new Date(y, mo - 1).toLocaleDateString('es-AR', { month: 'long', year: 'numeric' });
                    return `<option value="${m}" ${current === m ? 'selected' : ''}>${label}</option>`;
                }).join('')}
            </select>
        `;
    },

    setMonth(month) {
        this._monthFilter = month;
        this._render();
    },

    _getFilteredLogs() {
        if (!this._monthFilter) return this._allLogs;
        return this._allLogs.filter(l => {
            if (!l.created_at) return false;
            const d = new Date(l.created_at);
            const m = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            return m === this._monthFilter;
        });
    },

    _render() {
        const logs = this._getFilteredLogs();
        const tbody = document.getElementById('cae-tbody');
        const summaryDiv = document.getElementById('cae-summary');

        // ── Tabla ──
        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted)">No hay comprobantes en este período</td></tr>';
        } else {
            tbody.innerHTML = logs.map(l => `<tr>
                <td>${l.created_at ? new Date(l.created_at).toLocaleString('es-AR') : '-'}</td>
                <td><strong>${l.tipfac}-${l.codfac}</strong></td>
                <td>${l.punto_venta}</td>
                <td>${l.voucher_number}</td>
                <td><span class="badge badge-success">${l.cae}</span></td>
                <td>${l.cae_vto}</td>
                <td>${l.cliente_nombre || '-'}</td>
                <td class="text-right">$ ${(l.imp_total || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
            </tr>`).join('');
        }

        // ── Resumen por PV + Posición IVA ──
        if (!summaryDiv) return;

        // Agrupar por PV
        const byPv = {};
        let grandTotal = 0, grandNeto = 0, grandIva = 0;
        logs.forEach(l => {
            const pv = l.punto_venta || '?';
            if (!byPv[pv]) byPv[pv] = { count: 0, total: 0, neto: 0, iva: 0 };
            byPv[pv].count++;
            byPv[pv].total += (l.imp_total || 0);
            byPv[pv].neto += (l.imp_neto || 0);
            byPv[pv].iva += (l.imp_iva || 0);
            grandTotal += (l.imp_total || 0);
            grandNeto += (l.imp_neto || 0);
            grandIva += (l.imp_iva || 0);
        });

        const fmt = (n) => n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        let html = '<div class="cae-summary-grid">';

        // Cards por PV
        Object.entries(byPv).forEach(([pv, data]) => {
            html += `
                <div class="cae-summary-card">
                    <div class="cae-summary-pv">PV ${pv}</div>
                    <div class="cae-summary-count">${data.count} cbt(s)</div>
                    <div class="cae-summary-row">
                        <span>Total</span><strong>$ ${fmt(data.total)}</strong>
                    </div>
                    <div class="cae-summary-row">
                        <span>Neto Gravado</span><span>$ ${fmt(data.neto)}</span>
                    </div>
                    <div class="cae-summary-row">
                        <span>IVA</span><span>$ ${fmt(data.iva)}</span>
                    </div>
                </div>`;
        });

        // Card total consolidado
        if (Object.keys(byPv).length > 0) {
            html += `
                <div class="cae-summary-card cae-summary-total">
                    <div class="cae-summary-pv">TOTAL</div>
                    <div class="cae-summary-count">${logs.length} cbt(s)</div>
                    <div class="cae-summary-row">
                        <span>Total Facturado</span><strong>$ ${fmt(grandTotal)}</strong>
                    </div>
                    <div class="cae-summary-row">
                        <span>Neto Gravado</span><span>$ ${fmt(grandNeto)}</span>
                    </div>
                    <div class="cae-summary-row iva-position">
                        <span>Posición IVA (Débito Fiscal)</span><strong>$ ${fmt(grandIva)}</strong>
                    </div>
                </div>`;
        }

        html += '</div>';
        summaryDiv.innerHTML = html;
    },

    // ── Informe Cierre Z ─────────────────────────────────────────────────
    async printCierreZ() {
        const dateInput = document.getElementById('cae-cierre-date');
        const fecha = dateInput ? dateInput.value : '';
        if (!fecha) {
            App.toast('Seleccioná una fecha para el informe', 'error');
            return;
        }

        // Filtrar logs del día seleccionado
        const logs = this._allLogs.filter(l => {
            if (!l.created_at) return false;
            return l.created_at.slice(0, 10) === fecha;
        });

        if (logs.length === 0) {
            App.toast('No hay comprobantes emitidos en la fecha seleccionada', 'error');
            return;
        }

        // Obtener datos de empresa
        let empresa = { razon_social: '', cuit: '', domicilio: '' };
        try {
            const config = await API.get('/api/config');
            empresa = config.empresa || empresa;
        } catch (_) {}

        // Agrupar por PV
        const byPv = {};
        let grandTotal = 0, grandNeto = 0, grandIva = 0;
        logs.forEach(l => {
            const pv = l.punto_venta || '?';
            if (!byPv[pv]) byPv[pv] = { count: 0, total: 0, neto: 0, iva: 0 };
            byPv[pv].count++;
            byPv[pv].total += (l.imp_total || 0);
            byPv[pv].neto += (l.imp_neto || 0);
            byPv[pv].iva += (l.imp_iva || 0);
            grandTotal += (l.imp_total || 0);
            grandNeto += (l.imp_neto || 0);
            grandIva += (l.imp_iva || 0);
        });

        const fmt = (n) => n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        const fechaFmt = new Date(fecha + 'T12:00:00').toLocaleDateString('es-AR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        const ahora = new Date().toLocaleString('es-AR');

        // Generar filas de la tabla
        let rowsHtml = '';
        logs.forEach((l, i) => {
            const hora = l.created_at ? new Date(l.created_at).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : '';
            rowsHtml += `<tr>
                <td style="text-align:center">${i + 1}</td>
                <td>${hora}</td>
                <td><strong>${l.tipfac}-${l.codfac}</strong></td>
                <td style="text-align:center">${l.punto_venta}</td>
                <td style="text-align:center">${l.voucher_number}</td>
                <td style="font-size:11px">${l.cae}</td>
                <td>${l.cliente_nombre || '-'}</td>
                <td style="text-align:right;font-family:Consolas,monospace">$ ${fmt(l.imp_total || 0)}</td>
            </tr>`;
        });

        // Resumen por PV
        let pvHtml = '';
        Object.entries(byPv).forEach(([pv, d]) => {
            pvHtml += `<tr>
                <td><strong>PV ${pv}</strong></td>
                <td style="text-align:center">${d.count}</td>
                <td style="text-align:right;font-family:Consolas,monospace">$ ${fmt(d.neto)}</td>
                <td style="text-align:right;font-family:Consolas,monospace">$ ${fmt(d.iva)}</td>
                <td style="text-align:right;font-family:Consolas,monospace"><strong>$ ${fmt(d.total)}</strong></td>
            </tr>`;
        });

        // Formatear CUIT
        const cuit = empresa.cuit || '';
        const cuitFmt = cuit.length === 11 ? `${cuit.slice(0,2)}-${cuit.slice(2,10)}-${cuit.slice(10)}` : cuit;

        const html = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Cierre Z — ${fecha}</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: Arial, Helvetica, sans-serif; font-size: 13px; color: #111; padding: 20px; }
    .header { text-align: center; margin-bottom: 16px; }
    .header h1 { font-size: 18px; margin-bottom: 2px; }
    .header p { font-size: 12px; color: #444; }
    .header .fecha { font-size: 14px; font-weight: bold; margin-top: 8px; }
    hr { border: none; border-top: 1px solid #333; margin: 12px 0; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 16px; }
    th, td { border: 1px solid #999; padding: 4px 6px; font-size: 12px; }
    th { background: #eee; font-weight: 700; text-align: left; }
    .resumen th { background: #ddd; }
    .total-row td { border-top: 2px solid #333; font-weight: 700; font-size: 13px; }
    .footer { margin-top: 20px; font-size: 11px; color: #666; text-align: center; }
    @media print {
        body { padding: 0; }
        @page { margin: 15mm 10mm; }
    }
</style>
</head>
<body>
    <div class="header">
        <h1>${empresa.razon_social || 'Empresa'}</h1>
        <p>CUIT: ${cuitFmt || '-'}</p>
        <p>${empresa.domicilio || ''}</p>
        <hr>
        <div class="fecha">INFORME CIERRE Z — ${fechaFmt.toUpperCase()}</div>
    </div>
    <hr>

    <table>
        <thead>
            <tr>
                <th style="width:30px;text-align:center">#</th>
                <th style="width:50px">Hora</th>
                <th>Serie-Nro</th>
                <th style="text-align:center">PV</th>
                <th style="text-align:center">Cbte</th>
                <th>CAE</th>
                <th>Cliente</th>
                <th style="text-align:right">Total</th>
            </tr>
        </thead>
        <tbody>
            ${rowsHtml}
        </tbody>
    </table>

    <table class="resumen">
        <thead>
            <tr>
                <th>Punto de Venta</th>
                <th style="text-align:center">Cant.</th>
                <th style="text-align:right">Neto Gravado</th>
                <th style="text-align:right">IVA</th>
                <th style="text-align:right">Total</th>
            </tr>
        </thead>
        <tbody>
            ${pvHtml}
            <tr class="total-row">
                <td><strong>TOTAL</strong></td>
                <td style="text-align:center">${logs.length}</td>
                <td style="text-align:right;font-family:Consolas,monospace">$ ${fmt(grandNeto)}</td>
                <td style="text-align:right;font-family:Consolas,monospace">$ ${fmt(grandIva)}</td>
                <td style="text-align:right;font-family:Consolas,monospace">$ ${fmt(grandTotal)}</td>
            </tr>
        </tbody>
    </table>

    <hr>
    <div class="footer">
        Emitido: ${ahora} — Factusol ARCA Sync
    </div>

    <script>window.onload = function() { window.print(); }</script>
</body>
</html>`;

        const w = window.open('', '_blank');
        w.document.write(html);
        w.document.close();
    },

    // ── Exportador RG 1361 (Duplicado Electrónico) ──────────────────────
    async exportRG1361() {
        // Determinar período: usa el filtro de mes si está seleccionado, sino mes en curso
        let year, month;
        if (this._monthFilter) {
            const [y, m] = this._monthFilter.split('-');
            year = parseInt(y, 10);
            month = parseInt(m, 10);
        } else {
            const now = new Date();
            year = now.getFullYear();
            month = now.getMonth() + 1;
        }

        // Confirmación con detalle del período
        const periodoLabel = new Date(year, month - 1).toLocaleDateString('es-AR', { month: 'long', year: 'numeric' });
        const ok = confirm(
            `Generar archivos RG 1361 del período: ${periodoLabel}\n\n` +
            `Se descargará un ZIP con:\n` +
            `  • CABECERA_${year}${String(month).padStart(2, '0')}.txt\n` +
            `  • DETALLE_${year}${String(month).padStart(2, '0')}.txt\n\n` +
            `¿Continuar?`
        );
        if (!ok) return;

        try {
            const url = `/api/arca/rg1361/export?year=${year}&month=${month}`;
            const resp = await fetch(url, {
                headers: { 'Authorization': `Bearer ${API.token}` },
            });

            if (!resp.ok) {
                let detail = `Error ${resp.status}`;
                try { const j = await resp.json(); detail = j.detail || detail; } catch (_) {}
                App.toast(detail, 'error');
                return;
            }

            const count = resp.headers.get('X-Comprobantes-Count') || '?';
            const cd = resp.headers.get('Content-Disposition') || '';
            const m = /filename="([^"]+)"/.exec(cd);
            const filename = m ? m[1] : `RG1361_${year}${String(month).padStart(2, '0')}.zip`;

            const blob = await resp.blob();
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);

            App.toast(`Generados ${count} comprobante(s) — ${filename}`, 'success');
        } catch (err) {
            App.toast(err.message || 'Error al generar RG 1361', 'error');
        }
    },
};
