import requests
import json
import os
import time

CISA_FILE = "data/cve.json"
NVD_CACHE_FILE = "data/nvd_scores.json"
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

    # Seleccionamos los 40 más recientes
    recent_vulnerabilities = vulnerabilities[:40]

    for v in recent_vulnerabilities:
        cve_id = v['cveID']
        
        # SI el score no existe O es "N/A", intentamos buscarlo de nuevo
        current_score = nvd_cache.get(cve_id)
        if not current_score or current_score == "N/A":
            print(f"Buscando score real para {cve_id}...")
            try:
                time.sleep(1) # Respetamos el límite de la API
                res = requests.get(f"{API_URL}{cve_id}", timeout=10)
                
                if res.status_code == 200:
                    data = res.json()
                    # Extraemos el score probando varios campos (v3, v2, o base)
                    score = data.get('cvss3') or data.get('cvss')
                    
                    if isinstance(score, dict):
                        score = score.get('baseScore') or score.get('score')
                    
                    if score:
                        nvd_cache[cve_id] = str(score)
                        updated = True
                        print(f" -> [OK] {cve_id}: {score}")
                    else:
                        nvd_cache[cve_id] = "N/A"
                else:
                    nvd_cache[cve_id] = "N/A"
            except:
                nvd_cache[cve_id] = "N/A"

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("nvd_scores.json actualizado con nuevos valores.")
    else:
        print("No se encontraron nuevos scores para actualizar.")

if __name__ == "__main__":
    update_nvd()