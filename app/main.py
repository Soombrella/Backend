from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import SessionLocal

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
