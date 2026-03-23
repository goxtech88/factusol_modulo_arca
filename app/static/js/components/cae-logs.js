/**
 * CAE Logs Component
 */
const CAELogsComponent = {
    async load() {
        try {
            const logs = await API.get('/api/arca/logs');
            const tbody = document.getElementById('cae-tbody');

            if (logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted)">No hay comprobantes validados aún</td></tr>';
                return;
            }

            tbody.innerHTML = logs.map(l => `<tr>
                <td>${l.created_at ? new Date(l.created_at).toLocaleString('es-AR') : '-'}</td>
                <td><strong>${l.tipfac}-${l.codfac}</strong></td>
                <td>${l.punto_venta}</td>
                <td>${l.voucher_number}</td>
                <td><span class="badge badge-success">${l.cae}</span></td>
                <td>${l.cae_vto}</td>
                <td>${l.cliente_nombre || '-'}</td>
                <td>$ ${(l.imp_total || 0).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
            </tr>`).join('');
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },
};
