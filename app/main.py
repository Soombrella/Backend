from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.auth.router.auth_router import router as auth_router
from app.manage.router.manage_router import router as manage_router
from app.items.router.items_router import router as items_router
from app.personal.router.personal_router import router as personal_router
from app.admin.router.admin_router import router as admin_router
from app.db.database import engine, Base, get_db

# 모델 import (테이블 자동 생성용)
from app.rental.router.rental_router import router as rental_router
from app.reservation.router.reservation_router import router as reservation_router


app = FastAPI(
    title="Soombrella Backend API",
    version="0.1.0",
)

# CORS 설정
origins = [
    "http://localhost:3000",  # 프론트엔드 로컬 개발 서버
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(manage_router)
app.include_router(items_router)
app.include_router(personal_router)
app.include_router(rental_router)
app.include_router(reservation_router)
app.include_router(admin_router)


@app.get("/db-test", summary="DB 연결 테스트")
def db_test(db: Session = Depends(get_db)):
    try:
        # SQLAlchemy 2에서는 text()로 감싸주는 것이 안전함
        result = db.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        return {"tables": tables}
    except Exception as e:
        # 터미널에서 에러 원인 확인할 수 있도록 출력
        print("DB test error:", repr(e))
        raise HTTPException(status_code=500, detail="DB 연결 중 오류가 발생했습니다.")
