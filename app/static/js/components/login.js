/**
 * Login Component
 */
const LoginComponent = {
    init() {
        const form = document.getElementById('login-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        document.getElementById('btn-login').addEventListener('click', () => this.handleLogin());

        // Restore last used username and remembered password
        const saved = this._getSavedCredentials();
        if (saved) {
            document.getElementById('login-username').value = saved.username;
            document.getElementById('login-password').value = saved.password;
            document.getElementById('login-remember').checked = true;
            document.getElementById('btn-login').focus();
        } else {
            const lastUser = localStorage.getItem('arca_last_user');
            if (lastUser) document.getElementById('login-username').value = lastUser;
        }
    },

    // loadUsers kept as no-op for compatibility
    async loadUsers() {},

    _getSavedCredentials() {
        try {
            const data = localStorage.getItem('arca_remember');
            if (!data) return null;
            return JSON.parse(atob(data));
        } catch {
            return null;
        }
    },

    _saveCredentials(username, password, remember) {
        if (remember) {
            localStorage.setItem('arca_remember', btoa(JSON.stringify({ username, password })));
        } else {
            localStorage.removeItem('arca_remember');
        }
        localStorage.setItem('arca_last_user', username);
    },

    async handleLogin() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const remember = document.getElementById('login-remember').checked;
        const errorEl = document.getElementById('login-error');

        if (!username || !password) {
            errorEl.textContent = 'Ingrese usuario y contraseña';
            errorEl.classList.remove('hidden');
            return;
        }

        errorEl.classList.add('hidden');
        document.getElementById('btn-login').disabled = true;

        try {
            const data = await API.login(username, password);
            this._saveCredentials(username, password, remember);
            Auth.save(data.access_token, data.user);
            App.showApp();
        } catch (err) {
            errorEl.textContent = err.message;
            errorEl.classList.remove('hidden');
        } finally {
            document.getElementById('btn-login').disabled = false;
        }
    },
};
