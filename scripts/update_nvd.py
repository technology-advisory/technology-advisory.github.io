import requests
import json
import os
import time

CISA_FILE = "data/cve.json"
NVD_CACHE_FILE = "data/nvd_scores.json"
# Usaremos CIRCL como fuente principal pero con búsqueda mejorada
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

    # Filtramos los que tienen N/A para intentar recuperarlos hoy
    to_update = [v for v in vulnerabilities[:40] if nvd_cache.get(v['cveID']) == "N/A" or v['cveID'] not in nvd_cache]

    for v in to_update:
        cve_id = v['cveID']
        print(f"Intentando recuperar score para {cve_id}...")
        try:
            time.sleep(1) # Pausa para evitar bloqueos
            res = requests.get(f"{API_URL}{cve_id}", timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                # Buscamos en todas las posibles ubicaciones del score (v3.1, v3.0, v2)
                score = data.get('cvss3') or data.get('cvss') or data.get('cvss-vector')
                
                # Si CIRCL devuelve un objeto complejo, extraemos solo el número
                if isinstance(score, dict):
                    score = score.get('baseScore') or score.get('score')
                
                if score and score != "N/A":
                    nvd_cache[cve_id] = str(score)
                    updated = True
                    print(f" -> ¡Éxito! Score: {score}")
                else:
                    print(f" -> Sigue sin score en esta fuente.")
        except Exception as e:
            print(f" -> Error con {cve_id}: {e}")

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Archivo de severidad actualizado con nuevos datos.")
    else:
        print("No se han encontrado nuevos scores en esta pasada.")

if __name__ == "__main__":
    update_nvd()