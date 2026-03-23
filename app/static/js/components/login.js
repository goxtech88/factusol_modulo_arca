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
    },

    async handleLogin() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const errorEl = document.getElementById('login-error');

        if (!username || !password) {
            errorEl.textContent = 'Complete usuario y contraseña';
            errorEl.classList.remove('hidden');
            return;
        }

        errorEl.classList.add('hidden');
        document.getElementById('btn-login').disabled = true;

        try {
            const data = await API.login(username, password);
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
