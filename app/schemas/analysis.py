from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Literal

# Lo que el usuario (o la app móvil) envía
class AnalysisRequest(BaseModel):
    url: HttpUrl
    topic: str = Field(..., description="El tema de interés del usuario (ej: Python, Economía)")
    category: Literal["PROFESIONAL", "OCIO_SANO", "NOTICIAS", "RUIDO"] = Field(..., description="Categoría taxonómica")
    
# Lo que devolvemos (Estructura unificada)
class AnalysisResponse(BaseModel):
    url: str
    title: str
    status: str
    quality_score: float
    decision: Literal["SHOW", "BLOCK"]
    is_clickbait: bool
    reasoning: str
    estimated_read_time: int
    clean_text_snippet: Optional[str] = None # Para debug o previsualización
