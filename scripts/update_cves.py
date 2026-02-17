import requests
import json
import os
from datetime import datetime

CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
OUTPUT_FILE = "data/cve.json"

def update_cves():
    print(f"[{datetime.now()}] Iniciando descarga de CISA KEV...")
    try:
        response = requests.get(CISA_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        vulnerabilities = data.get('vulnerabilities', [])
        # Ordenar por fecha: lo más nuevo de 2026 arriba
        vulnerabilities.sort(key=lambda x: x['dateAdded'], reverse=True)
        
        for v in vulnerabilities:
            if 'shortDescription' not in v or not v['shortDescription']:
                v['shortDescription'] = v.get('vulnerabilityName', "No hay descripción disponible.")

        final_data = {
            "title": "CISA Intelligence Dashboard",
            "last_update_check": datetime.utcnow().isoformat() + "Z",
            "vulnerabilities": vulnerabilities
        }
        
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        print(f"Éxito: {len(vulnerabilities)} CVEs guardados.")

    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    update_cves()