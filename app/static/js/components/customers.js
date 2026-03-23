/**
 * Customers Component — Lista de clientes con datos fiscales y actualización desde padrón ARCA.
 */
const CustomersComponent = {
    _allCustomers: [],
    _search: '',

    init() {
        document.getElementById('customer-search')
            .addEventListener('input', App.debounce(() => this.load(), 400));
    },

    async load() {
        const search = document.getElementById('customer-search').value.trim();
        const tbody = document.getElementById('customers-tbody');
        const count = document.getElementById('customers-count');

        try {
            const customers = await API.get(`/api/factusol/customers?search=${encodeURIComponent(search)}`);
            this._allCustomers = customers;
            count.textContent = `${customers.length} clientes`;

            if (customers.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted)">No se encontraron clientes</td></tr>';
                return;
            }

            tbody.innerHTML = customers.map(c => {
                const cfeName = this._cfecliLabel(c.CFECLI);
                const cfeClass = this._cfecliClass(c.CFECLI);
                const cuit = c.NIFCLI || '-';
                return `<tr>
                    <td><strong>${c.CODCLI}</strong></td>
                    <td>${c.NOFCLI || ''}</td>
                    <td>${cuit}</td>
                    <td><span class="badge ${cfeClass}">${cfeName}</span></td>
                    <td>${c.POBCLI || ''}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="CustomersComponent.showDetail(${c.CODCLI})" title="Ver detalle">
                            <i data-lucide="eye"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="CustomersComponent.updateFromPadron(${c.CODCLI}, '${(cuit || '').replace(/'/g, '')}')" title="Actualizar desde Padrón ARCA">
                            <i data-lucide="refresh-cw"></i>
                        </button>
                    </td>
                </tr>`;
            }).join('');

            if (typeof lucide !== 'undefined') lucide.createIcons();
        } catch (err) {
            App.toast(err.message, 'error');
        }
    },

    _cfecliLabel(cfecli) {
        const map = { 0: 'No config', 1: 'Cons. Final', 2: 'Resp. Inscripto', 3: 'Monotributo', 4: 'Exento' };
        return map[cfecli] || `Tipo ${cfecli}`;
    },

    _cfecliClass(cfecli) {
        const map = { 0: 'badge-secondary', 1: 'badge-info', 2: 'badge-success', 3: 'badge-warning', 4: 'badge-danger' };
        return map[cfecli] || 'badge-secondary';
    },

    showDetail(codcli) {
        const c = this._allCustomers.find(x => x.CODCLI === codcli);
        if (!c) return;

        const modal = document.getElementById('customer-modal');
        document.getElementById('customer-modal-title').textContent = c.NOFCLI || `Cliente ${codcli}`;

        document.getElementById('customer-detail-body').innerHTML = `
            <div class="customer-detail-grid">
                <div class="customer-field"><label>Código</label><span>${c.CODCLI}</span></div>
                <div class="customer-field"><label>Razón Social</label><span>${c.NOFCLI || '-'}</span></div>
                <div class="customer-field"><label>CUIT/DNI</label><span>${c.NIFCLI || '-'}</span></div>
                <div class="customer-field"><label>Cond. Fiscal</label><span class="badge ${this._cfecliClass(c.CFECLI)}">${this._cfecliLabel(c.CFECLI)}</span></div>
                <div class="customer-field"><label>Domicilio</label><span>${c.DOMCLI || '-'}</span></div>
                <div class="customer-field"><label>Localidad</label><span>${c.POBCLI || '-'}</span></div>
                <div class="customer-field"><label>CP</label><span>${c.CPOCLI || '-'}</span></div>
                <div class="customer-field"><label>Provincia</label><span>${c.PROCLI || '-'}</span></div>
                <div class="customer-field"><label>Teléfono</label><span>${c.TELCLI || '-'}</span></div>
                <div class="customer-field"><label>Email</label><span>${c.EMACLI || '-'}</span></div>
            </div>
            <div style="margin-top:12px;text-align:right">
                <button class="btn btn-primary" onclick="CustomersComponent.updateFromPadron(${c.CODCLI}, '${(c.NIFCLI || '').replace(/'/g, '')}')">
                    <i data-lucide="refresh-cw"></i> Actualizar desde Padrón ARCA
                </button>
            </div>
        `;

        modal.classList.remove('hidden');
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    closeModal() {
        document.getElementById('customer-modal').classList.add('hidden');
    },

    async updateFromPadron(codcli, cuit) {
        if (!cuit || cuit.length < 10) {
            App.toast('El cliente no tiene CUIT válido', 'error');
            return;
        }

        App.toast('Consultando padrón ARCA...', 'info');

        try {
            const padron = await API.get(`/api/arca/padron/${cuit.replace(/-/g, '')}`);

            // Mapear condición IVA del padrón a CFECLI
            let cfecli = 0;
            const condIva = (padron.condicion_iva || '').toLowerCase();
            if (condIva.includes('consumidor final')) cfecli = 1;
            else if (condIva.includes('responsable inscripto')) cfecli = 2;
            else if (condIva.includes('monotributo')) cfecli = 3;
            else if (condIva.includes('exento')) cfecli = 4;

            // Preparar datos para actualizar
            const updateData = {};
            if (padron.razon_social) updateData.NOFCLI = padron.razon_social;
            if (padron.domicilio_fiscal?.direccion) updateData.DOMCLI = padron.domicilio_fiscal.direccion;
            if (padron.domicilio_fiscal?.localidad) updateData.POBCLI = padron.domicilio_fiscal.localidad;
            if (padron.domicilio_fiscal?.cod_postal) updateData.CPOCLI = padron.domicilio_fiscal.cod_postal;
            if (padron.domicilio_fiscal?.provincia) updateData.PROCLI = padron.domicilio_fiscal.provincia;
            if (cfecli) updateData.CFECLI = cfecli;

            await API.put(`/api/factusol/customers/${codcli}/fiscal`, updateData);

            App.toast(`✅ Cliente actualizado desde padrón: ${padron.condicion_iva || 'OK'}`, 'success');
            this.closeModal();
            this.load();
        } catch (err) {
            App.toast(`Error padrón: ${err.message}`, 'error');
        }
    },
};
