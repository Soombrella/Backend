# Soombrella Backend

Soombrella 서비스의 백엔드 서버 레포지토리입니다.
FastAPI 기반으로 API 서버를 구성하고, MySQL을 데이터베이스로 사용합니다.
로컬 개발 환경에서는 **Docker(MySQL) + 로컬(FastAPI)** 조합을 기본으로 합니다.

---

## 1) 프로젝트 개요

Soombrella는 학생회 비품(우산, 보조배터리 등) 대여/예약을 관리하기 위한 서비스입니다.
본 레포지토리는 해당 서비스의 **백엔드 API 서버**를 담당합니다.

주요 역할은 다음과 같습니다.

* 회원 관리
* 비품 및 카테고리 관리
* 예약 / 대여 / 반납 처리
* 보증금 거래 내역 관리
* API 제공 및 DB 연동

---

## 2) 기술 스택

* **FastAPI** – API 서버 프레임워크
* **SQLAlchemy** – ORM
* **MySQL 8** – 데이터베이스
* **Docker / Docker Compose** – 로컬 DB 환경 통일
* **Uvicorn** – ASGI 서버
* **Pydantic Settings** – 환경변수 관리

---

## 3) 로컬 개발환경 실행 방법

### 3-1. 환경변수 파일 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.

* macOS / Linux
  `cp .env.example .env`

* Windows
  `copy .env.example .env`

`.env` 파일에는 **FastAPI 서버에서 사용하는 설정 값**만 작성합니다.
(DB 접속 정보, SECRET_KEY 등)

> 실제 값은 로컬 환경에 맞게 설정해야 합니다.

---

### 3-2. MySQL (Docker) 실행

Docker가 설치되어 있는 상태에서, 프로젝트 루트에서 실행합니다.

```bash
docker compose up -d
```

* MySQL 컨테이너가 백그라운드에서 실행됩니다.
* 최초 실행 시 DB 볼륨이 자동 생성됩니다.

---

### 3-3. FastAPI 서버 실행

가상환경 활성화 후 아래 명령어를 실행합니다.

```bash
uvicorn app.main:app --reload
```

* 기본 실행 주소: `http://127.0.0.1:8000`

---

## 4) API 문서 경로

FastAPI에서 자동 생성되는 Swagger 문서를 제공합니다.

* Swagger UI:
  `http://127.0.0.1:8000/docs`

API 테스트 및 요청/응답 구조 확인은 위 경로를 통해 진행합니다.

---

## 5) DB Schema 설명

데이터베이스 스키마는 다음 엔티티들을 포함합니다.

* member (회원)
* item_category (비품 카테고리)
* item (비품)
* reservation (예약)
* rental (대여/반납)
* deposit_txn (보증금 거래)
* bank_account (환급 계좌)

스키마 정의 파일:

* `schema.sql`

ERD는 dbdiagram을 사용하여 관리합니다.
(링크는 팀 내부 문서 또는 노션에서 공유)

---

## 6) 팀원용 개발 가이드

### 6-1. 브랜치 전략

* `main` / `develop` 브랜치는 보호 브랜치로 직접 작업하지 않습니다.
* 모든 작업은 **feature 브랜치**에서 진행합니다.

브랜치 예시:

* `feat/mysql-docker-setting`
* `feat/auth`
* `feat/item-crud`

---

### 6-2. 작업 시작 흐름

```bash
git checkout develop
git pull origin develop
git checkout -b feat/작업-이름
```

---

### 6-3. PR 규칙

* feature 브랜치 → develop 브랜치로 PR 생성
* 최소 1명 이상 리뷰 후 merge
* 직접 merge / force push 금지

---

### 6-4. 커밋 메시지 규칙 (권장)

* `feat:` 새로운 기능 추가
* `fix:` 버그 수정
* `refactor:` 리팩토링
* `docs:` 문서 수정
* `chore:` 설정/환경 관련 작업

예시:

```text
feat: add mysql docker configuration
fix: resolve database connection error
docs: update backend setup guide
```