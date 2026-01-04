-- 1. EXTENSIONES
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. USUARIOS
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- KPI Cache (Para no recalcular todo el tiempo)
    total_time_saved_minutes INTEGER DEFAULT 0,
    focus_score DECIMAL(3,2) DEFAULT 5.0
);

-- 3. TAXONOMÍA (Cerebro del sistema)
CREATE TABLE category_taxonomy (
    code VARCHAR(20) PRIMARY KEY, -- Usamos códigos de texto para facilitar lectura (ej: PROFESIONAL)
    name VARCHAR(100) NOT NULL,
    priority_level INTEGER, -- 1=Alta, 4=Bloquear
    description TEXT
);

-- DATOS SEMILLA (CRÍTICO)
INSERT INTO category_taxonomy (code, name, priority_level, description) VALUES
('PROFESIONAL', 'Crecimiento Profesional', 1, 'Papers, documentación, noticias de industria, tutoriales técnicos'),
('OCIO_SANO', 'Ocio Creativo/Salud', 2, 'Recetas, ejercicios, arte, gaming de estrategia'),
('NOTICIAS', 'Noticias Generales', 3, 'Actualidad verificada, clima, tráfico'),
('RUIDO', 'Basura Digital', 4, 'Chismes, polémicas, virales vacíos, clickbait');

-- 4. INTERESES DEL USUARIO
CREATE TABLE user_interests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    keyword VARCHAR(100),
    category_code VARCHAR(20) REFERENCES category_taxonomy(code),
    min_quality_threshold DECIMAL(3,2) DEFAULT 0.7, -- Qué tan estricto ser
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. FUENTES CONFIABLES (Whitelist)
CREATE TABLE trusted_sources (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(100) UNIQUE, -- ej: arxiv.org
    base_trust_score DECIMAL(3,2) DEFAULT 1.0
);

-- 6. HISTORIAL UNIFICADO (Contenido + Logs de Bloqueo)
CREATE TABLE content_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    source_url TEXT NOT NULL,
    title TEXT,
    content_summary TEXT,
    
    -- Métricas de Análisis IA
    signal_score DECIMAL(3,2), -- 0.00 a 1.00
    is_signal BOOLEAN,
    rejection_reason TEXT, -- NULL si fue aceptado
    category_code VARCHAR(20),
    
    -- Métricas de Tiempo
    estimated_read_time_seconds INTEGER, 
    time_saved_seconds INTEGER, -- Se llena solo si is_signal = FALSE
    
    -- Vector Search
    embedding vector(768),
    
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
