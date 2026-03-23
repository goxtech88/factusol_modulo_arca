/**
 * Dashboard Component
 */
const DashboardComponent = {
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

        // Test ARCA
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
    },

    tipoComprobante(tipo) {
        const map = {
            1: 'Factura A', 2: 'Nota de Débito A', 3: 'Nota de Crédito A',
            6: 'Factura B', 7: 'Nota de Débito B', 8: 'Nota de Crédito B',
            11: 'Factura C', 12: 'Nota de Débito C', 13: 'Nota de Crédito C',
        };
        return map[tipo] || `Tipo ${tipo}`;
    },
};
