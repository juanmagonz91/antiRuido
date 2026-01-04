from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, func
from pgvector.sqlalchemy import Vector
from app.db.session import Base

class ContentHistory(Base):
    __tablename__ = "content_history"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(Text, nullable=False)
    title = Column(Text)
    
    # Resumen o snippet
    content_summary = Column(Text)
    
    # Métricas IA
    signal_score = Column(Float)
    is_signal = Column(Boolean)
    rejection_reason = Column(Text, nullable=True)
    category_code = Column(String(50))
    
    # Métricas de Tiempo
    estimated_read_time_seconds = Column(Integer)
    
    # Vector Semántico (Google = 768 dimensiones)
    embedding = Column(Vector(768))
    
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
