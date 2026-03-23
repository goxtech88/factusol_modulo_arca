/**
 * Config Component - System configuration.
 */
const ConfigComponent = {
    init() {
        document.getElementById('config-empresa-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await API.put('/api/config/empresa', {
                    razon_social: document.getElementById('cfg-razon-social').value,
                    cuit: document.getElementById('cfg-cuit').value,
                    domicilio: document.getElementById('cfg-domicilio').value,
                    inicio_actividades: document.getElementById('cfg-inicio-actividades').value,
                    condicion_iva: document.getElementById('cfg-condicion-iva').value,
                    concepto_facturacion: parseInt(document.getElementById('cfg-concepto').value) || 1,
                });
                App.toast('Configuración de empresa guardada', 'success');
                App.loadEmpresaName();
            } catch (err) { App.toast(err.message, 'error'); }
        });

        document.getElementById('config-factusol-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await API.put('/api/config/factusol', {
                    db_path: document.getElementById('cfg-db-path').value,
                });
                App.toast('Ruta de base de datos guardada', 'success');
            } catch (err) { App.toast(err.message, 'error'); }
        });

        document.getElementById('config-arca-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const arcaData = {
                environment: document.getElementById('cfg-environment').value,
                cert_path: document.getElementById('cfg-cert-path').value,
                key_path: document.getElementById('cfg-key-path').value,
            };
            try {
                await API.put('/api/config/arca', arcaData);
                App.toast('Configuración ARCA guardada', 'success');
            } catch (err) { App.toast(err.message, 'error'); }
        });

        document.getElementById('config-license-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const result = await API.put('/api/config/license', {
                    key: document.getElementById('cfg-license-key').value,
                });
                App.toast(result.message, result.valid ? 'success' : 'error');
                this._updateLicenseBar(result.valid);
                if (result.valid) App._checkLicense();
            } catch (err) { App.toast(err.message, 'error'); }
        });

        document.getElementById('btn-test-db').addEventListener('click', async () => {
            const el = document.getElementById('db-test-result');
            el.classList.remove('hidden', 'success', 'error');
            el.textContent = 'Probando...';
            try {
                const result = await API.get('/api/factusol/test-connection');
                if (result.status === 'ok') {
                    el.className = 'test-result success';
                    el.textContent = `Conectado: ${result.facturas} facturas, ${result.clientes} clientes, ${result.articulos} articulos`;
                } else {
                    el.className = 'test-result error';
                    el.textContent = `${result.message}`;
                }
            } catch (err) {
                el.className = 'test-result error';
                el.textContent = `${err.message}`;
            }
        });

        document.getElementById('btn-test-arca').addEventListener('click', async () => {
            const el = document.getElementById('arca-test-result');
            el.classList.remove('hidden', 'success', 'error');
            el.textContent = 'Autenticando con AFIP (WSAA)...';
            try {
                const result = await API.get('/api/arca/server-status');
                if (result.status === 'ok') {
                    const d = result.detail || {};
                    el.className = 'test-result success';
                    el.innerHTML = `
                        Autenticacion con WSAA exitosa<br>
                        AppServer: <strong>${d.AppServer || 'OK'}</strong> &nbsp;|&nbsp;
                        DbServer: <strong>${d.DbServer || 'OK'}</strong> &nbsp;|&nbsp;
                        AuthServer: <strong>${d.AuthServer || 'OK'}</strong>
                    `;
                } else {
                    el.className = 'test-result error';
                    el.textContent = `Error: ${result.message}`;
                }
            } catch (err) {
                el.className = 'test-result error';
                el.textContent = `Error: ${err.message}`;
            }
        });
    },

    async load() {
        try {
            const config = await API.get('/api/config');

            // Empresa
            document.getElementById('cfg-razon-social').value = config.empresa?.razon_social || '';
            document.getElementById('cfg-cuit').value = config.empresa?.cuit || '';
            document.getElementById('cfg-domicilio').value = config.empresa?.domicilio || '';
            document.getElementById('cfg-inicio-actividades').value = config.empresa?.inicio_actividades || '';
            document.getElementById('cfg-condicion-iva').value = config.empresa?.condicion_iva || 'Responsable Inscripto';
            document.getElementById('cfg-concepto').value = String(config.empresa?.concepto_facturacion || 1);

            // Factusol
            document.getElementById('cfg-db-path').value = config.factusol?.db_path || '';

            // ARCA
            document.getElementById('cfg-environment').value = config.arca?.environment || 'development';
            document.getElementById('cfg-cert-path').value = config.arca?.cert_path || '';
            document.getElementById('cfg-key-path').value = config.arca?.key_path || '';

            // Licencia
            document.getElementById('cfg-license-key').value = config.license_key || '';
            this._updateLicenseBar(config.license?.valid);
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    // --- Explorador de Archivos Nativo (Windows) ---
    // Llama al servidor que abre el diálogo de Windows directamente.
    async browseFile(targetInputId, extensions = '') {
        const btn = document.querySelector(`[onclick*="${targetInputId}"]`);
        const iconFolder = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>`;
        const iconSpin   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" style="animation:spin .8s linear infinite"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" opacity=".25"/><path d="M12 3a9 9 0 019 9" stroke-linecap="round"/></svg>`;

        if (btn) { btn.disabled = true; btn.innerHTML = iconSpin; }

        try {
            const data = await API.get(
                `/api/config/browse-dialog?extensions=${encodeURIComponent(extensions)}`
            );
            if (data.path) {
                document.getElementById(targetInputId).value = data.path;
            }
        } catch (err) {
            App.toast('Error al abrir el explorador: ' + err.message, 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = iconFolder; }
        }
    },

    _updateLicenseBar(valid) {
        const bar = document.getElementById('license-status-bar');
        if (!bar) return;
        if (valid) {
            bar.className = 'license-bar license-valid';
            bar.innerHTML = '<i data-lucide="check-circle"></i> Licencia activa';
        } else {
            bar.className = 'license-bar license-invalid';
            bar.innerHTML = '<i data-lucide="alert-triangle"></i> Sin licencia — Panel de Usuarios bloqueado';
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },
};
