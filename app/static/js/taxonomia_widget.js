// taxonomia_widget.js
// Widget de selección de producto

class TaxonomiaSelector {
    constructor(options = {}) {
        this.categoriaSelector = document.getElementById('categoriaSelector');
        this.subcategoria2Selector = document.getElementById('subcategoria2Selector');
        this.subcategoria3Selector = document.getElementById('subcategoria3Selector');
        this.customProductName = document.getElementById('customProductName');
        this.productNameInput = document.getElementById('productName');
        this.productTypeInput = document.getElementById('productType');
        this.submitBtn = document.querySelector('.product-form button[type="submit"]');
        this.taxonomia = null;
        this.options = options;
        this.init();
    }

    async init() {
        await this.fillCategorias();
        this.addListeners();
        this.updateSubmitState();
    }

    async fillCategorias() {
        this.categoriaSelector.innerHTML = '<option value="" disabled selected>Seleccione categoría...</option>';
        // Cargar toda la estructura de taxonomía (categoría > subcategoría > productos)
        const res = await fetch('/api/taxonomia/estructura');
        this.taxonomia = await res.json();
        Object.keys(this.taxonomia).forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat;
            this.categoriaSelector.appendChild(opt);
        });
        this.categoriaSelector.disabled = false;
        this.populateSubcategoria2();
        this.populateSubcategoria3();
    }

    populateSubcategoria2() {
        this.subcategoria2Selector.innerHTML = '<option value="" disabled selected>Seleccione subcategoría 2...</option>';
        const categoria = this.categoriaSelector.value;
        if (categoria && this.taxonomia[categoria]) {
            Object.keys(this.taxonomia[categoria]).forEach(subcat2 => {
                const opt = document.createElement('option');
                opt.value = subcat2;
                opt.textContent = subcat2;
                this.subcategoria2Selector.appendChild(opt);
            });
            this.subcategoria2Selector.disabled = false;
        } else {
            this.subcategoria2Selector.disabled = true;
        }
    }

    populateSubcategoria3() {
        this.subcategoria3Selector.innerHTML = '<option value="" disabled selected>Seleccione subcategoría 3...</option>';
        const categoria = this.categoriaSelector.value;
        const subcat2 = this.subcategoria2Selector.value;
        if (categoria && subcat2 && this.taxonomia[categoria] && this.taxonomia[categoria][subcat2]) {
            const subcats3 = this.taxonomia[categoria][subcat2];
            if (subcats3.length > 0) {
                subcats3.forEach(subcat3 => {
                    const opt = document.createElement('option');
                    opt.value = subcat3;
                    opt.textContent = subcat3;
                    this.subcategoria3Selector.appendChild(opt);
                });
                this.subcategoria3Selector.disabled = false;
            } else {
                this.subcategoria3Selector.disabled = true;
            }
        } else {
            this.subcategoria3Selector.disabled = true;
        }
    }

    addListeners() {
        this.categoriaSelector.addEventListener('change', () => {
            this.populateSubcategoria2();
            this.populateSubcategoria3();
            this.updateHiddenFields();
            this.updateSubmitState();
        });
        this.subcategoria2Selector.addEventListener('change', () => {
            this.populateSubcategoria3();
            this.updateHiddenFields();
            this.updateSubmitState();
        });
        this.subcategoria3Selector.addEventListener('change', () => {
            this.updateHiddenFields();
            this.updateSubmitState();
        });
        this.customProductName.addEventListener('input', () => {
            const custom = this.customProductName.value.trim();
            this.productNameInput.value = custom;
            this.updateSubmitState();
        });
    }

    updateHiddenFields() {
        // Rellena los campos ocultos para el backend
        const categoria = this.categoriaSelector.value;
        const subcat2 = this.subcategoria2Selector.value;
        const subcat3 = this.subcategoria3Selector.value;
        this.productTypeInput.value = subcat3 || subcat2 || '';
    }

    updateSubmitState() {
        const categoria = this.categoriaSelector.value;
        const subcat2 = this.subcategoria2Selector.value;
        const subcat3 = this.subcategoria3Selector.value;
        const custom = this.customProductName.value.trim();
        // La subcategoría válida es la de nivel 3 si existe, si no la de nivel 2
        const subcat = subcat3 || subcat2;
        // El producto válido es el nombre personalizado si existe
        const valid = categoria && subcat && custom.length > 0;
        if (this.submitBtn) {
            this.submitBtn.disabled = !valid;
            this.submitBtn.style.opacity = valid ? '1' : '0.6';
        }
        if (this.options.onSelect) {
            this.options.onSelect({ categoria, subcategoria: subcat, producto: custom });
        }
    }

    getSelectedProduct() {
        return {
            categoria: this.categoriaSelector.value,
            subcategoria: this.subcategoria3Selector.value || this.subcategoria2Selector.value,
            producto: this.customProductName.value.trim()
        };
    }
}

window.TaxonomiaSelector = TaxonomiaSelector;
