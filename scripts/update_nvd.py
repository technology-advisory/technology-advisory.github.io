import requests
import json
import os
import time

CISA_FILE = "data/cve.json"
NVD_CACHE_FILE = "data/nvd_scores.json"
# Esta API es el espejo de GCVE y es muy rápida
API_URL = "https://cve.circl.lu/api/cve/"

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
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

    # Procesamos solo los 30 más recientes para que el Action vuele
    for v in vulnerabilities[:30]:
        cve_id = v['cveID']
        
        if cve_id not in nvd_cache or nvd_cache[cve_id] == "N/A":
            print(f"Obteniendo severidad para {cve_id}...")
            try:
                time.sleep(0.5) 
                res = requests.get(f"{API_URL}{cve_id}", timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    # CIRCL guarda el score en cvss3 o cvss
                    score = data.get('cvss3') or data.get('cvss') or "N/A"
                    nvd_cache[cve_id] = score
                    updated = True
            except:
                continue

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Caché actualizado.")

if __name__ == "__main__":
    update_nvd()