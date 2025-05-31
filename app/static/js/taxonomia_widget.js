// taxonomia_widget.js
// Widget de selección de producto

class TaxonomiaSelector {
    constructor(options = {}) {
        this.options = options;
        this.taxonomia = null;
        this.init();
    }

    async init() {
        const res = await fetch('/api/taxonomia/estructura');
        this.taxonomia = await res.json();
        this.categoriaSelector = document.getElementById('categoriaSelector');
        this.subcategoriaSelector = document.getElementById('subcategoriaSelector');
        this.productoSelector = document.getElementById('productoSelector');
        this.productTypeInput = document.getElementById('productType');
        this.productNameInput = document.getElementById('productName');
        this.customProductName = document.getElementById('customProductName');
        this.submitBtn = document.querySelector('.product-form button[type="submit"]');
        this.fillCategorias();
        this.addListeners();
        this.updateSubmitState();
    }

    fillCategorias() {
        this.categoriaSelector.innerHTML = '<option value="" disabled selected>Seleccione categoría...</option>';
        for (const categoria in this.taxonomia) {
            const opt = document.createElement('option');
            opt.value = categoria;
            opt.textContent = categoria;
            this.categoriaSelector.appendChild(opt);
        }
        this.subcategoriaSelector.innerHTML = '<option value="" disabled selected>Seleccione subcategoría...</option>';
        this.productoSelector.innerHTML = '<option value="" disabled selected>Seleccione producto...</option>';
        this.subcategoriaSelector.disabled = true;
        this.productoSelector.disabled = true;
    }

    addListeners() {
        this.categoriaSelector.addEventListener('change', () => {
            const categoria = this.categoriaSelector.value;
            this.productTypeInput.value = categoria;
            this.subcategoriaSelector.innerHTML = '<option value="" disabled selected>Seleccione subcategoría...</option>';
            this.productoSelector.innerHTML = '<option value="" disabled selected>Seleccione producto...</option>';
            this.productoSelector.disabled = true;
            if (categoria && this.taxonomia[categoria]) {
                for (const subcat in this.taxonomia[categoria]) {
                    const opt = document.createElement('option');
                    opt.value = subcat;
                    opt.textContent = subcat;
                    this.subcategoriaSelector.appendChild(opt);
                }
                this.subcategoriaSelector.disabled = false;
            } else {
                this.subcategoriaSelector.disabled = true;
            }
            this.updateSubmitState();
        });
        this.subcategoriaSelector.addEventListener('change', () => {
            const categoria = this.categoriaSelector.value;
            const subcat = this.subcategoriaSelector.value;
            this.productoSelector.innerHTML = '<option value="" disabled selected>Seleccione producto...</option>';
            if (categoria && subcat && this.taxonomia[categoria][subcat]) {
                for (const producto of this.taxonomia[categoria][subcat]) {
                    const opt = document.createElement('option');
                    opt.value = producto;
                    opt.textContent = producto;
                    this.productoSelector.appendChild(opt);
                }
                this.productoSelector.disabled = false;
            } else {
                this.productoSelector.disabled = true;
            }
            this.updateSubmitState();
        });
        this.productoSelector.addEventListener('change', () => {
            const producto = this.productoSelector.value;
            this.productNameInput.value = producto;
            this.updateSubmitState();
        });
        this.customProductName.addEventListener('input', () => {
            const custom = this.customProductName.value.trim();
            if (custom.length > 0) {
                this.productNameInput.value = custom;
            } else if (this.productoSelector.value) {
                this.productNameInput.value = this.productoSelector.value;
            } else {
                this.productNameInput.value = '';
            }
            this.updateSubmitState();
        });
    }

    updateSubmitState() {
        const categoria = this.categoriaSelector.value;
        const subcat = this.subcategoriaSelector.value;
        const producto = this.productoSelector.value;
        const custom = this.customProductName.value.trim();
        const valid = categoria && subcat && (producto || custom);
        if (this.submitBtn) {
            this.submitBtn.disabled = !valid;
            this.submitBtn.style.opacity = valid ? '1' : '0.6';
        }
        if (this.options.onSelect) {
            this.options.onSelect({ categoria, subcategoria: subcat, producto: custom || producto });
        }
    }

    getSelectedProduct() {
        return {
            categoria: this.categoriaSelector.value,
            subcategoria: this.subcategoriaSelector.value,
            producto: this.customProductName.value.trim() || this.productoSelector.value
        };
    }
}

window.TaxonomiaSelector = TaxonomiaSelector;
