import os
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.prompts import RUTHLESS_EDITOR_PROMPT

# Configuración de Logging para ver cuándo ocurren los reintentos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentScorer:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
    
    # --- AQUÍ ESTÁ LA MAGIA DEL BACKOFF ---
    @retry(
        # 1. Espera Exponencial: 2s, 4s, 8s... hasta max 10s
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # 2. Rendirse después de 3 intentos (para no colgar al usuario eternamente)
        stop=stop_after_attempt(3),
        # 3. Loguear cada intento fallido
        before_sleep=lambda retry_state: logger.warning(f"⚠️ API saturada. Reintentando en {retry_state.next_action.sleep}s..."),
        # 4. Solo reintentar ante errores (RESOURCE_EXHAUSTED genera excepciones genéricas en este nivel)
        retry=retry_if_exception_type(Exception),
        reraise=True # Permite capturar el error final en el try/except de abajo
    )
    async def analyze_content(self, content: str, topic: str, category: str) -> dict:
        """
        Analiza el contenido con reintentos automáticos ante fallos de red/cuota.
        """
        messages = [
            ("system", RUTHLESS_EDITOR_PROMPT),
            ("human", f"TÓPICO: {topic}\nCATEGORÍA: {category}\n\nCONTENIDO A ANALIZAR:\n{content}")
        ]
        
        try:
            # Si esto falla por Rate Limit, @retry lo captura y espera
            response = await self.llm.ainvoke(messages)
            
            # Limpieza y Parseo JSON
            text_response = response.content
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0]
            elif "```" in text_response:
                text_response = text_response.replace("```", "")
                
            return json.loads(text_response.strip())

        except Exception as e:
            # Este bloque se ejecuta si se agotan todos los reintentos (o si falla el parseo)
            logger.error(f"❌ Scorer agotó reintentos o falló: {e}")
            return {
                "quality_score": 0.0,
                "decision": "BLOCK",
                "analysis_reasoning": "El servicio de IA está temporalmente no disponible (Rate Limit o Error de Proceso).",
                "is_clickbait": False,
                "estimated_read_time_seconds": 0
            }
