import requests
import json
import os
import time

CISA_FILE = "data/cve.json"
NVD_CACHE_FILE = "data/nvd_scores.json"
GCVE_API_URL = "https://db.gcve.eu/api/v1/cves/"

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
    cisa_data = load_json(CISA_FILE)
    nvd_cache = load_json(NVD_CACHE_FILE)
    vulnerabilities = cisa_data.get('vulnerabilities', [])
    updated = False

    for v in vulnerabilities:
        cve_id = v['cveID']
        
        # Consultamos si no está en el caché o si el valor es N/A
        if cve_id not in nvd_cache or nvd_cache[cve_id] == "N/A":
            print(f"Consultando GCVE para {cve_id}...")
            try:
                time.sleep(0.5) # Mucho más rápido que antes
                res = requests.get(f"{GCVE_API_URL}{cve_id}", timeout=10)
                
                if res.status_code == 200:
                    data = res.json()
                    # Extraemos el score de la estructura de GCVE
                    score = data.get('cvss', {}).get('score', "N/A")
                    nvd_cache[cve_id] = score
                    updated = True
                    print(f" -> Score de GCVE: {score}")
                else:
                    nvd_cache[cve_id] = "N/A"
            except:
                nvd_cache[cve_id] = "N/A"

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Base de datos de severidad actualizada con éxito desde GCVE.")
    else:
        print("No hay nuevos datos que actualizar.")

if __name__ == "__main__":
    update_nvd()