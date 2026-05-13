/**
 * Wizard de Primer Uso - Registro de Licencia Gratis
 *
 * Cuando la app arranca y la empresa no esta registrada (no hay CUIT/email/razon
 * social en config), se muestra un modal bloqueante que captura los datos
 * basicos. Al submit se POSTea al backend de la app, que a su vez se comunica
 * con el backend remoto de licencias para crear License + Lead en CRM.
 */
const WizardComponent = {
    _isOpen: false,

    /**
     * Verifica si hace falta mostrar el wizard. Llamado por App.init() despues
     * de que el usuario esta logueado.
     */
    async checkAndShow() {
        try {
            const info = await API.get('/api/license/needs-registration');
            if (info && info.needs_registration) {
                this.show();
            }
        } catch (err) {
            console.warn('No pude verificar registro de licencia:', err);
            // No bloqueamos la app si falla el check — silencioso
        }
    },

    show() {
        const modal = document.getElementById('wizard-modal');
        if (!modal) return;
        this._isOpen = true;
        modal.classList.remove('hidden');
        modal.classList.add('active');
        // Refrescar iconos lucide
        if (typeof lucide !== 'undefined') lucide.createIcons();
        // Pre-cargar datos existentes (cuando se abre desde "Activar licencia")
        this._prefillFromConfig();
        // Focus en el primer campo
        setTimeout(() => {
            const first = document.getElementById('wz-company');
            if (first) first.focus();
        }, 150);
    },

    /**
     * Si la app ya tiene datos en config.empresa (por ejemplo cuando el cliente
     * abre el wizard desde "Activar licencia" en Config), los pre-completamos
     * para que solo tenga que confirmar / actualizar lo que falte.
     */
    async _prefillFromConfig() {
        try {
            const info = await API.get('/api/license/needs-registration');
            const cfg = await API.get('/api/config');
            const emp = (cfg && cfg.empresa) || {};
            const wzc = document.getElementById('wz-company');
            const wzu = document.getElementById('wz-cuit');
            const wzn = document.getElementById('wz-contact');
            const wze = document.getElementById('wz-email');
            const wzp = document.getElementById('wz-phone');
            const wzi = document.getElementById('wz-cond-iva');
            if (wzc && emp.razon_social && !wzc.value) wzc.value = emp.razon_social;
            if (wzu && emp.cuit && !wzu.value) wzu.value = emp.cuit;
            if (wzn && emp.contact_name && !wzn.value) wzn.value = emp.contact_name;
            if (wze && emp.email && !wze.value) wze.value = emp.email;
            if (wzp && emp.whatsapp && !wzp.value) wzp.value = emp.whatsapp;
            if (wzi && emp.condicion_iva) wzi.value = emp.condicion_iva;
        } catch (_) { /* ignore — primer uso, sin datos */ }
    },

    hide() {
        const modal = document.getElementById('wizard-modal');
        if (!modal) return;
        this._isOpen = false;
        modal.classList.add('hidden');
        modal.classList.remove('active');
    },

    /**
     * Valida CUIT: 11 digitos + digito verificador (mod 11).
     * Misma logica que el backend para que el usuario vea el error antes del submit.
     */
    _isValidCuit(cuit) {
        const c = (cuit || '').replace(/\D/g, '');
        if (c.length !== 11) return false;
        const mults = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
        let total = 0;
        for (let i = 0; i < 10; i++) total += parseInt(c[i], 10) * mults[i];
        let expected = 11 - (total % 11);
        if (expected === 11) expected = 0;
        else if (expected === 10) return false;
        return parseInt(c[10], 10) === expected;
    },

    async submit() {
        const company = document.getElementById('wz-company').value.trim();
        const cuit = document.getElementById('wz-cuit').value.trim();
        const condIva = document.getElementById('wz-cond-iva').value;
        const contact = document.getElementById('wz-contact').value.trim();
        const email = document.getElementById('wz-email').value.trim();
        const phone = document.getElementById('wz-phone').value.trim();

        // ── Validaciones cliente ──
        if (!company) {
            App.toast('Razon social es obligatoria', 'error');
            document.getElementById('wz-company').focus();
            return;
        }
        if (!this._isValidCuit(cuit)) {
            App.toast('CUIT invalido. Verifica que tenga 11 digitos y digito verificador correcto.', 'error');
            document.getElementById('wz-cuit').focus();
            return;
        }
        if (!contact) {
            App.toast('Nombre del responsable es obligatorio', 'error');
            document.getElementById('wz-contact').focus();
            return;
        }
        if (!email || !email.includes('@') || !email.split('@')[1]?.includes('.')) {
            App.toast('Email invalido', 'error');
            document.getElementById('wz-email').focus();
            return;
        }
        const phoneDigits = phone.replace(/\D/g, '');
        if (phoneDigits.length < 8) {
            App.toast('WhatsApp es obligatorio (minimo 8 digitos)', 'error');
            document.getElementById('wz-phone').focus();
            return;
        }

        // ── Submit ──
        const btn = document.getElementById('wz-submit');
        btn.disabled = true;
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="loader"></i> Activando...';

        try {
            const resp = await API.post('/api/license/register', {
                cuit,
                company_name: company,
                email,
                phone,
                contact_name: contact,
                condicion_iva: condIva,
            });
            App.toast(`✓ ${resp.message || 'Licencia activada'}`, 'success');
            this.hide();

            // Recargar config para reflejar los nuevos datos en pantalla
            try {
                if (typeof ConfigComponent !== 'undefined' && ConfigComponent.load) {
                    await ConfigComponent.load();
                }
            } catch (_) { /* ignore */ }

            // Recargar dashboard si esta visible
            try {
                if (App.currentPage === 'dashboard' && typeof DashboardComponent !== 'undefined') {
                    DashboardComponent.load();
                }
            } catch (_) { /* ignore */ }
        } catch (err) {
            App.toast(err.message || 'Error al registrar', 'error');
            btn.disabled = false;
            btn.innerHTML = originalHtml;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    },
};
