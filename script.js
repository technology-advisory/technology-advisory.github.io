// script.js - Carga dinámica de contenido
document.addEventListener('DOMContentLoaded', function() {
    fetch('data/noticias.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error cargando noticias');
            }
            return response.json();
        })
        .then(data => {
            // 1. Cargar Notas Técnicas
            const notasContainer = document.getElementById('notas-container');
            if (notasContainer) {
                notasContainer.innerHTML = data.notas_tecnicas.map(nota => `
                    <a href="notas-tecnicas/${nota.archivo}" class="card">
                        <span class="tag ${nota.severidad}">${nota.tag}</span>
                        <h3>${nota.titulo}</h3>
                        <p>${nota.desc}</p>
                        <div class="date-badge">
                            <span>📅</span> ${nota.fecha}
                        </div>
                    </a>
                `).join('');
            }

            // 2. Cargar Vulnerabilidades principales
            const vulnContainer = document.getElementById('vulnerabilidades-container');
            if (vulnContainer) {
                vulnContainer.innerHTML = data.vulnerabilidades.slice(0, 3).map(vuln => `
                    <a href="vulnerabilidades/${vuln.archivo}" class="card">
                        <span class="tag ${vuln.severidad}">${vuln.cve} · ${vuln.severidad.toUpperCase()}</span>
                        <h3>${vuln.titulo}</h3>
                        <p>${vuln.desc}</p>
                        <div class="date-badge">
                            <span>⚠️</span> ${vuln.estado}
                        </div>
                    </a>
                `).join('');
            }

            // 3. Cargar Últimas Vulnerabilidades (sidebar)
            const ultimasVuln = document.getElementById('ultimas-vuln');
            if (ultimasVuln) {
                ultimasVuln.innerHTML = data.vulnerabilidades.slice(0, 5).map(vuln => `
                    <div class="vuln-item">
                        <div class="vuln-meta">
                            <span class="tag ${vuln.severidad}">${vuln.severidad}</span>
                            <span class="vuln-title">${vuln.cve}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">${vuln.titulo}</div>
                    </div>
                `).join('');
            }

            // 4. Cargar Tendencias
            const tendenciasContainer = document.getElementById('tendencias-container');
            if (tendenciasContainer && data.tendencias) {
                tendenciasContainer.innerHTML = data.tendencias.map(tag => `
                    <span class="tag medium" style="background: ${tag.color}; color: ${tag.texto};">${tag.nombre}</span>
                `).join('');
            }

            // 5. Actualizar contador de suscriptores
            const suscriptoresSpan = document.getElementById('suscriptores');
            if (suscriptoresSpan && data.suscriptores) {
                suscriptoresSpan.textContent = data.suscriptores;
            }
        })
        .catch(error => {
            console.error('Error cargando datos:', error);
            // Fallback: mostrar mensaje amigable
            document.getElementById('notas-container').innerHTML = `
                <div class="card" style="grid-column: 1/-1; text-align: center;">
                    <p>Error cargando noticias. Por favor, recarga la página.</p>
                </div>
            `;
        });
});
