# 명월헌 사주사이트 아키텍처 문서

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [현재 구조 (Before)](#현재-구조-before)
3. [개선된 구조 (After)](#개선된-구조-after)
4. [백엔드 아키텍처](#백엔드-아키텍처)
5. [프론트엔드 아키텍처](#프론트엔드-아키텍처)
6. [마이그레이션 가이드](#마이그레이션-가이드)

---

## 프로젝트 개요

**명월헌**은 AI 기반 사주팔자 운세 서비스 웹 애플리케이션입니다.

### 기술 스택
- **백엔드**: FastAPI (Python 3.11)
- **데이터베이스**: SQLite (SQLAlchemy ORM)
- **템플릿 엔진**: Jinja2
- **AI**: Google Gemini API
- **프론트엔드**: Vanilla JavaScript, CSS
- **배포**: Uvicorn (ASGI)

### 주요 서비스
1. 오늘의 운세 (`today`)
2. 정통 사주팔자 (`saju`)
3. 사주 궁합 (`match`)
4. 꿈해몽 (`dream`)
5. 2026년 신년운세 (`newyear2026`)
6. 타로 (`taro`)

---

## 현재 구조 (Before)

### 문제점
```
c:\사주사이트\
├── 루트 디렉토리가 너무 복잡함 ❌
│   ├── add_result_url_path_column.py
│   ├── add_url_path_column.py
│   ├── check_services.py
│   ├── create_individual_pages.py
│   ├── migrate_*.py (4개)
│   ├── reset_admin.py
│   ├── test_gemini.py
│   └── update_*.py (2개)
│
├── app/
│   └── templates/
│       ├── fortune/      (시작 페이지) ⚠️
│       ├── public/       (결과 페이지 + 메인) ⚠️
│       └── layout/       (공용 레이아웃) ✅
```

**주요 문제:**
1. **루트에 관리 스크립트 12개 산재** → 관리 어려움
2. **템플릿 구조 혼란** → `fortune/`과 `public/`의 역할이 불분명
3. **문서 부재** → 신규 개발자 온보딩 어려움

---

## 개선된 구조 (After)

```
c:\사주사이트\
│
├── app/                          # 백엔드 애플리케이션
│   ├── models/                   # 데이터베이스 모델
│   │   ├── __init__.py
│   │   ├── admin_user.py         # 관리자 계정
│   │   ├── fortune_result.py     # 운세 결과 캐시
│   │   ├── service_config.py     # 서비스 설정
│   │   └── site_config.py        # 사이트 전역 설정
│   │
│   ├── routers/                  # API 라우터 (MVC의 Controller)
│   │   ├── __init__.py
│   │   ├── fortune.py            # 공개 운세 서비스
│   │   └── admin/                # 관리자 전용
│   │       ├── __init__.py
│   │       ├── auth.py           # 로그인/로그아웃
│   │       └── dashboard.py      # 대시보드/설정
│   │
│   ├── services/                 # 비즈니스 로직 (MVC의 Model)
│   │   ├── __init__.py
│   │   ├── auth_service.py       # 인증 로직
│   │   ├── fortune_service.py    # 운세 생성 로직
│   │   ├── gemini_service.py     # AI API 호출
│   │   ├── saju_calculator.py    # 사주 계산 엔진
│   │   └── site_service.py       # 사이트 설정 관리
│   │
│   ├── schemas/                  # Pydantic 스키마 (데이터 검증)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── fortune.py
│   │   ├── service_config.py
│   │   └── site_config.py
│   │
│   ├── utils/                    # 유틸리티 함수
│   │   ├── __init__.py
│   │   ├── hashing.py            # 비밀번호 해싱
│   │   ├── image_utils.py        # 이미지 처리
│   │   └── security.py           # 보안 관련
│   │
│   ├── static/                   # 정적 파일
│   │   ├── css/
│   │   │   ├── main.css          # 공용 스타일
│   │   │   └── admin/            # 관리자 전용 스타일
│   │   │       ├── variables.css
│   │   │       ├── layout.css
│   │   │       ├── forms.css
│   │   │       ├── components.css
│   │   │       └── sidebar.css
│   │   ├── js/
│   │   │   ├── main.js           # 공용 스크립트
│   │   │   └── admin/            # 관리자 전용 스크립트
│   │   │       ├── alerts.js
│   │   │       ├── image-preview.js
│   │   │       ├── tabs.js
│   │   │       └── utils.js
│   │   └── uploads/              # 업로드된 미디어 파일
│   │
│   ├── templates/                # HTML 템플릿
│   │   ├── layout/               # 공용 레이아웃
│   │   │   ├── base.html         # 공개 사이트 기본 레이아웃
│   │   │   └── admin_base.html   # 관리자 기본 레이아웃
│   │   │
│   │   ├── pages/                # 🆕 시작 페이지 (fortune/ → pages/)
│   │   │   ├── today.html        # 오늘의 운세 입력 폼
│   │   │   ├── saju.html         # 사주팔자 입력 폼
│   │   │   ├── match.html        # 궁합 입력 폼
│   │   │   ├── dream.html        # 꿈해몽 입력 폼
│   │   │   ├── newyear2026.html  # 신년운세 입력 폼
│   │   │   └── taro.html         # 타로 입력 폼
│   │   │
│   │   ├── results/              # 🆕 결과 페이지 (public/ → results/)
│   │   │   ├── today_result.html
│   │   │   ├── saju_result.html
│   │   │   ├── match_result.html
│   │   │   ├── dream_result.html
│   │   │   ├── newyear2026_result.html
│   │   │   ├── index.html        # 메인 페이지
│   │   │   └── error.html        # 오류 페이지
│   │   │
│   │   └── admin/                # 관리자 페이지
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── settings_site.html
│   │       ├── settings_services.html
│   │       ├── settings_pages.html
│   │       └── settings_seo.html
│   │
│   ├── config.py                 # 설정 파일
│   ├── database.py               # DB 연결 설정
│   ├── init_db.py                # DB 초기화
│   └── main.py                   # FastAPI 앱 엔트리포인트
│
├── scripts/                      # 🆕 관리/마이그레이션 스크립트
│   ├── migrations/               # DB 마이그레이션
│   │   ├── add_url_path_column.py
│   │   ├── add_result_url_path_column.py
│   │   ├── migrate_add_banner_pc.py
│   │   ├── migrate_add_logo.py
│   │   ├── migrate_character_form_image.py
│   │   └── migrate_character_image.py
│   ├── admin/                    # 관리 스크립트
│   │   └── reset_admin.py
│   └── dev/                      # 개발/테스트 스크립트
│       ├── check_services.py
│       ├── test_gemini.py
│       ├── update_site_config.py
│       └── update_newyear_code.py
│
├── docs/                         # 🆕 문서
│   └── ARCHITECTURE.md           # 이 문서
│
├── .vscode/                      # VSCode 설정
│   └── settings.json             # Jinja2 템플릿 인식 설정
│
├── requirements.txt              # Python 패키지 의존성
├── README.md                     # 프로젝트 소개
└── myeongwolheon.db              # SQLite 데이터베이스
```

---

## 백엔드 아키텍처

### 1. MVC 패턴

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Router    │─────▶│   Service    │─────▶│    Model    │
│ (Controller)│      │  (Business)  │      │   (Data)    │
└─────────────┘      └──────────────┘      └─────────────┘
      │                     │                      │
      │                     │                      │
      ▼                     ▼                      ▼
  Templates            Gemini API            Database
```

### 2. 데이터 흐름

**운세 생성 요청 예시:**

```
1. 사용자 → /fortune/saju (POST)
   ↓
2. fortune.py (Router)
   ├─ 입력 검증 (birthdate, gender 필수)
   ├─ SiteService: 서비스 설정 조회
   └─ FortuneService.get_or_create_fortune()
      ↓
3. fortune_service.py
   ├─ 캐시 확인 (DB에서 동일 요청 검색)
   ├─ 캐시 없으면 → 새로 생성
   │  ├─ SajuCalculator: 사주 계산
   │  └─ GeminiService: AI 해석 생성
   └─ 결과 반환
      ↓
4. Router
   └─ results/saju_result.html 렌더링
```

### 3. 주요 서비스 클래스

| 클래스 | 역할 | 주요 메서드 |
|--------|------|-------------|
| `FortuneService` | 운세 생성 총괄 | `get_or_create_fortune()` |
| `GeminiService` | AI API 호출 | `generate_fortune()` |
| `SajuCalculator` | 사주 계산 | `calculate_saju()` |
| `SiteService` | 사이트 설정 관리 | `get_site_config()` |
| `AuthService` | 인증 처리 | `verify_password()` |

---

## 프론트엔드 아키텍처

### 1. CSS 구조

```
static/css/
├── main.css                      # 공용 스타일
│   ├─ CSS Variables (색상, 폰트 등)
│   ├─ 공통 컴포넌트 (버튼, 카드 등)
│   └─ 반응형 레이아웃
│
└── admin/                        # 관리자 전용 (모듈화)
    ├── variables.css             # 관리자 색상 변수
    ├── layout.css                # 그리드 레이아웃
    ├── sidebar.css               # 사이드바
    ├── forms.css                 # 폼 요소
    └── components.css            # 버튼, 알림 등
```

### 2. JavaScript 구조

```
static/js/
├── main.js                       # 공용 스크립트
│   ├─ 전역 유틸리티 함수
│   └─ 공통 이벤트 리스너
│
└── admin/                        # 관리자 전용 (모듈화)
    ├── utils.js                  # 유틸리티
    ├── alerts.js                 # 알림창
    ├── tabs.js                   # 탭 네비게이션
    └── image-preview.js          # 이미지 미리보기
```

### 3. 템플릿 상속 구조

```
┌─────────────────────────────────┐
│      layout/base.html           │  ← 최상위 레이아웃
│  (공통 헤더, 푸터, 메타 태그)   │
└─────────────────────────────────┘
              ▲
              │ extends
              │
    ┌─────────┴─────────┐
    │                   │
┌───┴────┐      ┌──────┴─────┐
│ pages/ │      │  results/  │
│        │      │            │
│ today  │      │ today      │
│ saju   │      │ saju       │
│ match  │      │ match      │
│ dream  │      │ dream      │
│ ...    │      │ ...        │
└────────┘      └────────────┘
```

**상속 예시:**
```jinja2
{% extends "layout/base.html" %}

{% block title %}오늘의 운세{% endblock %}

{% block content %}
  <!-- 페이지별 고유 컨텐츠 -->
{% endblock %}
```

---

## 마이그레이션 가이드

### 단계별 작업 계획

#### ✅ 1단계: scripts/ 폴더 생성 및 파일 정리
```bash
# 1. scripts/ 디렉토리 구조 생성
mkdir -p scripts/migrations
mkdir -p scripts/admin
mkdir -p scripts/dev

# 2. 마이그레이션 스크립트 이동
move add_url_path_column.py scripts/migrations/
move add_result_url_path_column.py scripts/migrations/
move migrate_*.py scripts/migrations/

# 3. 관리 스크립트 이동
move reset_admin.py scripts/admin/

# 4. 개발 스크립트 이동
move check_services.py scripts/dev/
move test_gemini.py scripts/dev/
move update_*.py scripts/dev/
move create_individual_pages.py scripts/dev/
```

#### ⏳ 2단계: templates/ 구조 개선
```bash
# 1. 새 디렉토리 생성
mkdir app/templates/pages
mkdir app/templates/results

# 2. 시작 페이지 이동 (fortune/ → pages/)
move app/templates/fortune/*.html app/templates/pages/

# 3. 결과 페이지 이동 (public/ → results/)
move app/templates/public/*.html app/templates/results/

# 4. 빈 폴더 삭제
rmdir app/templates/fortune
rmdir app/templates/public
```

#### ⏳ 3단계: 라우터 코드 업데이트

**변경 전 (`app/routers/fortune.py`):**
```python
template_name = f"fortune/{service_code}.html"
template_name = f"public/{service_code}_result.html"
```

**변경 후:**
```python
template_name = f"pages/{service_code}.html"
template_name = f"results/{service_code}_result.html"
```

#### ⏳ 4단계: 관리자 라우터 업데이트

**변경 전 (`app/routers/admin/dashboard.py`):**
```python
return templates.TemplateResponse("public/index.html", ...)
```

**변경 후:**
```python
return templates.TemplateResponse("results/index.html", ...)
```

#### ⏳ 5단계: 테스트

1. 서버 재시작
2. 모든 페이지 접속 테스트:
   - `/` (메인)
   - `/fortune/today` (오늘의 운세)
   - `/fortune/saju` (사주팔자)
   - `/fortune/match` (궁합)
   - `/fortune/dream` (꿈해몽)
   - `/fortune/newyear2026` (신년운세)
   - `/admin/login` (관리자 로그인)

---

## 디렉토리별 설명

### `/app/models/` - 데이터베이스 모델
SQLAlchemy ORM 모델 정의. 각 파일은 하나의 테이블을 담당.

### `/app/routers/` - API 라우터
FastAPI 라우터. URL 엔드포인트와 요청 처리 로직.

### `/app/services/` - 비즈니스 로직
순수 비즈니스 로직. 재사용 가능하고 테스트 가능.

### `/app/schemas/` - 데이터 검증
Pydantic 스키마. API 입출력 데이터 검증 및 직렬화.

### `/app/templates/` - HTML 템플릿
Jinja2 템플릿. SSR(Server-Side Rendering) 방식.

### `/scripts/` - 관리 스크립트
DB 마이그레이션, 관리 작업, 개발 도구.

---

## 명명 규칙

### 파일/폴더
- **소문자 + 언더스코어**: `fortune_service.py`
- **복수형**: `templates/`, `models/`, `scripts/`

### Python
- **클래스**: PascalCase (`FortuneService`)
- **함수/변수**: snake_case (`get_fortune()`)
- **상수**: UPPER_CASE (`API_KEY`)

### HTML/CSS
- **클래스**: kebab-case (`.fortune-header`)
- **ID**: camelCase (`#loadingOverlay`)

---

## 개발 워크플로우

### 1. 새 서비스 추가하기

1. **모델 생성** (`app/models/`)
2. **스키마 정의** (`app/schemas/`)
3. **서비스 로직 작성** (`app/services/`)
4. **라우터 추가** (`app/routers/`)
5. **템플릿 작성** (`app/templates/pages/`, `app/templates/results/`)

### 2. DB 마이그레이션

```bash
# 1. 마이그레이션 스크립트 작성
# scripts/migrations/add_new_column.py

# 2. 실행
python scripts/migrations/add_new_column.py
```

### 3. 관리자 계정 리셋

```bash
python scripts/admin/reset_admin.py
```

---

## 보안 고려사항

1. **비밀번호 해싱**: bcrypt 사용
2. **환경 변수**: API 키는 환경 변수로 관리
3. **CORS**: 필요시 FastAPI CORS 미들웨어 추가
4. **SQL Injection**: SQLAlchemy ORM 사용으로 방어
5. **XSS**: Jinja2 자동 이스케이프

---

## 성능 최적화

1. **캐싱**: 동일 요청은 DB 캐시 활용
2. **정적 파일**: CDN 사용 고려
3. **이미지 최적화**: WebP 포맷 사용
4. **DB 인덱싱**: 자주 조회하는 컬럼에 인덱스

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Jinja2 템플릿](https://jinja.palletsprojects.com/)
- [Google Gemini API](https://ai.google.dev/)

---

**작성일**: 2025-01-14
**버전**: 1.0
**작성자**: Claude + 개발자
