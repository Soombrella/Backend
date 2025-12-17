# Soombrella Backend

Soombrella 서비스의 백엔드 서버 레포지토리입니다.
FastAPI 기반의 API 서버를 제공하며, MySQL을 데이터베이스로 사용합니다.

개발 환경에서는 **Docker(MySQL) + FastAPI(API 서버)** 조합을 사용하며,
현재는 **AWS EC2 기반의 공용 개발 서버**를 함께 운영하고 있습니다.

---

## 1) 프로젝트 개요

Soombrella는 학생회 비품(우산, 보조배터리 등)의
**예약 · 대여 · 반납 · 보증금 관리**를 위한 서비스입니다.

본 레포지토리는 해당 서비스의 **백엔드 API 서버**를 담당합니다.

### 주요 기능

* 회원 관리 (일반 유저 / 관리자)
* 인증 및 계정 관련 처리
* 비품 및 카테고리 관리
* 예약 / 대여 / 반납 처리
* 보증금 및 환급 거래 내역 관리
* 프론트엔드 연동을 위한 REST API 제공

---

## 2) 기술 스택

* **FastAPI** – API 서버 프레임워크
* **SQLAlchemy** – ORM
* **MySQL 8** – 데이터베이스
* **Docker / Docker Compose** – DB 실행 및 환경 통일
* **Uvicorn** – ASGI 서버
* **Pydantic Settings** – 환경변수 관리

---

## 3) 개발 및 실행 환경 안내

### 3-1. 개발 환경 구조

* **DB**: Docker(MySQL)
* **API 서버**: FastAPI (로컬 또는 EC2)

> 프론트엔드는 기본적으로 **공용 개발 서버(API)** 를 사용하며,
> 백엔드 로컬 실행은 **백엔드 개발자 전용**입니다.

---

### 3-2. 환경변수 파일 설정

#### FastAPI 환경변수 (`.env`)

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.

```bash
cp .env.example .env
```

`.env` 파일에는 FastAPI 서버 실행에 필요한 설정 값만 작성합니다.

* DB 접속 정보
* JWT SECRET KEY
* 토큰 만료 시간 등

> `.env` 파일은 **Git에 커밋하지 않습니다.**

---

### 3-3. MySQL (Docker) 실행

Docker가 설치된 상태에서, 프로젝트 루트에서 실행합니다.

```bash
docker compose up -d
```

* MySQL 컨테이너가 백그라운드에서 실행됩니다.
* 최초 실행 시 DB 볼륨이 자동 생성됩니다.
* DB 스키마는 `schema.sql`을 기준으로 초기화됩니다.

---

### 3-4. FastAPI 서버 실행 (로컬)

가상환경 활성화 후 아래 명령어를 실행합니다.

```bash
uvicorn app.main:app --reload
```

* 기본 실행 주소:
  `http://127.0.0.1:8000`

---

## 4) 공용 개발 서버 (AWS EC2)

프론트엔드 연동을 위해 **공용 개발 서버**를 운영하고 있습니다.

* **Base URL**

  ```
  http://13.48.133.70:8000
  ```

* **Swagger UI**

  ```
  http://13.48.133.70:8000/docs
  ```

> 프론트엔드는 로컬 백엔드를 실행하지 않고
> **위 공용 서버만 사용**합니다.

---

## 5) API 문서

FastAPI에서 자동 생성되는 Swagger 문서를 제공합니다.

* 로컬 실행 시
  `http://127.0.0.1:8000/docs`

* 공용 개발 서버
  `http://13.48.133.70:8000/docs`

Swagger를 통해:

* API 목록 확인
* Request / Response 구조 확인
* 직접 API 테스트
  가 가능합니다.

---

## 6) DB Schema 관리 규칙 (중요)

### 6-1. 스키마 기준 파일

* DB 스키마의 **단일 기준 파일은 `schema.sql`입니다.**
* Docker로 DB를 초기화할 때, 항상 `schema.sql`을 기준으로 테이블이 생성됩니다.

---

### 6-2. 스키마 변경 시 반드시 해야 할 작업

로컬 개발 중 **테이블 추가 / 컬럼 변경 / 제약 조건 수정 등
DB 스키마 변경이 발생한 경우**, 아래 사항을 반드시 지켜야 합니다.

1. **로컬 DB 변경 사항을 `schema.sql`에 동일하게 반영**
2. 변경된 `schema.sql`을 커밋하여 PR에 포함
3. 스키마 변경 내용이 있음을 **팀원들에게 공유**

> `schema.sql`이 최신 상태가 아니면
> 다른 팀원의 로컬 DB / 서버 DB 구조가 어긋날 수 있습니다.

---

### 6-3. 스키마 변경 공유 예시

스키마 변경이 포함된 PR 또는 공유 시,
아래와 같이 **변경 요약을 함께 전달**합니다.

예시:

```
- auth_code 테이블 추가
- 인증 코드 저장을 위한 컬럼 반영
```

---

## 7) 팀원용 개발 가이드

### 7-1. 브랜치 전략

* `main`, `develop` 브랜치는 보호 브랜치입니다.
* 모든 작업은 **feature 브랜치**에서 진행합니다.

브랜치 예시:

* `feat/auth`
* `feat/item-crud`
* `feat/mysql-docker-setting`

---

### 7-2. 작업 시작 흐름

```bash
git checkout develop
git pull origin develop
git checkout -b feat/작업-이름
```

---

### 7-3. PR 규칙

* feature 브랜치 → develop 브랜치로 PR 생성
* 최소 1명 이상 리뷰 후 merge
* 직접 merge 및 force push 금지

---

### 7-4. 커밋 메시지 규칙 (권장)

* `feat:` 새로운 기능 추가
* `fix:` 버그 수정
* `refactor:` 리팩토링
* `docs:` 문서 수정
* `chore:` 설정 / 환경 관련 작업

예시:

```text
feat: add auth_code table
docs: update schema.sql after db change
chore: trim requirements.txt
```

---

## 8) 기타 유의 사항

* `.env`, `.env.docker` 파일은 **Git에 커밋하지 않습니다.**
* 서버 반영은 PR merge 후
  **EC2에서 pull → 의존성 설치 → 서버 재시작**으로 진행합니다.
* 스키마 변경이 포함된 경우, 반드시 팀에 변경 사항을 공유합니다.
