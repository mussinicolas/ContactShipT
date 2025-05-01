
from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/consultar_propiedad")
async def consultar_propiedad(request: Request):
    try:
        data_raw = await request.json()
        print("📦 JSON completo recibido:", json.dumps(data_raw, indent=2, ensure_ascii=False))
        data = data_raw.get("args", {})
        telefono = (data.get("telefono") or "").strip()
        direccion_base = (data.get("direccion") or "").strip() or None
        dato = (data.get("dato") or "").strip().lower() or None
        detalle = (data.get("detalle") or "").strip()
        return {"respuesta": f"Recibido: Tel={telefono}, Detalle={detalle}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
