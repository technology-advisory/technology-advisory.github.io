<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Archivo CVE | Technology Advisory</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <style>
        body { background: #0a0f1a; color: #f8fafc; font-family: sans-serif; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .search-box { width: 100%; padding: 12px; background: #111827; border: 1px solid #374151; border-radius: 8px; color: white; margin-bottom: 20px; }
        .cve-table { width: 100%; border-collapse: collapse; background: #111827; }
        .cve-table th { text-align: left; padding: 15px; background: #1f2937; color: #3b82f6; font-size: 0.8rem; }
        .cve-table td { padding: 15px; border-bottom: 1px solid #374151; font-size: 0.85rem; }
        .cvss-badge { font-weight: bold; padding: 4px 8px; border-radius: 4px; border: 1px solid; }
        .critical { color: #f87171; border-color: #ef4444; }
        .high { color: #fb923c; border-color: #f97316; }
        .na { color: #94a3b8; border-color: #374151; }
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" style="color:#3b82f6; text-decoration:none;">← Dashboard</a>
        <h1>Catálogo Maestro de Vulnerabilidades</h1>
        <input type="text" id="cveSearch" class="search-box" placeholder="Buscar por CVE, Fabricante...">
        <table class="cve-table">
            <thead>
                <tr>
                    <th>CVE ID</th>
                    <th>Producto</th>
                    <th>Fecha</th>
                    <th>Score</th>
                    <th>Descripción</th>
                </tr>
            </thead>
            <tbody id="cve-body"></tbody>
        </table>
    </div>
    <script>
        async function init() {
            const [rCisa, rNvd] = await Promise.all([
                fetch('../data/cve.json?t=' + Date.now()),
                fetch('../data/nvd_scores.json?t=' + Date.now()).catch(() => ({}))
            ]);
            const cisa = (await rCisa.json()).vulnerabilities;
            const nvd = await rNvd.json();
            
            const render = (list) => {
                document.getElementById('cve-body').innerHTML = list.map(v => {
                    const s = nvd[v.cveID] || "N/A";
                    const cls = s >= 9 ? 'critical' : (s >= 7 ? 'high' : 'na');
                    return `<tr>
                        <td><a href="https://db.gcve.eu/cve/${v.cveID}" target="_blank" style="color:#3b82f6; font-weight:bold; text-decoration:none;">${v.cveID}</a></td>
                        <td><b>${v.vendorProject}</b><br><small>${v.product}</small></td>
                        <td>${v.dateAdded}</td>
                        <td><span class="cvss-badge ${cls}">${s}</span></td>
                        <td style="font-size:0.75rem; color:#94a3b8;">${v.shortDescription || v.vulnerabilityName}</td>
                    </tr>`;
                }).join('');
            };

            render(cisa);
            document.getElementById('cveSearch').oninput = (e) => {
                const t = e.target.value.toLowerCase();
                render(cisa.filter(v => v.cveID.toLowerCase().includes(t) || v.vendorProject.toLowerCase().includes(t)));
            };
        }
        init();
    </script>
</body>
</html>