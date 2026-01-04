import httpx
import asyncio
import json

async def test_analyze():
    url = "http://localhost:8000/api/v1/analyze"
    payload = {
        "url": "https://en.wikipedia.org/wiki/Large_language_model",
        "topic": "Modelos de lenguaje extensos y su arquitectura",
        "category": "PROFESIONAL"
    }
    
    print(f"🚀 Enviando petición a {url}...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("✅ Respuesta recibida con éxito:")
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            else:
                print(f"❌ Error en la respuesta: {response.text}")
        except Exception as e:
            print(f"🔥 Error conectando con el servidor: {e}")

if __name__ == "__main__":
    asyncio.run(test_analyze())
