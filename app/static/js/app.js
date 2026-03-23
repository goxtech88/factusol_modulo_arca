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
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
        document.getElementById('login-error').classList.add('hidden');
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
        this.navigate('dashboard');
        if (typeof lucide !== 'undefined') lucide.createIcons();
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
            customers: 'Clientes',
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
            case 'customers':
                CustomersComponent.load();
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

        // Duracion segun tipo
        const durationMap = { error: 8000, warning: 6000, success: 4000, info: 4000 };
        const duration = durationMap[type] || 4000;

        toast.innerHTML = `
            <i data-lucide="${iconName}"></i>
            <span class="toast-msg">${message}</span>
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
