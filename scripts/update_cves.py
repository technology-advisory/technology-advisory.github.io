<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo Maestro de Vulnerabilidades | Intelligence</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <style>
        body { background: #0a0f1a; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; }
        .container { max-width: 1240px; margin: 40px auto; padding: 0 4%; }
        
        /* Buscador */
        .search-area { margin-bottom: 30px; display: flex; gap: 15px; }
        .search-input { 
            flex: 1; padding: 12px 20px; background: #111827; border: 1px solid #374151; 
            border-radius: 8px; color: white; font-size: 0.9rem; outline: none;
        }
        .search-input:focus { border-color: var(--accent); box-shadow: 0 0 10px rgba(59, 130, 246, 0.2); }

        .cve-table { width: 100%; border-collapse: collapse; background: #111827; border-radius: 12px; overflow: hidden; }
        .cve-table th { text-align: left; color: var(--accent); font-size: 0.75rem; text-transform: uppercase; padding: 18px; background: #1f2937; }
        .cve-table td { padding: 18px; border-bottom: 1px solid #374151; font-size: 0.85rem; vertical-align: top; }
        
        .cvss-badge { font-weight: 800; padding: 4px 10px; border-radius: 6px; font-family: 'JetBrains Mono'; font-size: 0.75rem; white-space: nowrap; }
        .critical { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
        .high { background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid #f97316; }
        .medium { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
        .na { background: #1f2937; color: #94a3b8; border: 1px solid #374151; }
        
        .desc-text { font-size: 0.8rem; color: #94a3b8; line-height: 1.5; max-width: 500px; }
        .back-link { color: var(--accent); text-decoration: none; font-weight: 600; display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>

    <div class="container">
        <a href="../index.html" class="back-link">← Volver al Dashboard</a>
        <h1 style="font-size: 1.8rem; margin-bottom: 5px;">Catálogo Maestro de Vulnerabilidades</h1>
        <p style="color: #94a3b8; margin-bottom: 30px;">Cruce de datos CISA KEV + NIST NVD (Métricas CVSS v4.0)</p>

        <div class="search-area">
            <input type="text" id="cveSearch" class="search-input" placeholder="Buscar por CVE ID, Fabricante o Producto (ej: Microsoft, Apple, Cisco)...">
        </div>

        <table class="cve-table">
            <thead>
                <tr>
                    <th style="width: 140px;">CVE ID</th>
                    <th style="width: 220px;">Fabricante y Producto</th>
                    <th style="width: 110px;">Fecha KEV</th>
                    <th style="width: 100px;">CVSS Score</th>
                    <th>Descripción de la Amenaza</th>
                </tr>
            </thead>
            <tbody id="cve-body">
                </tbody>
        </table>
    </div>

    <script>
        let allVulnerabilities = [];

        async function loadData() {
            try {
                const res = await fetch('../data/cve.json');
                const data = await res.json();
                allVulnerabilities = data.vulnerabilities.sort((a, b) => new Date(b.dateAdded) - new Date(a.dateAdded));
                renderTable(allVulnerabilities);
            } catch (e) { console.error("Error cargando JSON:", e); }
        }

        function renderTable(list) {
            const tbody = document.getElementById('cve-body');
            tbody.innerHTML = list.map(v => {
                const score = v.cvssScore || "N/A";
                let sevClass = "na";
                
                if (score !== "N/A") {
                    if (score >= 9.0) sevClass = "critical";
                    else if (score >= 7.0) sevClass = "high";
                    else sevClass = "medium";
                }

                return `
                    <tr>
                        <td style="color:var(--accent); font-weight:800; font-family:'JetBrains Mono';">${v.cveID}</td>
                        <td>
                            <div style="font-weight:700;">${v.vendorProject}</div>
                            <div style="font-size:0.75rem; color:#94a3b8;">${v.product}</div>
                        </td>
                        <td style="color:#94a3b8; font-size:0.8rem; font-family:'JetBrains Mono';">${v.dateAdded}</td>
                        <td><span class="cvss-badge ${sevClass}">${score}</span></td>
                        <td class="desc-text">${v.shortDescription || "No hay descripción detallada disponible."}</td>
                    </tr>
                `;
            }).join('');
        }

        // Lógica del Buscador
        document.getElementById('cveSearch').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = allVulnerabilities.filter(v => 
                v.cveID.toLowerCase().includes(term) ||
                v.vendorProject.toLowerCase().includes(term) ||
                v.product.toLowerCase().includes(term)
            );
            renderTable(filtered);
        });

        loadData();
    </script>
</body>
</html>