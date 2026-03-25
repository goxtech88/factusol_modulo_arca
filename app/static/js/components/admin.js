/**
 * Admin Component - User management.
 */
const AdminComponent = {
    editingUserId: null,

    init() {
        document.getElementById('btn-new-user').addEventListener('click', () => this.showUserModal());
        document.getElementById('btn-save-user').addEventListener('click', () => this.saveUser());
        document.getElementById('btn-add-pv').addEventListener('click', () => this.addPvField());

        document.querySelectorAll('#user-modal .modal-close, #user-modal .modal-overlay').forEach(el => {
            el.addEventListener('click', () => this.closeModal());
        });
    },

    async load() {
        try {
            const users = await API.get('/api/users');
            const list = document.getElementById('users-list');

            list.innerHTML = users.map(u => `
                <div class="user-item">
                    <div class="user-item-info">
                        <i data-lucide="user-circle"></i>
                        <div class="user-item-details">
                            <h4>${u.full_name} ${!u.is_active ? '<span class="badge badge-danger">Inactivo</span>' : ''}
                                ${u.auto_validate_enabled ? '<span class="badge badge-success-subtle" title="Auto-validación activa"><i data-lucide="bot" style="width:12px;height:12px"></i> Auto</span>' : '<span class="badge badge-muted" title="Auto-validación desactivada"><i data-lucide="bot-off" style="width:12px;height:12px"></i></span>'}
                            </h4>
                            <p>@${u.username} · ${u.role === 'admin' ? 'Admin' : 'Usuario'} · ${u.puntos_venta.length} PdV</p>
                        </div>
                    </div>
                    <div class="user-item-actions">
                        <button class="btn btn-sm btn-secondary" onclick="AdminComponent.editUser(${u.id})">
                            <i data-lucide="pencil"></i>
                        </button>
                        ${u.is_active ? `<button class="btn btn-sm btn-danger" onclick="AdminComponent.deactivateUser(${u.id}, '${u.username}')">
                            <i data-lucide="ban"></i>
                        </button>` : ''}
                    </div>
                </div>
            `).join('');
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    showUserModal(user = null) {
        this.editingUserId = user ? user.id : null;
        document.getElementById('user-modal-title').textContent = user ? 'Editar Usuario' : 'Nuevo Usuario';
        document.getElementById('user-username').value = user ? user.username : '';
        document.getElementById('user-username').disabled = !!user;
        document.getElementById('user-fullname').value = user ? user.full_name : '';
        document.getElementById('user-password').value = '';
        document.getElementById('user-role').value = user ? user.role : 'user';

        // Auto-validación toggle
        const autoValEnabled = user ? (user.auto_validate_enabled !== false) : true;
        const autoValCheckbox = document.getElementById('user-auto-validate');
        autoValCheckbox.checked = autoValEnabled;
        this._updateAutoValidateLabel(autoValEnabled);
        autoValCheckbox.onchange = () => this._updateAutoValidateLabel(autoValCheckbox.checked);

        const hint = document.getElementById('user-password-hint');
        hint.classList.toggle('hidden', !user);

        // Puntos de venta
        const pvList = document.getElementById('user-puntos-venta-list');
        pvList.innerHTML = '';
        if (user && user.puntos_venta) {
            user.puntos_venta.forEach(pv => this.addPvField(pv));
        }

        document.getElementById('user-modal').classList.remove('hidden');
    },

    _updateAutoValidateLabel(enabled) {
        const label = document.getElementById('user-auto-validate-label');
        if (label) {
            label.textContent = enabled ? 'Activado' : 'Desactivado';
            label.className = `toggle-label ${enabled ? 'text-success' : 'text-muted'}`;
        }
    },

    closeModal() {
        document.getElementById('user-modal').classList.add('hidden');
    },

    addPvField(pv = null) {
        const container = document.getElementById('user-puntos-venta-list');
        const div = document.createElement('div');
        div.className = 'pv-form-item';
        div.innerHTML = `
            <button type="button" class="btn-remove-pv" onclick="this.parentElement.remove()">
                <i data-lucide="x"></i>
            </button>
            <div class="form-group">
                <label>Nombre (Sucursal)</label>
                <input type="text" class="pv-nombre" value="${pv ? pv.nombre : ''}" placeholder="Ej: Sucursal Centro">
            </div>
            <div class="pv-form-grid">
                <div class="form-group">
                    <label>Punto de Venta ARCA</label>
                    <input type="number" class="pv-punto-venta" value="${pv ? pv.punto_venta : ''}" min="1" placeholder="1">
                </div>
                <div class="form-group">
                    <label>Serie Factusol (TIPFAC)</label>
                    <input type="number" class="pv-serie" value="${pv ? pv.serie_factusol : ''}" min="1" max="9" placeholder="1">
                </div>
                <div class="form-group">
                    <label>Tipo Comprobante</label>
                    <select class="pv-tipo-cbte">
                        <option value="0" ${!pv || pv.tipo_comprobante == 0 ? 'selected' : ''}>Auto (segun IVA)</option>
                        <option value="1" ${pv && pv.tipo_comprobante == 1 ? 'selected' : ''}>Factura A</option>
                        <option value="6" ${pv && pv.tipo_comprobante == 6 ? 'selected' : ''}>Factura B</option>
                        <option value="11" ${pv && pv.tipo_comprobante == 11 ? 'selected' : ''}>Factura C</option>
                    </select>
                </div>
            </div>
            ${pv && pv.id ? `<input type="hidden" class="pv-id" value="${pv.id}">` : ''}
        `;
        container.appendChild(div);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    async saveUser() {
        const username = document.getElementById('user-username').value.trim();
        const fullName = document.getElementById('user-fullname').value.trim();
        const password = document.getElementById('user-password').value;
        const role = document.getElementById('user-role').value;

        if (!username || !fullName) {
            App.toast('Complete usuario y nombre', 'error');
            return;
        }

        if (!this.editingUserId && !password) {
            App.toast('La contraseña es obligatoria para nuevos usuarios', 'error');
            return;
        }

        try {
            if (this.editingUserId) {
                // Update user
                const updateData = { full_name: fullName, role, auto_validate_enabled: document.getElementById('user-auto-validate').checked };
                if (password) updateData.password = password;
                await API.put(`/api/users/${this.editingUserId}`, updateData);

                // Get current PVs
                const users = await API.get('/api/users');
                const currentUser = users.find(u => u.id === this.editingUserId);
                const existingPvIds = currentUser ? currentUser.puntos_venta.map(pv => pv.id) : [];

                // Sync PVs
                const pvItems = document.querySelectorAll('#user-puntos-venta-list .pv-form-item');
                const newPvIds = [];

                for (const item of pvItems) {
                    const pvId = item.querySelector('.pv-id');
                    const pvData = {
                        nombre: item.querySelector('.pv-nombre').value,
                        punto_venta: parseInt(item.querySelector('.pv-punto-venta').value),
                        serie_factusol: parseInt(item.querySelector('.pv-serie').value),
                        tipo_comprobante: parseInt(item.querySelector('.pv-tipo-cbte').value) || 0,
                    };

                    if (pvId) {
                        newPvIds.push(parseInt(pvId.value));
                        await API.put(`/api/users/${this.editingUserId}/puntos-venta/${pvId.value}`, pvData);
                    } else {
                        await API.post(`/api/users/${this.editingUserId}/puntos-venta`, pvData);
                    }
                }

                // Remove deleted PVs
                for (const id of existingPvIds) {
                    if (!newPvIds.includes(id)) {
                        await API.delete(`/api/users/${this.editingUserId}/puntos-venta/${id}`);
                    }
                }

                App.toast('Usuario actualizado', 'success');
            } else {
                // Create user
                const result = await API.post('/api/users', { username, password, full_name: fullName, role });
                const userId = result.id;

                // Add PVs
                const pvItems = document.querySelectorAll('#user-puntos-venta-list .pv-form-item');
                for (const item of pvItems) {
                    await API.post(`/api/users/${userId}/puntos-venta`, {
                        nombre: item.querySelector('.pv-nombre').value,
                        punto_venta: parseInt(item.querySelector('.pv-punto-venta').value),
                        serie_factusol: parseInt(item.querySelector('.pv-serie').value),
                        tipo_comprobante: parseInt(item.querySelector('.pv-tipo-cbte').value) || 0,
                    });
                }

                App.toast('Usuario creado', 'success');
            }

            this.closeModal();
            this.load();

            // Refrescar perfil del usuario logueado para actualizar puntos_venta en memoria
            await Auth.refresh();

            // Si el usuario editado es el usuario actual, recargar dashboard y facturas
            const currentUserId = Auth.user?.id;
            if (this.editingUserId === currentUserId || !this.editingUserId) {
                // Recargar dashboard
                if (typeof DashboardComponent !== 'undefined') DashboardComponent.load();
                // Recargar selector de puntos de venta en facturas
                if (typeof InvoicesComponent !== 'undefined') InvoicesComponent.loadPuntosVenta();
            }
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    async editUser(userId) {
        try {
            const users = await API.get('/api/users');
            const user = users.find(u => u.id === userId);
            if (user) this.showUserModal(user);
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    async deactivateUser(userId, username) {
        if (!confirm(`¿Desactivar usuario "${username}"?`)) return;
        try {
            await API.delete(`/api/users/${userId}`);
            App.toast('Usuario desactivado', 'success');
            this.load();
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },
};
