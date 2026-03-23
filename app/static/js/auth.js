/**
 * Auth Module - Token management and session handling.
 */
const Auth = {
    user: null,

    init() {
        const token = localStorage.getItem('arca_token');
        const user = localStorage.getItem('arca_user');
        if (token && user) {
            API.token = token;
            this.user = JSON.parse(user);
            return true;
        }
        return false;
    },

    save(token, user) {
        API.token = token;
        this.user = user;
        localStorage.setItem('arca_token', token);
        localStorage.setItem('arca_user', JSON.stringify(user));
    },

    logout() {
        API.token = null;
        this.user = null;
        localStorage.removeItem('arca_token');
        localStorage.removeItem('arca_user');
        App.showLogin();
    },

    isAdmin() {
        return this.user && this.user.role === 'admin';
    },

    getPuntosVenta() {
        return this.user ? (this.user.puntos_venta || []) : [];
    },

    async refresh() {
        // Recarga el perfil completo (con puntos_venta actualizados) desde el servidor
        try {
            const me = await API.get('/api/auth/me');
            this.user = { ...this.user, ...me };
            localStorage.setItem('arca_user', JSON.stringify(this.user));
        } catch (err) {
            console.warn('Auth.refresh() falló:', err);
        }
    },
};
