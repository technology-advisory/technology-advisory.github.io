import requests
import json
import os
import time

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
    # 1. Cargar lo que ya tenemos para no repetir peticiones innecesarias
    cisa_data = load_json(CISA_FILE)
    nvd_cache = load_json(NVD_CACHE_FILE) # Estructura: {"CVE-XXXX": 9.8}
    
    vulnerabilities = cisa_data.get('vulnerabilities', [])
    updated = False

    for v in vulnerabilities:
        cve_id = v['cveID']
        
        # Si no tenemos el score en el caché, lo buscamos
        if cve_id not in nvd_cache:
            print(f"Consultando NVD para {cve_id}...")
            try:
                time.sleep(6) # Respetar rate limit de NIST
                res = requests.get(f"{NVD_API_URL}{cve_id}", timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    metrics = data['vulnerabilities'][0]['cve'].get('metrics', {})
                    # Prioridad v4.0 -> v3.1
                    score = "N/A"
                    if 'cvssMetricV40' in metrics:
                        score = metrics['cvssMetricV40'][0]['cvssData']['baseScore']
                    elif 'cvssMetricV31' in metrics:
                        score = metrics['cvssMetricV31'][0]['cvssData']['baseScore']
                    
                    nvd_cache[cve_id] = score
                    updated = True
            except:
                continue

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Caché NVD actualizado.")

if __name__ == "__main__":
    update_nvd()