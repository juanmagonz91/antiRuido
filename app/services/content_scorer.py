import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.prompts import RUTHLESS_EDITOR_PROMPT

class ContentScorer:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
    
    async def analyze_content(self, content: str, topic: str, category: str) -> dict:
        """
        Analiza el contenido contra el Tópico y Categoría del usuario.
        """
        messages = [
            ("system", RUTHLESS_EDITOR_PROMPT),
            ("human", f"TÓPICO: {topic}\nCATEGORÍA: {category}\n\nCONTENIDO A ANALIZAR:\n{content}")
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            text_response = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(text_response)
        except Exception as e:
            print(f"Error en AI: {e}")
            return {
                "quality_score": 0.0,
                "decision": "BLOCK",
                "analysis_reasoning": f"Error de proceso: {str(e)}",
                "is_clickbait": False,
                "estimated_read_time_seconds": 0
            }
