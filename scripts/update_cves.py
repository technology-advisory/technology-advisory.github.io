import requests
import json
import os
import time
from datetime import datetime

# Configuración
CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NVD_API_URL = "https://services.nvd.nist.gov/api/rest/json/cves/2.0?cveId="
OUTPUT_FILE = "data/cve.json"

def get_cvss_score(cve_id):
    """
    Consulta la API de NIST NVD para obtener el score CVSS.
    Prioriza v4.0, luego v3.1 y v3.0.
    """
    try:
        # Pausa de seguridad para evitar Rate Limiting (NIST permite 5 peticiones cada 30s sin API Key)
        time.sleep(6) 
        response = requests.get(f"{NVD_API_URL}{cve_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            vulnerabilities = data.get('vulnerabilities', [])
            if not vulnerabilities:
                return "N/A"
            
            metrics = vulnerabilities[0]['cve'].get('metrics', {})
            
            # 1. Intentar CVSS v4.0
            if 'cvssMetricV40' in metrics:
                return metrics['cvssMetricV40'][0]['cvssData']['baseScore']
            # 2. Intentar CVSS v3.1
            elif 'cvssMetricV31' in metrics:
                return metrics['cvssMetricV31'][0]['cvssData']['baseScore']
            # 3. Intentar CVSS v3.0
            elif 'cvssMetricV30' in metrics:
                return metrics['cvssMetricV30'][0]['cvssData']['baseScore']
        return "N/A"
    except Exception as e:
        print(f"Error consultando NVD para {cve_id}: {e}")
        return "N/A"

def update_cve_data():
    print(f"[{datetime.now()}] Iniciando actualización de CVEs...")
    
    try:
        # 1. Descargar datos de CISA
        response = requests.get(CISA_URL)
        response.raise_for_status()
        cisa_data = response.json()
        
        # 2. Filtrar y procesar (Tomamos los 20 más recientes para no eternizar el proceso)
        # El histórico completo de CISA tiene miles; el robot tardaría horas por el delay de NIST.
        raw_vulnerabilities = cisa_data.get('vulnerabilities', [])
        # Ordenar por fecha de añadido (más recientes primero)
        raw_vulnerabilities.sort(key=lambda x: x['dateAdded'], reverse=True)
        
        processed_vulnerabilities = []
        
        # Procesamos solo los 30 más recientes para mantener el Action rápido
        for v in raw_vulnerabilities[:30]:
            cve_id = v.get('cveID')
            print(f"Procesando {cve_id}...")
            
            # Enriquecer con CVSS de NVD
            v['cvssScore'] = get_cvss_score(cve_id)
            processed_vulnerabilities.append(v)
            
        # 3. Preparar JSON final
        final_data = {
            "title": "CISA Intelligence Dashboard + NIST NVD",
            "last_update_check": datetime.utcnow().isoformat() + "Z",
            "vulnerabilities": processed_vulnerabilities
        }
        
        # 4. Guardar archivo
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
        print(f"Éxito: {len(processed_vulnerabilities)} CVEs actualizados en {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error crítico en la actualización: {e}")

if __name__ == "__main__":
    update_cve_data()