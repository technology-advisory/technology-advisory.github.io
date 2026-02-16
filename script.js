document.addEventListener('DOMContentLoaded', function() {
    fetch('data/noticias.json')
        .then(response => response.json())
        .then(data => {
            
            // 1. Cargar Notas Técnicas
            const notasContainer = document.getElementById('notas-container');
            if (notasContainer) {
                notasContainer.innerHTML = data.notas_tecnicas.map(nota => `
                    <a href="notas-tecnicas/${nota.archivo}" class="glass-card">
                        <div class="card-tag">${nota.tag}</div>
                        <h3>${nota.titulo}</h3>
                        <p>${nota.desc}</p>
                        <span style="font-size: 0.7rem; color: var(--text-muted);">${nota.fecha}</span>
                    </a>
                `).join('');
            }

            // 2. Cargar Vulnerabilidades (Sidebar)
            const vulnContainer = document.getElementById('vuln-container');
            if (vulnContainer) {
                vulnContainer.innerHTML = data.vulnerabilidades.map(v => `
                    <div class="vuln-item">
                        <div class="vuln-header">
                            <span class="cve-id">${v.cve}</span>
                            <span class="severity" style="color: ${v.severidad === 'critical' ? '#ef4444' : '#f97316'}">
                                ${v.severidad.toUpperCase()}
                            </span>
                        </div>
                        <p>${v.desc}</p>
                    </div>
                `).join('');
            }

            // 3. Cargar Tendencias/Tags
            const tendenciasContainer = document.getElementById('tendencias-container');
            if (tendenciasContainer) {
                tendenciasContainer.innerHTML = data.tendencias.map(t => `
                    <span style="background: ${t.color}; color: ${t.texto}; padding: 5px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;">
                        ${t.nombre}
                    </span>
                `).join('');
            }
        });
});