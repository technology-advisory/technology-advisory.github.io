import requests
import json
import os
import time

# Configuración de rutas
CISA_FILE = "data/cve.json"
NVD_CACHE_FILE = "data/nvd_scores.json"
NVD_API_URL = "https://services.nvd.nist.gov/api/rest/json/cves/2.0?cveId="

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def update_nvd():
    # 1. Cargar la lista de CISA (generada por tu otro script)
    cisa_data = load_json(CISA_FILE)
    # 2. Cargar el caché de scores (si ya existe)
    nvd_cache = load_json(NVD_CACHE_FILE) 
    
    vulnerabilities = cisa_data.get('vulnerabilities', [])
    updated = False

    # Solo procesamos los IDs que no tengamos ya en el caché
    for v in vulnerabilities:
        cve_id = v['cveID']
        
        if cve_id not in nvd_cache:
            print(f"Buscando score para {cve_id} en NIST...")
            try:
                # Pausa técnica para evitar que el gobierno de EEUU nos bloquee
                time.sleep(6) 
                res = requests.get(f"{NVD_API_URL}{cve_id}", timeout=10)
                
                if res.status_code == 200:
                    data = res.json()
                    vulns = data.get('vulnerabilities', [])
                    if not vulns:
                        continue
                        
                    metrics = vulns[0]['cve'].get('metrics', {})
                    score = "N/A"
                    
                    # Intentar obtener CVSS v4.0, v3.1 o v3.0
                    if 'cvssMetricV40' in metrics:
                        score = metrics['cvssMetricV40'][0]['cvssData']['baseScore']
                    elif 'cvssMetricV31' in metrics:
                        score = metrics['cvssMetricV31'][0]['cvssData']['baseScore']
                    elif 'cvssMetricV30' in metrics:
                        score = metrics['cvssMetricV30'][0]['cvssData']['baseScore']
                    
                    nvd_cache[cve_id] = score
                    updated = True
                    print(f"-> {cve_id}: {score}")
            except Exception as e:
                print(f"Error con {cve_id}: {e}")
                continue

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Caché de scores NVD actualizado correctamente.")
    else:
        print("No se encontraron nuevos CVEs para enriquecer.")

if __name__ == "__main__":
    update_nvd()