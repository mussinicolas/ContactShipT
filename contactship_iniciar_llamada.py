
import json
import os
from pathlib import Path

TOKKO_BASIC_PATH = Path(__file__).parent / "propiedades_basicas.json"

def cargar_lista_basica():
    if not TOKKO_BASIC_PATH.exists():
        print("⚠️ Archivo propiedades_basicas.json no encontrado.")
        return []
    with open(TOKKO_BASIC_PATH, "r", encoding="utf-8") as f:
        propiedades = json.load(f)
        print(f"✅ {len(propiedades)} propiedades cargadas desde archivo.")
        return propiedades

# Simula el uso inicial en una llamada de ContactShip
def iniciar_llamada_contactship():
    propiedades = cargar_lista_basica()
    if not propiedades:
        return
    # Simulamos usar la dirección para identificar una propiedad
    ejemplo_consulta = "Rivera 2799"
    coincidencias = [p for p in propiedades if ejemplo_consulta.lower() in p["direccion"].lower()]
    print(f"🔍 Coincidencias para '{ejemplo_consulta}':")
    for prop in coincidencias:
        print(f"- ID Tokko: {prop['id']} | Dirección: {prop['direccion']} | Precio USD: {prop['precio_usd']}")

if __name__ == "__main__":
    iniciar_llamada_contactship()