from fastapi import FastAPI
from app.api.routes import auth  # 👈 IMPORTANTE

app = FastAPI(title="NEXARO AI")

@app.get("/")
def root():
    return {"message": "NEXARO AI running"}

# 👇 ESTO ES LO QUE TE FALTA
app.include_router(auth.router, prefix="/auth", tags=["Auth"])