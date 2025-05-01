import os
import json
import urllib.parse
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKKO_API_TOKEN = "22541d3aea3d10b960e3f550d4bc20c2390a7dd3"

def direccion_contiene_numero(direccion_tokko, numero_cliente):
    import re
    numeros_en_direccion = re.findall(r"\d{2,5}", direccion_tokko)
    return str(numero_cliente) in numeros_en_direccion

def convert_words_to_numbers(texto):
    reemplazos_directos = {
        "mil novecientos": "1900",
        "mil ochocientos": "1800",
        "mil setecientos": "1700",
        "mil seiscientos": "1600",
        "mil quinientos": "1500"
    }
    for k, v in reemplazos_directos.items():
        texto = texto.lower().replace(k, v)

    num_map = {
        "cero": "0", "uno": "1", "dos": "2", "tres": "3", "cuatro": "4",
        "cinco": "5", "seis": "6", "siete": "7", "ocho": "8", "nueve": "9"
    }
    words = texto.split()
    resultado = []
    buffer_numeros = ""

    for word in words:
        if word in num_map:
            buffer_numeros += num_map[word]
        else:
            if buffer_numeros:
                resultado.append(buffer_numeros)
                buffer_numeros = ""
            resultado.append(word)

    if buffer_numeros:
        resultado.append(buffer_numeros)

    return ' '.join(resultado)

def extraer_dato_y_direccion(detalle):
    import re
    texto = convert_words_to_numbers(detalle.lower())
    if "precio" in texto or "vale" in texto or "cuánto" in texto:
        dato = "precio"
    elif "cochera" in texto or "garage" in texto:
        dato = "cochera"
    elif "ambiente" in texto:
        dato = "ambientes"
    elif "dormitorio" in texto or "habitación" in texto:
        dato = "dormitorios"
    elif "superficie" in texto or "metros" in texto:
        dato = "superficie"
    elif "asesor" in texto or "contacto" in texto or "productor" in texto:
        dato = "asesor"
    else:
        dato = "direccion"



 # Buscar dirección tipo "rivera 2799" (palabra seguida de número)
    import re
    m = re.search(r"([a-záéíóúñü]{3,})[^\d]{0,3}(\d{3,5})", texto)
    if m:
        direccion = f"{m.group(1)} {m.group(2)}"
    else:
        direccion = ""

    print(f"🧠 Dirección detectada: {direccion} | Dato: {dato}")
    return dato, direccion



@app.post("/consultar_propiedad")
async def consultar_propiedad(request: Request):
    try:
        data_raw = await request.json()

        print("📥 Payload recibido desde ContactShip:")
        print(json.dumps(data_raw, indent=2, ensure_ascii=False))

        args = data_raw.get("args", {})
        call = data_raw.get("call", {})

        telefono = (args.get("telefono") or call.get("call_id") or "").strip()
        ##telefono = (call.get("call_id") or "").strip()

        print(f"📞 Teléfono o ID detectado: {telefono}")

        detalle = (args.get("detalle") or "").strip()
        detalle = convert_words_to_numbers(detalle)

        dato, direccion_base = extraer_dato_y_direccion(detalle)

        # Extraer número de dirección (ej: 5010)
        import re
        match_numero = re.search(r"\d{3,5}", direccion_base)
        numero_buscado = match_numero.group(0) if match_numero else None


        # 👇 Nueva lógica: separar calle y número
        import re
        match = re.search(r"([a-záéíóúñü\s]+)\s(\d{3,5})", direccion_base.lower())
        if match:
            calle = match.group(1).strip()
            numero = match.group(2)
        else:
            calle = direccion_base.strip()
            numero = None

        print(f"📍 Dirección detectada: {direccion_base}")


        if not direccion_base:
            return {"respuesta": "¿Podés decirme la dirección que te interesa?"}

        filtro = {
            "current_localization_type": "country",
            "price_from": 0,
            "price_to": 99999999,
            "operation_types": [1, 2, 3],
            "property_types": [1, 2, 3, 4, 5, 6, 7],
##            "filters": [["address", "contains", direccion_base]]
            "filters": [["address", "contains", calle]]

        }
        data_param = urllib.parse.quote(json.dumps(filtro))
        url = f"https://www.tokkobroker.com/api/v1/property/search/?format=json&limit=1000&key={TOKKO_API_TOKEN}&data={data_param}"
        
        print("🔍 URL que se enviará a Tokko:")
        print(url)
        print("📤 Filtro JSON sin encode:")
        print(json.dumps(filtro, indent=2, ensure_ascii=False))

        print(f"🔗 URL consultada: {url}")

        res = requests.get(url)

        if res.status_code != 200:
            return {"respuesta": f"Error al consultar Tokko: {res.status_code} {res.text}"}


        # DEBUG: Mostrar resultado crudo para ver cuántas propiedades hay realmente
        res_json = res.json()
        print("🔍 Recuento bruto:", len(res_json.get("objects", [])))
        for i, obj in enumerate(res_json.get("objects", [])):
            print(f"🏡 Prop {i+1}: {obj.get('real_address')}")

        propiedades_raw = res_json.get("objects", [])

        propiedades_raw = res_json.get("objects", [])
        propiedades = []

        for p in propiedades_raw:
            direccion_completa = f"{p.get('real_address', '')} {p.get('address', '')} {p.get('fake_address', '')}".lower()

            if numero_buscado and not direccion_contiene_numero(direccion_completa, numero_buscado):
                print(f"❌ Descartada: {direccion_completa} – No contiene el número {numero_buscado}")
                continue

            print(f"✅ Incluida: {direccion_completa} – Contiene el número {numero_buscado}")

            tags = [t.get("name", "").lower() for t in p.get("tags", [])]
            apta_credito = any("apto credito" in t or "apt credit" in t for t in tags)
            apta_mascotas = any("mascota" in t or "pet" in t for t in tags)

            propiedades.append({
                "direccion": p.get("real_address", p.get("address", "")),
                "ambientes": p.get("room_amount", p.get("ambients")),
                "superficie_total": float(p.get("total_surface", 0)),
                "superficie_cubierta": float(p.get("roofed_surface", 0)),
                "precio_usd": next((pr.get("price") for op in p.get("operations", []) for pr in op.get("prices", []) if pr.get("currency") == "USD"), None),
                "expensas": p.get("expenses"),
                "baños": p.get("bathroom_amount"),
                "toilettes": p.get("toilet_amount"),
                "estado": "Muy bueno" if p.get("property_condition") == "Very good" else p.get("property_condition"),
                "apta_credito": apta_credito,
                "apta_mascotas": apta_mascotas,
                "ubicacion": f"{p.get('location', {}).get('name', '')} - Capital Federal",
                "productor": {
                    "nombre": p.get("producer", {}).get("name"),
                    "email": p.get("producer", {}).get("email"),
                    "telefono": p.get("producer", {}).get("cellphone")
                }
            })

        # 🔍 Esto va afuera del for:
        print(f"🔍 Cantidad de propiedades encontradas: {len(propiedades)}")

        return {
            "direccion_detectada": direccion_base,
            "dato_solicitado": dato,
            "cantidad_propiedades": len(propiedades),
            "propiedades": propiedades,
            "instrucciones_llm": "Solo respondé con el precio."
        }

@app.get("/descargar_propiedades")
def descargar_propiedades():
    try:
        url = f"https://www.tokkobroker.com/api/v1/property/search/?format=json&limit=1000&key={TOKKO_API_TOKEN}"
        res = requests.get(url)
        res.raise_for_status()

        data = res.json()
        propiedades = []

        for p in data.get("objects", []):
            propiedades.append({
                "id": p.get("id"),
                "direccion": p.get("real_address", ""),
                "address": p.get("address", ""),
                "fake_address": p.get("fake_address", ""),
                "barrio": p.get("location", {}).get("name", ""),
                "ambientes": p.get("room_amount", p.get("ambients")),
                "precio_usd": next((pr.get("price") for op in p.get("operations", []) for pr in op.get("prices", []) if pr.get("currency") == "USD"), None),
                "productor": {
                    "nombre": p.get("producer", {}).get("name"),
                    "email": p.get("producer", {}).get("email"),
                    "telefono": p.get("producer", {}).get("cellphone")
                }
            })

        with open("propiedades_basicas.json", "w", encoding="utf-8") as f:
            json.dump(propiedades, f, indent=2, ensure_ascii=False)

        return {"mensaje": f"✅ Se guardaron {len(propiedades)} propiedades en propiedades_basicas.json"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
