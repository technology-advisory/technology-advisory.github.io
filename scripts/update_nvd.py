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

def get_data_from_ncsc(cve_id):
    """Extrae Inteligencia Real del CSAF del NCSC-NL"""
    try:
        year = cve_id.split('-')[1]
        url = f"https://vulnerabilities.ncsc.nl/csaf/v2/{year}/{cve_id.lower()}.json"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            vuln = data.get('vulnerabilities', [{}])[0]
            
            # 1. Búsqueda de Score (Prioridad CVSS v4 > v3 > v2)
            score = "N/A"
            # Buscamos en las notas el 'CVSSV4 base score' que vimos en tu archivo (9.9)
            for note in vuln.get('notes', []):
                if note.get('title') == "CVSSV4 base score":
                    score = str(note.get('text'))
                    break
            
            # Si no hay v4, buscamos en el array de scores normal
            if score == "N/A":
                for s in vuln.get('scores', []):
                    cvss = s.get('cvss_v3', {}) or s.get('cvss_v4', {})
                    if cvss.get('baseScore'):
                        score = str(cvss.get('baseScore'))
                        break

            # 2. Captura de STATUS (del tracking del documento)
            # Puede ser: interim, final, draft...
            doc_status = data.get('document', {}).get('tracking', {}).get('status', 'unknown')

            # 3. EXPLOITED (Buscamos si hay mención a explotación activa)
            exploited = "NO"
            for note in vuln.get('notes', []):
                if "exploit data available" in note.get('text', '').lower():
                    exploited = "YES"
                    break

            return {
                "score": score,
                "status": doc_status.upper(),
                "exploited": exploited
            }
    except: return None

def update_nvd():
    cisa_data = load_json(CISA_FILE)
    nvd_cache = load_json(NVD_CACHE_FILE)
    vulnerabilities = cisa_data.get('vulnerabilities', [])
    updated = False

    # Analizamos los 40 más recientes
    for v in vulnerabilities[:40]:
        cve_id = v['cveID']
        
        # Siempre intentamos actualizar si el dato no es un objeto completo
        # o si el status es 'unknown'
        current = nvd_cache.get(cve_id, {})
        if not isinstance(current, dict) or current.get('status') in [None, "UNKNOWN", "N/A"]:
            print(f"Investigando {cve_id}...")
            
            data = get_data_from_ncsc(cve_id)
            
            if data:
                nvd_cache[cve_id] = data
                updated = True
                print(f" -> Encontrado: {data['score']} | Status: {data['status']} | Exploit: {data['exploited']}")

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Inteligencia CSAF sincronizada.")

if __name__ == "__main__":
    update_nvd()