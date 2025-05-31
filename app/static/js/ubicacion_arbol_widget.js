// Widget de árbol de selección para Región > Provincia > Cantón
// Similar a TaxonomiaSelector, pero para ubicación geográfica

class UbicacionArbolSelector {
    constructor(options = {}) {
        this.options = options;
        this.data = null;
        this.selected = { region: '', provincia: '', canton: '' };
        this.init();
    }

    async init() {
        // Cargar la estructura desde el backend
        this.data = await this.getEstructura();
        this.renderTree();
        this.addListeners();
    }

    async getEstructura() {
        const res = await fetch('/api/ubicacion/estructura');
        return await res.json();
    }

    renderTree() {
        const container = document.getElementById('ubicacion-arbol');
        if (!container || !this.data) return;
        container.innerHTML = '';
        
        // Crear el árbol con estructura horizontal
        let treeHTML = '<ul class="taxonomia-tree">';
        
        // Crear botones de región en línea horizontal
        for (const region in this.data) {
            treeHTML += `
                <li class="categoria">
                    <span class="toggle collapsed">+</span>
                    <span>${region}</span>
                    <ul>`;
            
            // Provincias como submenú desplegable
            for (const provincia in this.data[region]) {
                treeHTML += `
                        <li class="subcategoria">
                            <span class="toggle collapsed">+</span>
                            <span>${provincia}</span>
                            <ul>`;
                
                // Cantones como elementos finales
                for (const canton of this.data[region][provincia]) {
                    treeHTML += `
                                <li class="producto-leaf" data-region="${region}" data-provincia="${provincia}" data-canton="${canton}">${canton}</li>`;
                }
                
                treeHTML += `
                            </ul>
                        </li>`;
            }
            
            treeHTML += `
                    </ul>
                </li>`;
        }
        
        treeHTML += '</ul>';
        container.innerHTML = treeHTML;
        
        // Agregar event listeners después de crear el HTML
        this.setupEventListeners();
    }

    setupEventListeners() {
        const container = document.getElementById('ubicacion-arbol');
        
        // Agregar evento de clic a los toggles de región y provincia
        container.querySelectorAll('.toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const parentLi = toggle.parentNode;
                const isExpanded = parentLi.classList.toggle('expanded');
                
                // Cerrar otros elementos del mismo nivel si se está expandiendo
                if (isExpanded) {
                    // Cambiar el estilo del toggle
                    toggle.classList.remove('collapsed');
                    toggle.textContent = '-';
                    
                    // Si es una categoría (región), cerrar otras categorías
                    if (parentLi.classList.contains('categoria')) {
                        const siblings = Array.from(parentLi.parentNode.children).filter(el => 
                            el !== parentLi && el.classList.contains('categoria'));
                        
                        siblings.forEach(sibling => {
                            sibling.classList.remove('expanded');
                            const siblingToggle = sibling.querySelector('.toggle');
                            if (siblingToggle) {
                                siblingToggle.classList.add('collapsed');
                                siblingToggle.textContent = '+';
                            }
                        });
                    }
                } else {
                    // Colapsar
                    toggle.classList.add('collapsed');
                    toggle.textContent = '+';
                }
            });
        });
        
        // Agregar evento de clic a los nombres de región y provincia
        container.querySelectorAll('.categoria > span:not(.toggle), .subcategoria > span:not(.toggle)').forEach(label => {
            label.addEventListener('click', function() {
                const parentLi = label.parentNode;
                const toggle = parentLi.querySelector('.toggle');
                if (toggle) toggle.click();
            });
        });
        
        // Agregar evento de clic a los cantones
        container.querySelectorAll('.producto-leaf').forEach(leaf => {
            leaf.addEventListener('click', () => {
                // Quitar la selección anterior
                container.querySelectorAll('.producto-leaf.selected').forEach(el => {
                    el.classList.remove('selected');
                });
                
                // Aplicar la selección actual
                leaf.classList.add('selected');
                
                const region = leaf.getAttribute('data-region');
                const provincia = leaf.getAttribute('data-provincia');
                const canton = leaf.getAttribute('data-canton');
                this.selectUbicacion(region, provincia, canton);
            });
        });
    }

    selectUbicacion(region, provincia, canton) {
        this.selected = { region, provincia, canton };
        document.getElementById('region').value = region;
        document.getElementById('provincia').value = provincia;
        document.getElementById('canton').value = canton;
        
        // Visual feedback - quitar selección anterior
        const container = document.getElementById('ubicacion-arbol');
        container.querySelectorAll('.producto-leaf.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Agregar selección al cantón elegido
        container.querySelectorAll('.producto-leaf').forEach(el => {
            if (el.textContent === canton) {
                el.classList.add('selected');
            }
        });
        
        if (this.options.onSelect) {
            this.options.onSelect(this.selected);
        }
    }

    addListeners() {
        // Método para manejar cambios externos si es necesario
    }

    getSelectedUbicacion() {
        return this.selected;
    }
}

window.UbicacionArbolSelector = UbicacionArbolSelector;
