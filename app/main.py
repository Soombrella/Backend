from fastapi import FastAPI
from app.api.auth_router import router as auth_router
from app.database import engine, Base

app = FastAPI(
    title="Soombrella Backend API",
    version="0.1.0",
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/hello")
def say_hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}
