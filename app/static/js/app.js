/**
 * Main App Controller
 */
const App = {
    currentPage: 'dashboard',

    init() {
        // Check existing session
        if (Auth.init()) {
            this.showApp();
        } else {
            this.showLogin();
        }

        // Init Lucide icons
        if (typeof lucide !== 'undefined') lucide.createIcons();

        // Init components
        LoginComponent.init();
        InvoicesComponent.init();
        AdminComponent.init();
        ConfigComponent.init();
        if (typeof CreditNotesComponent !== 'undefined') CreditNotesComponent.init();

        // Floating Support Button (WhatsApp)
        const fab = document.getElementById('support-fab');
        if (fab) {
            fab.addEventListener('click', () => this._openWhatsAppSupport());
        }

        // Sidebar navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                this.navigate(page);
            });
        });

        // Logout
        document.getElementById('btn-logout').addEventListener('click', () => Auth.logout());

        // Toggle sidebar (mobile)
        document.getElementById('btn-toggle-sidebar').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
        });
    },

    showLogin() {
        document.getElementById('page-login').classList.add('active');
        document.getElementById('page-login').classList.remove('hidden');
        document.getElementById('page-app').classList.add('hidden');
        document.getElementById('page-app').classList.remove('active');
        document.getElementById('login-error').classList.add('hidden');
        // Populate user dropdown and restore saved credentials
        LoginComponent.loadUsers();
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    showApp() {
        document.getElementById('page-login').classList.add('hidden');
        document.getElementById('page-login').classList.remove('active');
        document.getElementById('page-app').classList.add('active');
        document.getElementById('page-app').classList.remove('hidden');

        // Update UI
        document.getElementById('sidebar-username').textContent = Auth.user.full_name || Auth.user.username;

        // Show/hide admin items
        const isAdmin = Auth.isAdmin();
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = isAdmin ? '' : 'none';
        });

        this.loadEmpresaName();
        this._checkLicense();
        this.navigate('dashboard');
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    async _checkLicense() {
        try {
            const config = await API.get('/api/config');
            const lic = config.license || {};
            this._plan = lic.plan || 'basica';
            // Desde v1.5.0: el plan basico tiene todas las funciones; los planes
            // pagos se diferencian unicamente por incluir soporte por WhatsApp.
            this._hasCompleta = (lic.plan === 'completa' && lic.active);
            this._hasSupport = this._hasCompleta;

            // Quitar banner de trial si existia de version anterior
            const banner = document.getElementById('trial-banner');
            if (banner) banner.remove();

            // Actualizar visibilidad del boton flotante de soporte
            this._updateSupportFab();
        } catch {
            this._plan = 'basica';
            this._hasCompleta = false;
            this._hasSupport = false;
            this._updateSupportFab();
        }
    },

    _updateSupportFab() {
        const fab = document.getElementById('support-fab');
        if (!fab) return;
        fab.style.display = this._hasSupport ? '' : 'none';
    },

    async _openWhatsAppSupport() {
        try {
            // TODO: Replace with GoxTech real number
            const phone = '5491112345678';
            let empresa = {};
            try {
                const cfg = await API.get('/api/config');
                empresa = cfg.empresa || {};
            } catch { /* ignore */ }
            const nombre = (Auth.user && (Auth.user.full_name || Auth.user.username)) || 'Usuario';
            const razon = empresa.razon_social || 'Empresa';
            const cuit = empresa.cuit || 'sin CUIT';
            const msg = `Hola, soy ${nombre} de ${razon} (CUIT ${cuit}). Tengo una consulta sobre ARCA Sync v1.5.0...`;
            const url = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;
            window.open(url, '_blank', 'noopener');
        } catch (e) {
            App.toast('No se pudo abrir WhatsApp', 'error');
        }
    },

    navigate(page) {
        this.currentPage = page;

        // Update sidebar
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const navItem = document.querySelector(`.nav-item[data-page="${page}"]`);
        if (navItem) navItem.classList.add('active');

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            invoices: 'Facturas',
            'credit-notes': 'Notas de Crédito',
            purchases: 'Compras',
            'cae-logs': 'CAE Emitidos',
            users: 'Usuarios',
            config: 'Configuración',
        };
        document.getElementById('page-title').textContent = titles[page] || 'Dashboard';

        // Show section
        document.querySelectorAll('.section').forEach(el => {
            el.classList.add('hidden');
            el.classList.remove('active');
        });
        const section = document.getElementById(`section-${page}`);
        if (section) {
            section.classList.remove('hidden');
            section.classList.add('active');
        }

        // Load data
        switch (page) {
            case 'dashboard':
                DashboardComponent.load();
                break;
            case 'invoices':
                InvoicesComponent.loadPuntosVenta();
                break;
            case 'credit-notes':
                if (typeof CreditNotesComponent !== 'undefined') CreditNotesComponent.load();
                break;
            case 'purchases':
                // Placeholder, sin carga de datos
                break;
            case 'cae-logs':
                CAELogsComponent.load();
                break;
            case 'users':
                AdminComponent.load();
                break;
            case 'config':
                ConfigComponent.load();
                break;
        }

        // Close sidebar on mobile
        document.getElementById('sidebar').classList.remove('open');

        // Render Lucide icons for new content
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    async loadEmpresaName() {
        try {
            if (Auth.isAdmin()) {
                const config = await API.get('/api/config');
                const nombre = config.empresa?.razon_social;
                document.getElementById('top-bar-empresa').textContent = nombre || 'Sin configurar';
            }
        } catch {}
    },

    toast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const iconMap = {
            success: 'check-circle',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info',
        };
        const iconName = iconMap[type] || 'info';

        // Duracion segun tipo y largo del mensaje (mensajes largos quedan mas tiempo)
        const baseDuration = { error: 8000, warning: 6000, success: 4000, info: 4000 };
        const extraPerChar = String(message).length > 100 ? Math.min(8000, String(message).length * 30) : 0;
        const duration = (baseDuration[type] || 4000) + extraPerChar;

        // Escape HTML y preservar saltos de linea con pre-wrap (mensajes multilinea)
        const escapeHtml = (s) => String(s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

        toast.innerHTML = `
            <i data-lucide="${iconName}"></i>
            <span class="toast-msg" style="white-space:pre-wrap; word-break:break-word">${escapeHtml(message)}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        container.appendChild(toast);
        if (typeof lucide !== 'undefined') lucide.createIcons();

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },


    debounce(fn, ms) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), ms);
        };
    },
};

// Boot
document.addEventListener('DOMContentLoaded', () => App.init());
