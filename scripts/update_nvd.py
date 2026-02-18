import requests
import json
import os
import time
import sys

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
    # Intentamos NCSC-NL
    try:
        year = cve_id.split('-')[1]
        res = requests.get(f"https://vulnerabilities.ncsc.nl/csaf/v2/{year}/{cve_id.lower()}.json", timeout=5)
        if res.status_code == 200:
            for note in res.json().get('vulnerabilities', [{}])[0].get('notes', []):
                if "score" in note.get('title', '').lower(): return str(note.get('text'))
    except: pass
    # Fallback a CIRCL
    try:
        res = requests.get(f"https://cve.circl.lu/api/cve/{cve_id}", timeout=5)
        if res.status_code == 200:
            d = res.json()
            score = d.get('cvss3') or d.get('cvss')
            if isinstance(score, dict): score = score.get('baseScore')
            return str(score) if score else "N/A"
    except: pass
    return "N/A"

def update_nvd():
    # Miramos si pasamos el argumento '--full' al ejecutar el script
    full_scan = "--full" in sys.argv
    cisa_data = load_json(CISA_FILE)
    nvd_cache = load_json(NVD_CACHE_FILE)
    vulnerabilities = cisa_data.get('vulnerabilities', [])
    updated = False

    print(f"Modo: {'ESCANEO COMPLETO' if full_scan else 'MANTENIMIENTO RÁPIDO'}")

    for i, v in enumerate(vulnerabilities):
        cve_id = v['cveID']
        current = nvd_cache.get(cve_id, {})
        
        # Lógica de decisión:
        # 1. ¿No tiene score? -> Lo buscamos siempre.
        # 2. ¿Es de los 50 más nuevos? -> Lo re-escaneamos siempre.
        # 3. ¿Es escaneo completo (domingos)? -> Lo re-escaneamos todo.
        is_missing = not current or (isinstance(current, dict) and current.get('score') == "N/A")
        is_recent = i < 50
        
        if is_missing or is_recent or full_scan:
            old_score = current.get('score') if isinstance(current, dict) else None
            new_score = get_score(cve_id)
            
            if new_score != "N/A" and new_score != old_score:
                nvd_cache[cve_id] = {"score": new_score}
                updated = True
                print(f" -> {cve_id}: {new_score}")
                time.sleep(0.2)

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Datos actualizados correctamente.")

if __name__ == "__main__":
    update_nvd()