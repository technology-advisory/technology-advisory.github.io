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

def get_data_from_circl(cve_id):
    """Obtiene score y datos básicos de CIRCL"""
    try:
        res = requests.get(f"https://cve.circl.lu/api/cve/{cve_id}", timeout=10)
        if res.status_code == 200:
            data = res.json()
            score = data.get('cvss3') or data.get('cvss')
            if isinstance(score, dict):
                score = score.get('baseScore') or score.get('score')
            return {"score": str(score) if score else "N/A"}
    except: return None

def get_data_from_ncsc(cve_id):
    """Extrae Score, Status y Exploited del formato CSAF del NCSC-NL"""
    try:
        year = cve_id.split('-')[1]
        url = f"https://vulnerabilities.ncsc.nl/csaf/v2/{year}/{cve_id.lower()}.json"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            vuln = data.get('vulnerabilities', [{}])[0]
            
            # 1. Buscar Score (CVSS v3.1)
            score = "N/A"
            for s in vuln.get('scores', []):
                cvss = s.get('cvss_v3', {}) or s.get('cvss_v4', {})
                if cvss.get('baseScore'):
                    score = str(cvss.get('baseScore'))
                    break
            
            # 2. Status & Exploited
            # El CSAF suele indicar el estatus en el tracking o notas
            status = data.get('document', {}).get('tracking', {}).get('status', 'unknown')
            
            return {
                "score": score,
                "status": status.upper(),
                "exploited": "YES" # Si está en este feed de vulnerabilidades, suele ser porque hay evidencia
            }
    except: return None

def update_nvd():
    cisa_data = load_json(CISA_FILE)
    nvd_cache = load_json(NVD_CACHE_FILE)
    vulnerabilities = cisa_data.get('vulnerabilities', [])
    updated = False

    for v in vulnerabilities[:40]:
        cve_id = v['cveID']
        # Si el dato es simple (antiguo) o no existe, actualizamos al nuevo formato
        current = nvd_cache.get(cve_id)
        if not isinstance(current, dict) or current.get('score') == "N/A":
            print(f"Capturando inteligencia completa para {cve_id}...")
            
            # Intentamos primero NCSC para tener Status/Exploited
            data = get_data_from_ncsc(cve_id)
            
            # Si falla, vamos a CIRCL por el score básico
            if not data or data['score'] == "N/A":
                circl_data = get_data_from_circl(cve_id)
                if circl_data:
                    data = {
                        "score": circl_data['score'],
                        "status": "CONFIRMED", # Default para CISA
                        "exploited": "YES"
                    }

            if data:
                nvd_cache[cve_id] = data
                updated = True
                print(f" -> [!] {cve_id}: {data['score']} | {data['status']} | {data['exploited']}")

    if updated:
        save_json(NVD_CACHE_FILE, nvd_cache)
        print("Base de datos de inteligencia actualizada.")

if __name__ == "__main__":
    update_nvd()