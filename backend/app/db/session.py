from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://nexaro:nexaro@db:5432/nexaroai"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# 🔥 ESTA FUNCIÓN ES OBLIGATORIA
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()