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
                    facturar_mono_como_a: document.getElementById('cfg-mono-como-a').checked,
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
                    serie_nc: document.getElementById('cfg-serie-nc').value,
                });
                App.toast('Configuración de Factusol guardada', 'success');
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

        document.getElementById('config-iva-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await API.put('/api/config/iva-mapping', {
                    tipo_1: document.getElementById('cfg-iva-tipo-1').value,
                    tipo_2: document.getElementById('cfg-iva-tipo-2').value,
                    tipo_3: document.getElementById('cfg-iva-tipo-3').value,
                    tipo_4: document.getElementById('cfg-iva-tipo-4').value,
                });
                App.toast('Mapeo de IVA guardado', 'success');
            } catch (err) { App.toast(err.message, 'error'); }
        });
    },

    async inferIvaMapping() {
        const btn = document.getElementById('btn-infer-iva');
        const result = document.getElementById('iva-infer-result');
        btn.disabled = true;
        btn.innerHTML = '<i data-lucide="loader-2" class="spin-icon"></i> Analizando...';
        if (typeof lucide !== 'undefined') lucide.createIcons();
        try {
            const data = await API.post('/api/config/iva-mapping/infer');
            const mapping = data.mapping || {};
            const stats = data.stats || {};

            // Solo rellenar slots que tienen mapping (no null). Los null se dejan como esta.
            const detected = [];
            const skipped = [];
            for (let i = 1; i <= 4; i++) {
                const key = `tipo_${i}`;
                const val = mapping[key];
                if (val !== null && val !== undefined) {
                    document.getElementById(`cfg-iva-tipo-${i}`).value = val;
                    detected.push(`Tipo ${i}: ${val === 'exento' ? 'Exento' : val + '%'}`);
                } else {
                    skipped.push(`Tipo ${i}`);
                }
            }

            // Mostrar resultado
            result.classList.remove('hidden', 'success', 'error');
            result.className = 'test-result success';
            const stMsg = stats.facturas_analizadas
                ? `${stats.facturas_analizadas} facturas analizadas (series fiscales: ${(stats.series_fiscales || []).join(', ') || '—'})`
                : (stats.mensaje || '');
            let html = `<strong>Detectado:</strong> ${detected.join(' · ') || '(nada)'}<br><span style="font-size:11px">${stMsg}</span>`;
            if (skipped.length) {
                html += `<br><span style="font-size:11px;color:var(--text-muted)">Sin datos suficientes: ${skipped.join(', ')} (se mantuvo el valor actual)</span>`;
            }
            html += '<br><span style="font-size:11px">Revisá y presioná <strong>Guardar</strong> para confirmar.</span>';
            result.innerHTML = html;
        } catch (err) {
            result.classList.remove('hidden', 'success');
            result.className = 'test-result error';
            result.textContent = err.message;
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="wand-2"></i> Detectar desde Factusol';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }

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
            document.getElementById('cfg-mono-como-a').checked = config.empresa?.facturar_mono_como_a !== false;

            // Factusol
            document.getElementById('cfg-db-path').value = config.factusol?.db_path || '';
            document.getElementById('cfg-serie-nc').value = config.factusol?.serie_nc || '9';

            // ARCA
            document.getElementById('cfg-environment').value = config.arca?.environment || 'development';
            document.getElementById('cfg-cert-path').value = config.arca?.cert_path || '';
            document.getElementById('cfg-key-path').value = config.arca?.key_path || '';

            // Tipos de IVA (Factusol → AFIP)
            const ivaMap = config.iva_mapping || {};
            document.getElementById('cfg-iva-tipo-1').value = ivaMap.tipo_1 || '21';
            document.getElementById('cfg-iva-tipo-2').value = ivaMap.tipo_2 || '10.5';
            document.getElementById('cfg-iva-tipo-3').value = ivaMap.tipo_3 || '27';
            document.getElementById('cfg-iva-tipo-4').value = ivaMap.tipo_4 || 'exento';

            // Plan / Licencia
            this._updateLicenseBar(config.license);

            // Puntos de Venta
            this.loadPVs();
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
            // Desde v1.5.0 el plan pago se diferencia por incluir soporte WhatsApp.
            const etiqueta = (license.sub_plan === 'vitalicia') ? 'Vitalicia (con soporte WhatsApp)' : 'Mensual (con soporte WhatsApp)';
            bar.innerHTML = `<i data-lucide="check-circle"></i> ${etiqueta}${until}${cache}`;
        } else if (license && license.plan === 'completa' && !license.active) {
            bar.className = 'license-bar license-invalid';
            bar.innerHTML = '<i data-lucide="alert-triangle"></i> Plan pago vencido — <a href="https://goxtech.com.ar" target="_blank">Renovar</a>';
        } else {
            bar.className = 'license-bar license-trial';
            bar.innerHTML = '<i data-lucide="info"></i> Básica (sin soporte)';
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    // ── Punto de Venta ─────────────────────────────────────────────────
    _editingPvId: null,

    async loadPVs() {
        try {
            const pvs = await API.get('/api/config/my-puntos-venta');
            const container = document.getElementById('config-pv-list');
            if (!pvs.length) {
                container.innerHTML = '<p style="color:var(--text-muted);font-size:13px">No tiene puntos de venta configurados. Agregue uno para poder facturar.</p>';
                document.getElementById('btn-add-pv-config').classList.remove('hidden');
                return;
            }
            const tipoMap = {0: 'Auto', 1: 'Factura A', 6: 'Factura B', 11: 'Factura C'};
            container.innerHTML = pvs.map(pv => `
                <div class="pv-config-row" style="display:flex;align-items:center;gap:10px;padding:8px;border:1px solid var(--border);border-radius:6px;margin-bottom:6px">
                    <div style="flex:1">
                        <strong>${pv.nombre}</strong>
                        <span style="font-size:12px;color:var(--text-muted)">
                            — PV ${pv.punto_venta} | Serie ${pv.serie_factusol} | ${tipoMap[pv.tipo_comprobante] || 'Tipo ' + pv.tipo_comprobante}
                        </span>
                    </div>
                    <button class="btn btn-sm btn-secondary" onclick="ConfigComponent.editPV(${pv.id}, '${pv.nombre}', ${pv.punto_venta}, ${pv.serie_factusol}, ${pv.tipo_comprobante})">
                        <i data-lucide="pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="ConfigComponent.deletePV(${pv.id})">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            `).join('');

            // En plan básico con 1 PV, ocultar botón agregar
            const hasCompleta = App._hasCompleta;
            const addBtn = document.getElementById('btn-add-pv-config');
            if (!hasCompleta && pvs.length >= 1) {
                addBtn.classList.add('hidden');
            } else {
                addBtn.classList.remove('hidden');
            }

            if (typeof lucide !== 'undefined') lucide.createIcons();
        } catch (err) {
            console.error('Error loading PVs:', err);
        }
    },

    showAddPV() {
        this._editingPvId = null;
        document.getElementById('cfg-pv-nombre').value = '';
        document.getElementById('cfg-pv-numero').value = '';
        document.getElementById('cfg-pv-serie').value = '1';
        document.getElementById('cfg-pv-tipo').value = '0';
        document.getElementById('config-pv-form').classList.remove('hidden');
        document.getElementById('btn-add-pv-config').classList.add('hidden');
    },

    editPV(id, nombre, pv, serie, tipo) {
        this._editingPvId = id;
        document.getElementById('cfg-pv-nombre').value = nombre;
        document.getElementById('cfg-pv-numero').value = pv;
        document.getElementById('cfg-pv-serie').value = serie;
        document.getElementById('cfg-pv-tipo').value = tipo;
        document.getElementById('config-pv-form').classList.remove('hidden');
        document.getElementById('btn-add-pv-config').classList.add('hidden');
    },

    cancelPV() {
        this._editingPvId = null;
        document.getElementById('config-pv-form').classList.add('hidden');
        document.getElementById('btn-add-pv-config').classList.remove('hidden');
    },

    async savePV() {
        const data = {
            nombre: document.getElementById('cfg-pv-nombre').value.trim(),
            punto_venta: parseInt(document.getElementById('cfg-pv-numero').value) || 0,
            serie_factusol: parseInt(document.getElementById('cfg-pv-serie').value) || 1,
            tipo_comprobante: parseInt(document.getElementById('cfg-pv-tipo').value) || 0,
        };
        if (!data.nombre || !data.punto_venta) {
            App.toast('Complete el nombre y el numero de PV', 'error');
            return;
        }
        try {
            if (this._editingPvId) {
                await API.put(`/api/config/my-puntos-venta/${this._editingPvId}`, data);
                App.toast('Punto de venta actualizado', 'success');
            } else {
                await API.post('/api/config/my-puntos-venta', data);
                App.toast('Punto de venta agregado', 'success');
            }
            this.cancelPV();
            this.loadPVs();
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    async deletePV(pvId) {
        if (!confirm('Eliminar este punto de venta?')) return;
        try {
            await API.delete(`/api/config/my-puntos-venta/${pvId}`);
            App.toast('Punto de venta eliminado', 'success');
            this.loadPVs();
        } catch (err) {
            App.toast(err.message, 'error');
        }
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

    // ── Actualizaciones ───────────────────────────────────────────────
    _latestUpdate: null,

    async checkUpdate() {
        const btn = document.getElementById('btn-check-update');
        const status = document.getElementById('update-status');
        const applyBtn = document.getElementById('btn-apply-update');
        const changelogDiv = document.getElementById('update-changelog');

        btn.disabled = true;
        btn.innerHTML = '<i data-lucide="loader"></i> Verificando...';
        if (typeof lucide !== 'undefined') lucide.createIcons();

        try {
            const data = await API.get('/api/updates/check');
            this._latestUpdate = data;

            if (data.has_update) {
                status.innerHTML = `
                    <div style="padding:8px 12px;background:var(--primary-light, #e8f5e9);border-radius:6px;border-left:4px solid var(--primary)">
                        <strong>Nueva version disponible: v${data.latest_version}</strong>
                        <span style="color:var(--text-muted);margin-left:8px">(${data.date})</span>
                        <br><span style="font-size:13px">Version actual: v${data.current_version}</span>
                    </div>`;
                applyBtn.classList.remove('hidden');
                if (data.changelog) {
                    changelogDiv.classList.remove('hidden');
                    changelogDiv.innerHTML = `<strong>Cambios:</strong><br>${data.changelog}`;
                }
                App.toast(`Nueva version disponible: v${data.latest_version}`, 'info');
            } else {
                status.innerHTML = `
                    <div style="padding:8px 12px;background:var(--bg-tertiary);border-radius:6px">
                        <i data-lucide="check-circle" style="width:16px;height:16px;vertical-align:middle;color:var(--success)"></i>
                        <strong>Estas al dia</strong> — Version actual: v${data.current_version}
                    </div>`;
                applyBtn.classList.add('hidden');
                changelogDiv.classList.add('hidden');
                App.toast('Ya tenes la ultima version', 'success');
            }
        } catch (err) {
            status.innerHTML = `<span style="color:var(--danger)">Error al verificar: ${err.message}</span>`;
            App.toast('No se pudo verificar actualizaciones: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="search"></i> Verificar ultima version';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    },

    async applyUpdate() {
        if (!this._latestUpdate?.has_update) {
            App.toast('No hay actualizaciones disponibles', 'warning');
            return;
        }

        if (!confirm(
            `Actualizar ARCA a v${this._latestUpdate.latest_version}?\n\n` +
            `La aplicacion se cerrara, se actualizara automaticamente y se reiniciara.\n` +
            `Su configuracion, base de datos y certificados se preservaran.\n\n` +
            `Continuar?`
        )) return;

        const btn = document.getElementById('btn-apply-update');
        const status = document.getElementById('update-status');
        btn.disabled = true;
        btn.innerHTML = '<i data-lucide="loader"></i> Descargando...';
        if (typeof lucide !== 'undefined') lucide.createIcons();

        status.innerHTML = `
            <div style="padding:12px;background:var(--bg-tertiary);border-radius:6px;text-align:center">
                <div style="font-size:16px;margin-bottom:8px"><strong>Descargando actualizacion...</strong></div>
                <div style="font-size:13px;color:var(--text-muted)">No cierre la aplicacion. Se reiniciara automaticamente.</div>
            </div>`;

        try {
            const result = await API.post('/api/updates/apply');

            if (result.status === 'updating') {
                status.innerHTML = `
                    <div style="padding:12px;background:var(--primary-light, #e8f5e9);border-radius:6px;text-align:center">
                        <div style="font-size:16px;margin-bottom:8px"><strong>Actualizacion descargada</strong></div>
                        <div style="font-size:13px">La aplicacion se cerrara y reiniciara en unos segundos...</div>
                    </div>`;
                App.toast('Actualizacion en progreso. Reiniciando...', 'success');
            } else if (result.status === 'up_to_date') {
                status.innerHTML = `<span style="color:var(--success)">Ya estas en la version mas reciente.</span>`;
                btn.classList.add('hidden');
                App.toast(result.message, 'info');
            }
        } catch (err) {
            status.innerHTML = `<span style="color:var(--danger)">Error al actualizar: ${err.message}</span>`;
            App.toast('Error al actualizar: ' + err.message, 'error');
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="download"></i> Actualizar ahora';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    },
};
