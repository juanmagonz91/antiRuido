import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class EmbeddingService:
    def __init__(self):
        # Usamos el modelo optimizado de Google (768 dimensiones)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    async def generate_embedding(self, text: str):
        try:
            # Google recomienda no enviar textos masivos de golpe para embeddings
            # Recortamos a caracteres razonables para el contexto semántico
            truncated_text = text[:10000] 
            vector = await self.embeddings.aembed_query(truncated_text)
            return vector
        except Exception as e:
            print(f"⚠️ Error generando embedding: {e}")
            return None
