
import requests
import json
import urllib.parse

TOKKO_API_TOKEN = "22541d3aea3d10b960e3f550d4bc20c2390a7dd3"


def obtener_lista_basica_propiedades():
    filtro = {
        "current_localization_type": "country",
        "price_from": 0,
        "price_to": 99999999,
        "operation_types": [1, 2, 3],
        "property_types": [1, 2, 3, 4, 5, 6, 7]
    }
    data_param = urllib.parse.quote(json.dumps(filtro))
    url = f"https://www.tokkobroker.com/api/v1/property/search/?format=json&limit=1000&key={TOKKO_API_TOKEN}&data={data_param}"

    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"Error al consultar Tokko: {res.status_code} - {res.text}")

    propiedades_raw = res.json().get("objects", [])
    propiedades = []

    for p in propiedades_raw:
        propiedades.append({
            "id": p.get("id"),
            "titulo": p.get("publication_title"),
            "direccion": p.get("real_address", p.get("address", "")),
            "fake_address": p.get("fake_address"),
            "barrio": p.get("location", {}).get("name"),
            "ambientes": p.get("room_amount", p.get("ambients")),
            "precio_usd": next((pr.get("price") for op in p.get("operations", []) 
                                for pr in op.get("prices", []) if pr.get("currency") == "USD"), None),
            "productor": {
                "nombre": p.get("producer", {}).get("name"),
                "email": p.get("producer", {}).get("email"),
                "telefono": p.get("producer", {}).get("cellphone")
            }
        })

    with open("propiedades_basicas.json", "w", encoding="utf-8") as f:
        json.dump(propiedades, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(propiedades)} propiedades guardadas en propiedades_basicas.json")

if __name__ == "__main__":
    obtener_lista_basica_propiedades()
