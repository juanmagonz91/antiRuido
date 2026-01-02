from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="The Signal Engine API")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "The Signal Engine",
        "database": "PostgreSQL + pgvector",
        "ai_provider": "Google Gemini 2.0 Flash"
    }

@app.get("/health")
def health_check():
    # Verifica si la API Key fue inyectada correctamente
    key_status = "Loaded" if os.getenv("GOOGLE_API_KEY") else "Missing"
    return {"api_key_status": key_status}
