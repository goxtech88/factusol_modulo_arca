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

        // Botón "Consultar CUIT" en empresa - autocompleta datos fiscales
        document.getElementById('btn-lookup-cuit').addEventListener('click', async () => {
            const cuit = document.getElementById('cfg-cuit').value.replace(/[^0-9]/g, '').trim();
            if (!cuit || cuit.length < 10) {
                App.toast('Ingresá un CUIT válido (10-11 dígitos)', 'error');
                return;
            }
            const btn = document.getElementById('btn-lookup-cuit');
            btn.disabled = true;
            btn.innerHTML = '<i data-lucide="loader-2" class="spin-icon"></i> Consultando...';
            if (typeof lucide !== 'undefined') lucide.createIcons();

            try {
                const data = await API.get(`/api/arca/padron/${cuit}`);
                // Autocompletar campos
                if (data.razon_social) {
                    document.getElementById('cfg-razon-social').value = data.razon_social;
                }
                if (data.domicilio_fiscal) {
                    const dom = data.domicilio_fiscal;
                    const parts = [dom.calle, dom.numero, dom.piso, dom.depto].filter(Boolean);
                    const loc = [dom.localidad, dom.provincia, dom.cp].filter(Boolean);
                    const full = parts.concat(loc).join(', ');
                    if (full) document.getElementById('cfg-domicilio').value = full;
                }
                // Mapear condición IVA
                if (data.condicion_iva) {
                    const condLower = data.condicion_iva.toLowerCase();
                    const select = document.getElementById('cfg-condicion-iva');
                    if (condLower.includes('monotributo')) select.value = 'Monotributista';
                    else if (condLower.includes('exento')) select.value = 'Exento';
                    else if (condLower.includes('inscripto')) select.value = 'Responsable Inscripto';
                }
                App.toast(`✅ Datos obtenidos: ${data.razon_social || 'OK'}`, 'success');
            } catch (err) {
                App.toast(`Error al consultar CUIT: ${err.message}`, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i data-lucide="search"></i> Consultar';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
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

            // Plan / Licencia
            this._updateLicenseBar(config.license);
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

    // ── Generador de Certificado AFIP ──────────────────────────────────
    async generateCert() {
        const btn = document.getElementById('btn-generate-cert');
        const result = document.getElementById('cert-gen-result');
        btn.disabled = true;
        btn.innerHTML = '<i data-lucide="loader-2" class="spin-icon"></i> Generando...';
        if (typeof lucide !== 'undefined') lucide.createIcons();

        try {
            const data = await API.post('/api/config/generate-cert');
            // Auto-rellenar key_path
            document.getElementById('cfg-key-path').value = data.key_path;

            result.classList.remove('hidden');
            result.innerHTML = `
                <div class="test-result success" style="white-space:normal">
                    <strong>Certificado generado correctamente</strong><br>
                    <span style="font-size:11px">
                        Clave privada: <code>${data.key_path}</code><br>
                        CSR: <code>${data.csr_path}</code>
                    </span>
                </div>
                <div class="info-note" style="margin-top:8px;font-size:11px">
                    <i data-lucide="info"></i>
                    <div>
                        <strong>Pasos siguientes:</strong><br>
                        1. Ir a <a href="https://auth.afip.gob.ar/" target="_blank">auth.afip.gob.ar</a><br>
                        2. Administración de Certificados Digitales<br>
                        3. Crear alias y pegar el contenido del CSR:<br>
                        <textarea readonly style="width:100%;height:80px;font-size:10px;font-family:monospace;margin-top:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;padding:4px;color:var(--text-main)">${data.csr_content}</textarea>
                        4. Asociar al Web Service <strong>wsfe</strong><br>
                        5. Descargar el <strong>.crt</strong> y configurarlo arriba
                    </div>
                </div>`;
            if (typeof lucide !== 'undefined') lucide.createIcons();
            App.toast('Certificado generado — configure el .crt de AFIP', 'success');
        } catch (err) {
            result.classList.remove('hidden');
            result.innerHTML = `<div class="test-result error">${err.message}</div>`;
            App.toast(err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="shield-plus"></i> Generar Certificado AFIP';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    },

    _updateLicenseBar(license) {
        const bar = document.getElementById('license-status-bar');
        if (!bar) return;

        if (license && license.plan === 'completa' && license.active) {
            bar.className = 'license-bar license-valid';
            const until = license.valid_until ? ` — vence ${license.valid_until}` : '';
            const cache = license.from_cache ? ' <span style="font-size:11px;opacity:.7">(sin conexión)</span>' : '';
            bar.innerHTML = `<i data-lucide="check-circle"></i> Plan Completo activo${until}${cache}`;
        } else if (license && license.plan === 'completa' && !license.active) {
            bar.className = 'license-bar license-invalid';
            bar.innerHTML = '<i data-lucide="alert-triangle"></i> Plan Completo vencido — <a href="https://goxtech.com.ar" target="_blank">Renovar</a>';
        } else {
            bar.className = 'license-bar license-trial';
            const msg = (license && license.message) ? license.message : 'Plan Básico activo';
            bar.innerHTML = `<i data-lucide="info"></i> ${msg}`;
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    async refreshLicense() {
        const btn = document.getElementById('btn-refresh-license');
        if (btn) { btn.disabled = true; btn.innerHTML = '<i data-lucide="loader-2" class="spin-icon"></i> Verificando...'; }
        if (typeof lucide !== 'undefined') lucide.createIcons();
        try {
            const result = await API.post('/api/config/license/refresh');
            this._updateLicenseBar(result);
            App._checkLicense();
            App.toast(result.message, result.plan === 'completa' ? 'success' : 'info');
        } catch (err) {
            App.toast('Error al verificar plan: ' + err.message, 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = '<i data-lucide="refresh-cw"></i> Verificar plan'; }
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    },
};
