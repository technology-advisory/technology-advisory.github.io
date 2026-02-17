import requests
import json
import os

def update_cve_json():
    # URL oficial del catálogo KEV de CISA
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    
    # Definir la ruta de salida subiendo un nivel desde 'scripts/' hacia 'data/'
    # Esto asegura que funcione tanto en local como en GitHub Actions
    base_path = os.path.dirname(__file__)
    output_path = os.path.join(base_path, '..', 'data', 'cve.json')
    
    print(f"Iniciando actualización de inteligencia desde CISA...")

    try:
        # Realizar la petición a CISA
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Lanza error si la descarga falla
        
        data = response.json()
        
        # Extraer la lista de vulnerabilidades
        # CISA usa la clave "vulnerabilities"
        all_vulns = data.get('vulnerabilities', [])
        
        # Tomamos las 10 más recientes (suelen estar al final del documento)
        # Las invertimos para que la más nueva sea la primera de la lista
        latest_vulns = all_vulns[-10:]
        latest_vulns.reverse()

        # Creamos la estructura final que consumirá tu script.js
        final_structure = {
            "title": "CISA Export - Local Mirror",
            "last_update": data.get('dateReleased'),
            "vulnerabilities": latest_vulns
        }

        # Asegurar que la carpeta 'data' existe (por si acaso)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Guardar el archivo JSON formateado
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_structure, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Éxito: Se han guardado {len(latest_vulns)} vulnerabilidades en {output_path}")

    except Exception as e:
        print(f"❌ Error crítico durante la actualización: {e}")

if __name__ == "__main__":
    update_cve_json()