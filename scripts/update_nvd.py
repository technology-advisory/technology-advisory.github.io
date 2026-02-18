import requests
import json
import os
import time

CISA_FILE = "data/cve.json"
NVD_CACHE_FILE = "data/nvd_scores.json"

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

def get_score(cve_id):
    """Busca el score en NCSC (v4/v3) y CIRCL como respaldo"""
    try:
        year = cve_id.split('-')[1]
        # Fuente 1: NCSC-NL (CSAF) - Muy fiable para nuevos de 2026
        res = requests.get(f"https://vulnerabilities.ncsc.nl/csaf/v2/{year}/{cve_id.lower()}.json", timeout=5)
        if res.status_code == 200:
            data = res.json()
            for note in data.get('vulnerabilities', [{}])[0].get('notes', []):
                if "score" in note.get('title', '').lower():
                    return str(note.get('text'))
    except: pass

    try:
        # Fuente 2: CIRCL API
        res = requests.get(f"https://cve.circl.lu/api/cve/{cve_id}", timeout=5)
        if res.status_code == 200:
            d = res.json()
            score = d.get('cvss3') or d.get('cvss')
            if isinstance(score, dict): score = score.get('baseScore')
            return str(score) if score else "N/A"
    except: pass
    return "N/A"

def update_nvd():
    cisa_data = load_json(CISA_FILE)
    nvd_cache = load_json(NVD_CACHE_FILE)
    vulnerabilities = cisa_data.get('vulnerabilities', [])
    updated = False

    # Procesamos todos para asegurar que no hay huecos, 
    # pero solo pedimos a la API los que no tienen score
    for v in vulnerabilities:
        cve_id = v['cveID']
        current = nvd_cache.get(cve_id)
        
        # Si no existe, es un string "N/A" o un objeto con score "N/A"
        is_missing = not current or \
                     (isinstance(current, dict) and current.get('score') == "N/A") or \
                     current == "N/A"

        if is_missing:
            print(f"Buscando score para {cve_id}...")
            score = get_score(cve_id)
            if score != "N/A":
                nvd_cache[cve_id] = {"score": score}
                updated = True
                print(f" -> [OK] {score}")
                time.sleep(0.3) 

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Caché de severidad actualizado.")

if __name__ == "__main__":
    update_nvd()