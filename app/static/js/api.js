/**
 * API Client - Wrapper for all backend API calls.
 */
const API = {
    token: null,
    _skipLogoutUntil: 0,

    async request(url, options = {}) {
        const headers = { 'Content-Type': 'application/json', ...options.headers };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        const response = await fetch(url, { ...options, headers });
        if (response.status === 401) {
            // Don't auto-logout if we just logged in (grace period)
            if (Date.now() < this._skipLogoutUntil) {
                throw new Error('No autorizado');
            }
            Auth.logout();
            throw new Error('Sesion expirada');
        }
        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: 'Error desconocido' }));
            throw new Error(err.detail || `Error ${response.status}`);
        }
        return response.json();
    },

    get(url) { return this.request(url); },
    post(url, data) { return this.request(url, { method: 'POST', body: JSON.stringify(data) }); },
    put(url, data) { return this.request(url, { method: 'PUT', body: JSON.stringify(data) }); },
    delete(url) { return this.request(url, { method: 'DELETE' }); },

    // Special: login uses form-urlencoded
    async login(username, password) {
        const body = new URLSearchParams({ username, password });
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body,
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: 'Error de login' }));
            throw new Error(err.detail);
        }
        const data = await response.json();
        // Grace period: don't auto-logout on 401 for 5 seconds after login
        this._skipLogoutUntil = Date.now() + 5000;
        return data;
    },
};
