document.addEventListener('DOMContentLoaded', () => {
    
    // 1. CARGA DE NOTICIAS, TAGS Y CONTADOR
    fetch('data/noticias.json')
        .then(response => {
            if (!response.ok) throw new Error("No se encuentra noticias.json");
            return response.json();
        })
        .then(data => {
            // A. Inyectar Notas Técnicas (Como DIVs, no como LINKS)
            const notasCont = document.getElementById('notas-container');
            if (notasCont && data.notas_tecnicas) {
                notasCont.innerHTML = data.notas_tecnicas.map(nota => `
                    <div class="glass-card">
                        <div style="font-size: 0.7rem; color: var(--accent); font-weight: 800; margin-bottom: 8px;">${nota.tag}</div>
                        <h3 style="font-size: 1rem; margin-bottom: 8px;">${nota.titulo}</h3>
                        <p style="font-size: 0.85rem; color: var(--text-muted);">${nota.desc}</p>
                    </div>
                `).join('');
            }

            // B. Inyectar Tendencias/Tags
            const tagCont = document.getElementById('tendencias-container');
            if (tagCont && data.tendencias) {
                tagCont.innerHTML = data.tendencias.map(t => `
                    <span class="tag" style="background: ${t.color}; color: ${t.texto}; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px;">${t.nombre}</span>
                `).join('');
            }

            // C. Animación del Contador
            const countEl = document.getElementById('suscriptores-count');
            if (countEl && data.suscriptores) {
                let current = 0;
                const target = data.suscriptores;
                const increment = Math.ceil(target / 100);
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        countEl.innerText = target.toLocaleString();
                        clearInterval(timer);
                    } else {
                        countEl.innerText = current.toLocaleString();
                    }
                }, 20);
            }
        })
        .catch(error => console.error("Error en noticias:", error));

    // 2. CARGA DE INTELIGENCIA DE AMENAZAS (TOP 3)
    const vulnCont = document.getElementById('vuln-container');

    // Usamos ./data/ para asegurar la ruta en GitHub Pages
    fetch('./data/cve.json?t=' + new Date().getTime())
        .then(res => {
            if (!res.ok) throw new Error("Error al leer cve.json");
            return res.json();
        })
        .then(localData => {
            // Limitamos a los 3 primeros (Top 3)
            const top3 = localData.vulnerabilities.slice(0, 3);
            renderVulnerabilidades(top3);
        })
        .catch(localErr => {
            console.error("Error cargando cve.json:", localErr);
            if(vulnCont) vulnCont.innerHTML = "<p style='font-size:0.8rem; color: var(--text-muted);'>Inteligencia temporalmente no disponible.</p>";
        });
});

// Función auxiliar para pintar las CVEs
function renderVulnerabilidades(items) {
    const vulnCont = document.getElementById('vuln-container');
    if (!vulnCont) return;

    vulnCont.innerHTML = items.map(v => `
        <div class="vuln-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="font-family:'JetBrains Mono'; font-size:0.85rem; color:var(--accent);">${v.cveID}</h4>
                <span style="border:1px solid #ef4444; color:#ef4444; font-size:0.6rem; padding:1px 4px; border-radius:3px; font-weight:bold;">ACTIVA</span>
            </div>
            <p style="font-size:0.75rem; color:var(--text); font-weight:bold; margin-top:5px;">${v.vendorProject} ${v.product}</p>
            <p style="font-size:0.75rem; color:var(--text-muted); line-height:1.3; margin-top:2px;">${v.vulnerabilityName}</p>
        </div>
    `).join('');
}