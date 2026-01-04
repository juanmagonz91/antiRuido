from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.source_navigator import SourceNavigator
from app.services.content_scorer import ContentScorer
from app.services.embedding_service import EmbeddingService
from app.db.session import get_db, engine, Base
from app.db.models import ContentHistory

# Inicializar tablas si no existen (útil para desarrollo)
Base.metadata.create_all(bind=engine)

from pydantic import BaseModel

# DTO para el historial (lo que ve el usuario)
class HistoryItem(BaseModel):
    id: int
    title: Optional[str]
    url: str
    decision: str
    score: float
    time_saved: int
    date: str # O datetime

    class Config:
        from_attributes = True # Antes orm_mode

app = FastAPI(title="The Signal Engine API", version="0.2.0")

# Servicios
navigator = SourceNavigator()
scorer = ContentScorer()
vectorizer = EmbeddingService() # Nuevo servicio

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "The Signal Engine",
        "ai_model": "Google Gemini 2.0 Flash"
    }

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_url(
    request: AnalysisRequest, 
    db: Session = Depends(get_db)
):
    # 1. Navegación
    print(f"🔍 [1/3] Navegando: {request.url}")
    nav_result = await navigator.fetch_and_clean(str(request.url))
    
    if nav_result.get("status") != "success":
        raise HTTPException(status_code=400, detail=f"Error navegación: {nav_result.get('error')}")

    clean_text = nav_result.get("clean_text", "")
    if len(clean_text) < 50:
        raise HTTPException(status_code=422, detail="Contenido insuficiente para analizar.")

    # 2. Análisis (Cerebro)
    print("🧠 [2/3] Evaluando calidad...")
    ai_result = await scorer.analyze_content(
        content=clean_text[:15000], 
        topic=request.topic, 
        category=request.category
    )

    # 3. Embeddings (Memoria Semántica)
    print("🧬 [3/3] Generando vectores...")
    # Vectorizamos el resumen o los primeros párrafos, no todo el texto para ahorrar
    vector = await vectorizer.generate_embedding(clean_text[:2000])

    # 4. Persistencia
    try:
        db_entry = ContentHistory(
            source_url=str(request.url),
            title=nav_result.get("title"),
            content_summary=ai_result.get("analysis_reasoning"),
            signal_score=ai_result.get("quality_score"),
            is_signal=(ai_result.get("decision") == "SHOW"),
            rejection_reason=ai_result.get("analysis_reasoning") if ai_result.get("decision") == "BLOCK" else None,
            category_code=request.category,
            estimated_read_time_seconds=ai_result.get("estimated_read_time_seconds", 0),
            embedding=vector # Guardamos el array de floats
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        print(f"✅ Guardado en DB (ID: {db_entry.id})")
        
    except Exception as e:
        print(f"⚠️ Error DB: {e}")
        # Continuamos aunque falle el guardado para responder al usuario

    return AnalysisResponse(
        url=str(request.url),
        title=nav_result.get("title"),
        status="processed",
        quality_score=ai_result.get("quality_score", 0.0),
        decision=ai_result.get("decision", "BLOCK"),
        is_clickbait=ai_result.get("is_clickbait", False),
        reasoning=ai_result.get("analysis_reasoning", ""),
        estimated_read_time=ai_result.get("estimated_read_time_seconds", 0),
        clean_text_snippet=clean_text[:200]
    )

@app.get("/api/v1/history", response_model=List[HistoryItem])
def get_user_history(
    limit: int = 10, 
    decision: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """
    Recupera el historial de análisis. 
    Permite filtrar por decisión (SHOW/BLOCK).
    """
    query = db.query(ContentHistory)
    
    if decision:
        is_signal = (decision.upper() == "SHOW")
        query = query.filter(ContentHistory.is_signal == is_signal)
    
    # Ordenar por el más reciente
    results = query.order_by(desc(ContentHistory.id)).limit(limit).all()
    
    # Mapeo manual simple para formatear fecha (o usar Pydantic avanzado)
    response_list = []
    for item in results:
        response_list.append(HistoryItem(
            id=item.id,
            title=item.title or "Sin título",
            url=item.source_url,
            decision="SHOW" if item.is_signal else "BLOCK",
            score=float(item.signal_score) if item.signal_score is not None else 0.0,
            time_saved=item.estimated_read_time_seconds or 0,
            date=str(item.analyzed_at)
        ))
    
    return response_list

@app.get("/api/v1/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    KPIs para el Dashboard del usuario (Gráficos)
    """
    # 1. Total procesado
    total_count = db.query(ContentHistory).count()
    if total_count == 0:
        return {
            "total_items": 0,
            "blocked_items": 0,
            "noise_ratio": 0,
            "time_saved_minutes": 0,
            "digital_health_score": 0
        }
    
    # 2. Total Bloqueado (Ruido)
    blocked_count = db.query(ContentHistory).filter(ContentHistory.is_signal == False).count()
    
    # 3. Tiempo Ahorrado Total (Suma de segundos de contenido bloqueado)
    time_saved_seconds = db.query(func.sum(ContentHistory.estimated_read_time_seconds))\
        .filter(ContentHistory.is_signal == False)\
        .scalar() or 0
    
    # 4. Promedio de Calidad
    avg_quality = db.query(func.avg(ContentHistory.signal_score)).scalar() or 0.0

    return {
        "total_items": total_count,
        "blocked_items": blocked_count,
        "noise_ratio": round((blocked_count / total_count * 100), 1),
        "time_saved_minutes": int(time_saved_seconds / 60),
        "digital_health_score": round(float(avg_quality) * 10, 1) # Escala 0-10
    }
