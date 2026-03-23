/**
 * Dashboard Component — con Monitor de Servidores ARCA
 */
const DashboardComponent = {
    _monitorTimer: null,

    async load() {
        // Puntos de venta del usuario
        const pvs = Auth.getPuntosVenta();
        document.getElementById('stat-puntos-venta').textContent = pvs.length;

        const pvList = document.getElementById('dashboard-puntos-venta');
        if (pvs.length === 0) {
            pvList.innerHTML = '<p style="color:var(--text-muted)">No tiene puntos de venta asignados. Contacte al administrador.</p>';
        } else {
            pvList.innerHTML = pvs.map(pv => `
                <div class="pv-card">
                    <h4>${pv.nombre}</h4>
                    <p><strong>Punto de Venta ARCA:</strong> ${pv.punto_venta}</p>
                    <p><strong>Serie Factusol:</strong> ${pv.serie_factusol}</p>
                </div>
            `).join('');
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }

        // Test Factusol connection
        try {
            const dbStatus = await API.get('/api/factusol/test-connection');
            const el = document.getElementById('stat-db-status');
            if (dbStatus.status === 'ok') {
                el.textContent = `${dbStatus.facturas} facturas`;
                el.style.color = 'var(--success)';
            } else {
                el.textContent = 'Error';
                el.style.color = 'var(--danger)';
            }
        } catch {
            document.getElementById('stat-db-status').textContent = 'Sin configurar';
        }

        // Test ARCA (simple)
        try {
            const arcaStatus = await API.get('/api/arca/server-status');
            const el = document.getElementById('stat-arca-status');
            if (arcaStatus.status === 'ok') {
                el.textContent = 'Conectado';
                el.style.color = 'var(--success)';
            } else {
                el.textContent = 'Error';
                el.style.color = 'var(--danger)';
            }
        } catch {
            document.getElementById('stat-arca-status').textContent = 'Sin configurar';
        }

        // CAE count
        try {
            const logs = await API.get('/api/arca/logs');
            document.getElementById('stat-cae-count').textContent = logs.length;
        } catch {
            document.getElementById('stat-cae-count').textContent = '-';
        }

        // Cargar monitor ARCA
        this.loadMonitor();
    },

    // ── Monitor de servidores ARCA ────────────────────────────────────────
    async loadMonitor() {
        const container = document.getElementById('monitor-content');
        const btnRefresh = document.getElementById('btn-refresh-monitor');

        // Spinner en botón
        if (btnRefresh) {
            btnRefresh.classList.add('spinning');
            btnRefresh.disabled = true;
        }

        container.innerHTML = `
            <div class="monitor-loading">
                <i data-lucide="loader-2" class="spin-icon"></i>
                <span>Consultando servidores ARCA...</span>
            </div>`;
        if (typeof lucide !== 'undefined') lucide.createIcons();

        try {
            const data = await API.get('/api/arca/server-monitor');
            this._renderMonitor(data);
        } catch (err) {
            container.innerHTML = `
                <div class="monitor-error">
                    <i data-lucide="alert-circle"></i>
                    <span>Error al consultar monitor: ${err.message}</span>
                </div>`;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } finally {
            if (btnRefresh) {
                btnRefresh.classList.remove('spinning');
                btnRefresh.disabled = false;
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
        }
    },

    _renderMonitor(data) {
        const container = document.getElementById('monitor-content');
        const ts = data.timestamp ? new Date(data.timestamp).toLocaleString('es-AR') : '-';

        // Servidores
        const servers = data.servers || {};
        const serverEntries = [
            { key: 'AppServer', label: 'Aplicacion', icon: 'server' },
            { key: 'DbServer', label: 'Base de Datos', icon: 'database' },
            { key: 'AuthServer', label: 'Autenticacion', icon: 'shield' },
        ];

        let html = `<div class="monitor-timestamp">Ultima consulta: ${ts}</div>`;

        // Servidores grid
        html += '<div class="monitor-servers-grid">';
        for (const s of serverEntries) {
            const val = servers[s.key] || 'N/D';
            const isOk = val === 'OK';
            const statusClass = isOk ? 'monitor-ok' : 'monitor-error-status';
            const statusIcon = isOk ? 'check-circle' : 'x-circle';
            html += `
                <div class="monitor-server-card ${statusClass}">
                    <div class="monitor-server-icon">
                        <i data-lucide="${s.icon}"></i>
                    </div>
                    <div class="monitor-server-info">
                        <span class="monitor-server-label">${s.label}</span>
                        <span class="monitor-server-status">
                            <i data-lucide="${statusIcon}"></i> ${val}
                        </span>
                    </div>
                </div>`;
        }
        html += '</div>';

        // Puntos de venta + último comprobante
        if (data.puntos_venta && data.puntos_venta.length > 0) {
            html += '<div class="monitor-pvs">';
            html += '<h4 class="monitor-pvs-title"><i data-lucide="hash"></i> Ultimo Comprobante por Punto de Venta</h4>';
            html += '<div class="monitor-pvs-grid">';
            for (const pv of data.puntos_venta) {
                const tipoLabel = this.tipoComprobante(pv.tipo_comprobante);
                const hasError = !!pv.error;
                html += `
                    <div class="monitor-pv-card ${hasError ? 'monitor-pv-error' : ''}">
                        <div class="monitor-pv-header">
                            <strong>PV ${pv.punto_venta}</strong>
                            <span class="monitor-pv-name">${pv.nombre}</span>
                        </div>
                        <div class="monitor-pv-body">
                            <div class="monitor-pv-field">
                                <label>Tipo Cbte</label>
                                <span>${tipoLabel}</span>
                            </div>
                            <div class="monitor-pv-field">
                                <label>Serie Factusol</label>
                                <span>${pv.serie_factusol}</span>
                            </div>
                            <div class="monitor-pv-field">
                                <label>Ultimo Nro</label>
                                <span class="monitor-pv-cbte ${hasError ? 'text-danger' : ''}">
                                    ${hasError ? 'Error' : (pv.ultimo_cbte || 0)}
                                </span>
                            </div>
                        </div>
                        ${hasError ? `<div class="monitor-pv-error-msg"><i data-lucide="alert-triangle"></i> ${pv.error}</div>` : ''}
                    </div>`;
            }
            html += '</div></div>';
        }

        // Errores globales
        if (data.errors && data.errors.length > 0) {
            html += '<div class="monitor-errors">';
            html += '<h4 class="monitor-errors-title"><i data-lucide="alert-circle"></i> Errores Detectados</h4>';
            for (const err of data.errors) {
                html += `<div class="monitor-error-item"><i data-lucide="x-circle"></i> ${err}</div>`;
            }
            html += '</div>';
        }

        container.innerHTML = html;
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    tipoComprobante(tipo) {
        const map = {
            1: 'Factura A', 2: 'Nota Debito A', 3: 'Nota Credito A',
            6: 'Factura B', 7: 'Nota Debito B', 8: 'Nota Credito B',
            11: 'Factura C', 12: 'Nota Debito C', 13: 'Nota Credito C',
        };
        return map[tipo] || `Tipo ${tipo}`;
    },
};
