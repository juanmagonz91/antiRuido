import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Construimos la URL de conexión. 
# En Docker, el host es 'db', usuario 'user', pass 'password', db 'signal_engine'
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/signal_engine")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
