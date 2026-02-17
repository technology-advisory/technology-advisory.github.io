import requests
import json
import os

def update_cve_json():
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    base_path = os.path.dirname(__file__)
    output_path = os.path.join(base_path, '..', 'data', 'cve.json')

    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        all_vulns = data.get('vulnerabilities', [])

        # ORDENAR: Las más nuevas según la fecha en que CISA las publicó (dateAdded)
        # Usamos reverse=True para que las más recientes queden arriba
        sorted_vulns = sorted(all_vulns, key=lambda x: x['dateAdded'], reverse=True)

        # Ahora sí, tomamos las 10 que realmente son las más recientes en el tiempo
        latest_vulns = sorted_vulns[:10]

        final_structure = {
            "title": "CISA Intelligence Dashboard",
            "last_update_check": data.get('dateReleased'),
            "vulnerabilities": latest_vulns
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_structure, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Éxito: Se han guardado las 10 vulnerabilidades más recientes por fecha.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_cve_json()