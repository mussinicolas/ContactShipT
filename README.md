
# RolandoAI - Integración FastAPI + Tokko Broker

Este microservicio recibe una dirección desde un agente telefónico (por ejemplo, ContactShip) y responde con datos de una propiedad registrada en Tokko Broker. Guarda el contexto por número de teléfono para mantener continuidad de conversación.

## Uso

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecutar servidor:

```bash
uvicorn main:app --reload
```

3. Ejemplo de request:

```json
POST /consultar_propiedad
{
  "telefono": "+5491151193232",
  "direccion": "Aráoz 2150",
  "dato": "precio"
}
```
