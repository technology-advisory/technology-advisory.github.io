// script.js - Carga dinámica de contenido
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 Script iniciado - Versión definitiva");
    
    fetch('data/noticias.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status} - No se pudo cargar noticias.json`);
            }
            return response.json();
        })
        .then(data => {
            console.log("📊 Datos cargados correctamente:", data);
            
            // 1. NOTAS TÉCNICAS
            const notasContainer = document.getElementById('notas-container');
            if (notasContainer) {
                console.log("✅ Cargando", data.notas_tecnicas.length, "notas técnicas");
                let htmlNotas = '';
                data.notas_tecnicas.forEach(nota => {
                    htmlNotas += `
                        <a href="notas-tecnicas/${nota.archivo}" class="card">
                            <span class="tag ${nota.severidad}">${nota.tag}</span>
                            <h3>${nota.titulo}</h3>
                            <p>${nota.desc}</p>
                            <div class="date-badge">
                                <span>📅</span> ${nota.fecha}
                            </div>
                        </a>
                    `;
                });
                notasContainer.innerHTML = htmlNotas;
            } else {
                console.error("❌ No se encontró el elemento 'notas-container'");
            }

            // 2. VULNERABILIDADES PRINCIPALES
            const vulnContainer = document.getElementById('vulnerabilidades-container');
            if (vulnContainer) {
                console.log("✅ Cargando", Math.min(3, data.vulnerabilidades.length), "vulnerabilidades principales");
                let htmlVuln = '';
                data.vulnerabilidades.slice(0, 3).forEach(vuln => {
                    htmlVuln += `
                        <a href="vulnerabilidades/${vuln.archivo}" class="card">
                            <span class="tag ${vuln.severidad}">${vuln.cve} · ${vuln.severidad.toUpperCase()}</span>
                            <h3>${vuln.titulo}</h3>
                            <p>${vuln.desc}</p>
                            <div class="date-badge">
                                <span>⚠️</span> ${vuln.estado}
                            </div>
                        </a>
                    `;
                });
                vulnContainer.innerHTML = htmlVuln;
            }

            // 3. ÚLTIMAS VULNERABILIDADES (SIDEBAR)
            const ultimasVuln = document.getElementById('ultimas-vuln');
            if (ultimasVuln) {
                let htmlUltimas = '';
                data.vulnerabilidades.slice(0, 5).forEach(vuln => {
                    htmlUltimas += `
                        <div class="vuln-item">
                            <div class="vuln-meta">
                                <span class="tag ${vuln.severidad}">${vuln.severidad}</span>
                                <span class="vuln-title">${vuln.cve}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">${vuln.titulo}</div>
                        </div>
                    `;
                });
                ultimasVuln.innerHTML = htmlUltimas;
            }

            // 4. TENDENCIAS
            const tendenciasContainer = document.getElementById('tendencias-container');
            if (tendenciasContainer && data.tendencias) {
                let htmlTendencias = '';
                data.tendencias.forEach(tag => {
                    htmlTendencias += `
                        <span class="tag medium" style="background: ${tag.color}; color: ${tag.texto};">${tag.nombre}</span>
                    `;
                });
                tendenciasContainer.innerHTML = htmlTendencias;
            }

            // 5. SUSCRIPTORES
            const suscriptoresSpan = document.getElementById('suscriptores');
            if (suscriptoresSpan && data.suscriptores) {
                suscriptoresSpan.textContent = data.suscriptores;
            }

            console.log("🎉 ¡Todo cargado correctamente!");
        })
        .catch(error => {
            console.error("❌ ERROR GRAVE:", error);
            
            // Mostrar error visible en la página
            const notasContainer = document.getElementById('notas-container');
            if (notasContainer) {
                notasContainer.innerHTML = `
                    <div class="card" style="grid-column: 1/-1; text-align: center; padding: 2rem; background: #fff0f0; border: 2px solid #ff4444;">
                        <h3 style="color: #ff4444;">⚠️ Error al cargar las noticias</h3>
                        <p>${error.message}</p>
                        <p style="font-size: 0.85rem; margin-top: 1rem;">Revisa la consola (F12) para más detalles</p>
                    </div>
                `;
            }
        });
});