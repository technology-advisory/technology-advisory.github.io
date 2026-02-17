import requests
import json
import os
from datetime import datetime

# Configuración de rutas
CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
OUTPUT_FILE = "data/cve.json"

def update_cves():
    print(f"[{datetime.now()}] Iniciando descarga de CISA KEV...")
    
    try:
        # 1. Descargar el feed oficial
        response = requests.get(CISA_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # 2. Extraer y ordenar vulnerabilidades
        # Las ordenamos por 'dateAdded' descendente para que 2026 esté arriba
        vulnerabilities = data.get('vulnerabilities', [])
        vulnerabilities.sort(key=lambda x: x['dateAdded'], reverse=True)
        
        # 3. Limpieza y preparación de datos
        # Nos aseguramos de que todos tengan el campo shortDescription
        for v in vulnerabilities:
            if 'shortDescription' not in v or not v['shortDescription']:
                v['shortDescription'] = v.get('vulnerabilityName', "No hay descripción técnica disponible.")

        # 4. Estructura final del JSON
        final_data = {
            "title": "CISA Intelligence Dashboard",
            "last_update_check": datetime.utcnow().isoformat() + "Z",
            "vulnerabilities": vulnerabilities
        }
        
        # 5. Guardar en la carpeta data
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
        print(f"Éxito: {len(vulnerabilities)} vulnerabilidades guardadas en {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error crítico actualizando CISA: {e}")

if __name__ == "__main__":
    update_cves()