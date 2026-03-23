/**
 * CAE Logs Component — Comprobantes validados con filtro por mes, totales por PV, posición IVA.
 */
const CAELogsComponent = {
    _allLogs: [],
    _monthFilter: '',  // '' = todos, '2026-03' = mes específico

    init() {
        // El select de mes se crea dinámicamente al cargar
    },

    async load() {
        try {
            const logs = await API.get('/api/arca/logs');
            this._allLogs = logs;
            this._renderMonthSelector(logs);
            this._render();
        } catch (err) {
            App.toast(err.message, 'error');
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
};
