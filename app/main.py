from fastapi import FastAPI

app = FastAPI(
    title="FocusDash Backend API",
    version="0.1.0",
)

# 헬스체크용 엔드포인트
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 테스트용 간단 엔드포인트
@app.get("/hello")
def say_hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}
