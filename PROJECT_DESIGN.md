# 🧱 명월헌 운세 사이트 – 프로젝트 설계서

## 📋 목차
1. [프로젝트 개요](#1-프로젝트-개요)
2. [기술 스택](#2-기술-스택)
3. [서비스 기능](#3-서비스-기능)
4. [URL 구조](#4-url-구조)
5. [폴더 구조](#5-폴더-구조)
6. [데이터 모델](#6-데이터-모델)
7. [운세 처리 흐름](#7-운세-처리-흐름)
8. [템플릿 구조](#8-템플릿-구조)
9. [관리자 페이지](#9-관리자-페이지)
10. [배포 설정](#10-배포-설정)

---

## 1. 프로젝트 개요

### 🎯 서비스 이름
**명월헌(明月軒)**

### 🎬 비즈니스 모델
```
유튜브 쇼츠 콘텐츠 업로드
    ↓
쇼츠 설명/댓글에 명월헌 링크
    ↓
사용자 사이트 방문 → 무료 운세 확인
    ↓
구글 애드센스 광고 노출
    ↓
수익 발생 (쇼츠 + 애드센스)
```

### 💼 수익 구조
- 유튜브 쇼츠 광고 수익
- 명월헌 사이트 애드센스 수익

### 🛠 백엔드
- **FastAPI** 기반
- **Gemini API** 연동 (초기: 더미 텍스트 → 추후: AI 생성)

### 🌐 호스팅
- **Render** Web Service 1개로 운영
- 백엔드 + 템플릿 통합 서비스

---

## 2. 기술 스택

| 구분 | 기술 |
|------|------|
| **백엔드** | FastAPI (Python) |
| **템플릿 엔진** | Jinja2 (서버 렌더링 HTML) |
| **스타일** | 기본 CSS → 추후 Tailwind CSS |
| **데이터베이스** | SQLite (초기) → PostgreSQL (추후) |
| **캐싱** | DB 기반 캐싱 (user_key + service + date) |
| **호스팅** | Render – Web Service |
| **관리자 인증** | 단일 관리자 계정 (ID/비밀번호) |
| **AI** | Gemini 2.0 Flash (무료) |

---

## 3. 서비스 기능

### 🎭 4가지 운세 서비스

| 코드 | 서비스명 | 캐릭터 | 설명 |
|------|----------|--------|------|
| `today` | 오늘의 운세 | 야광묘 🐱✨ | 행운의 색상·숫자·방향 |
| `saju` | 정통 사주팔자 | 청월아씨 👘 | 오행/팔자/전체 흐름 |
| `match` | 사주궁합 | 월하낭자 💕 | 연애·결혼·인연운 |
| `dream` | 꿈해몽 | 백운선생 ☁️ | 꿈의 의미·재물·건강 |

### 👤 사용자 기능

#### 메인 페이지 (`/`)
- **히어로 영역**: 메인 이미지, 카피 문구
- **4개 서비스 카드**: 각 운세 소개 + "바로 보기" 버튼
- **빠른 운세 보기**: 간단 입력 폼 → 즉시 "오늘의 운세" 결과

#### 각 운세 상세 페이지
- `/fortune/today` - 오늘의 운세 (야광묘)
- `/fortune/saju` - 정통 사주팔자 (청월아씨)
- `/fortune/match` - 사주궁합 (월하낭자)
- `/fortune/dream` - 꿈해몽 (백운선생)

**구성**: 소개 문구 + 입력 폼 + 결과 페이지

#### 운세 결과
- **오늘의 운세**: 전체운 + 행운의 색/숫자/방향
- **사주팔자**: 오행/팔자/성격/직업운/연애운/건강운
- **사주궁합**: 두 사람의 궁합도/연애운/결혼운
- **꿈해몽**: 꿈 해석 + 재물운/건강운

#### 🔄 1일 1회 로직
```
같은 사람(user_key) + 같은 날(today) + 같은 서비스
→ 캐시된 결과 반환
→ "오늘 이미 보신 운세예요" 안내
```

#### 💰 애드센스 광고
- **메인 페이지**: 상단/중간/하단 슬롯
- **결과 페이지**: 본문 중간/하단 슬롯
- 광고 코드는 템플릿에 삽입, ID는 관리자 설정에서 관리

### 🔧 관리자 기능

#### 로그인 (`/admin/login`)
- 관리자 ID/비밀번호 인증
- DB 또는 `.env` 기반 초기 설정

#### 대시보드 (`/admin`)
- 오늘 호출 수
- 서비스별 조회 수
- 최근 운세 조회 로그 (상위 10개)

#### 사이트 설정 관리 (`/admin/settings/site`)
수정 가능 항목:
- 사이트 이름: "명월헌"
- 메인 타이틀: "명월헌 – 야광묘가 알려주는 오늘의 기운"
- 메인 서브텍스트
- 히어로 이미지 URL
- 빠른 운세 제목/설명
- 푸터 텍스트 (저작권, 이메일, 안내)
- 애드센스 Client ID / Slot ID

#### 서비스 설정 관리 (`/admin/settings/services`)
각 서비스별 수정 항목:
- 제목: "오늘의 운세"
- 서브텍스트: "야광묘가 알려드려요"
- 설명: "행운의 색상·숫자·방향"
- 캐릭터 이름: "야광묘"
- 캐릭터 이모지: "🐱✨"
- 활성/비활성 토글
- AI 프롬프트 템플릿 (고급)

#### 운세 조회 로그 (`/admin/logs`, 선택)
- 날짜/시간
- 서비스
- 입력 정보 (연도/성별/띠)
- 생성/캐시 여부

---

## 4. URL 구조

### 🟦 사용자용 (Public)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/` | 메인 페이지 (4개 서비스 카드 + 빠른 운세 폼) |
| `GET` | `/fortune/{service_code}` | 각 서비스 설명 + 입력 폼 |
| `POST` | `/fortune/{service_code}` | 폼 제출 → 결과 렌더링 (캐시/AI 호출) |
| `POST` | `/api/fortune/{service_code}` | JSON API (앱/webview용) |

**service_code**: `today` | `saju` | `match` | `dream`

### 🟥 관리자용 (Admin)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/admin/login` | 로그인 페이지 |
| `POST` | `/admin/login` | 로그인 처리 |
| `GET` | `/admin/logout` | 로그아웃 |
| `GET` | `/admin` | 대시보드 (조회 통계) |
| `GET` | `/admin/settings/site` | 사이트 설정 페이지 |
| `POST` | `/admin/settings/site` | 사이트 설정 저장 |
| `GET` | `/admin/settings/services` | 서비스 설정 목록 |
| `POST` | `/admin/settings/services/{service_code}` | 서비스 설정 저장 |
| `GET` | `/admin/logs` | 운세 조회 로그 (선택) |

---

## 5. 폴더 구조

```
myeongwolheon/
├─ app/
│  ├─ main.py                      # FastAPI 엔트리, 라우터 모음
│  ├─ config.py                    # 환경 변수, 설정 로딩
│  ├─ database.py                  # DB 연결 (SessionLocal)
│  │
│  ├─ models/                      # SQLAlchemy 모델
│  │   ├─ base.py                  # Base 클래스
│  │   ├─ site_config.py           # SiteConfig 모델
│  │   ├─ service_config.py        # FortuneServiceConfig 모델
│  │   ├─ fortune_result.py        # FortuneResult 모델
│  │   └─ admin_user.py            # AdminUser 모델
│  │
│  ├─ schemas/                     # Pydantic 스키마
│  │   ├─ fortune.py               # 운세 입력/출력 스키마
│  │   ├─ site_config.py           # 사이트 설정 스키마
│  │   └─ admin.py                 # 관리자 스키마
│  │
│  ├─ routers/                     # 라우팅 분리
│  │   ├─ public.py                # 메인, 각 운세 페이지
│  │   ├─ api_fortune.py           # /api/fortune/*
│  │   └─ admin/
│  │       ├─ auth.py              # 로그인/로그아웃
│  │       ├─ dashboard.py         # /admin
│  │       ├─ settings_site.py     # 사이트 설정
│  │       └─ settings_service.py  # 서비스 설정
│  │
│  ├─ services/                    # 비즈니스 로직
│  │   ├─ fortune_service.py       # 운세 생성/캐싱/AI 호출
│  │   ├─ site_service.py          # 설정 로드/저장
│  │   └─ auth_service.py          # 관리자 인증
│  │
│  ├─ templates/                   # Jinja2 템플릿
│  │   ├─ layout/
│  │   │   ├─ base.html            # 공통 레이아웃 (헤더/푸터/광고)
│  │   │   └─ admin_base.html      # 관리자 공통 레이아웃
│  │   ├─ public/
│  │   │   ├─ index.html           # 메인 페이지
│  │   │   ├─ fortune_form.html    # 서비스별 폼/설명
│  │   │   └─ fortune_result.html  # 결과 페이지
│  │   └─ admin/
│  │       ├─ login.html           # 로그인
│  │       ├─ dashboard.html       # 대시보드
│  │       ├─ settings_site.html   # 사이트 설정
│  │       ├─ settings_services.html # 서비스 설정
│  │       └─ logs.html            # 로그 (선택)
│  │
│  ├─ static/
│  │   ├─ css/
│  │   │   └─ style.css            # 메인 스타일
│  │   └─ images/                  # 로고, 캐릭터, 배너
│  │
│  └─ utils/
│      ├─ security.py              # 비밀번호 해시, 세션/쿠키
│      └─ hashing.py               # user_key 생성
│
├─ requirements.txt                # Python 패키지 목록
├─ render.yaml                     # Render 배포 설정
├─ README.md                       # 프로젝트 소개
└─ .env.example                    # 환경 변수 예시
```

---

## 6. 데이터 모델

### 6.1 SiteConfig (사이트 전체 설정)

```python
class SiteConfig(Base):
    __tablename__ = "site_config"

    id: int (PK)
    site_name: str                    # "명월헌"
    main_title: str                   # 메인 큰 제목
    main_subtitle: str                # 메인 설명
    hero_image_url: str               # 메인 이미지 URL
    quick_fortune_title: str          # "빠른 운세 보기"
    quick_fortune_description: str    # 설명 텍스트
    footer_text: str                  # 푸터 카피/저작권
    adsense_client_id: str (nullable) # 애드센스 클라이언트 ID
    adsense_slot_main: str (nullable) # 메인 광고 슬롯
    adsense_slot_result: str (nullable) # 결과 광고 슬롯
    created_at: datetime
    updated_at: datetime
```

**관리**: `/admin/settings/site` 페이지에서 수정

---

### 6.2 FortuneServiceConfig (4가지 운세 서비스 설정)

```python
class FortuneServiceConfig(Base):
    __tablename__ = "fortune_service_config"

    id: int (PK)
    code: str (unique)                # "today" | "saju" | "match" | "dream"
    title: str                        # "오늘의 운세"
    subtitle: str                     # "야광묘가 알려드려요"
    description: str                  # "행운의 색상·숫자·방향"
    character_name: str               # "야광묘"
    character_emoji: str              # "🐱✨"
    is_active: bool                   # 활성/비활성
    prompt_template: text (nullable)  # AI 프롬프트 템플릿
    created_at: datetime
    updated_at: datetime
```

**초기 데이터**: 4개 서비스 seed 데이터 삽입
**관리**: `/admin/settings/services` 페이지에서 수정

---

### 6.3 FortuneResult (운세 결과 캐시/로그)

```python
class FortuneResult(Base):
    __tablename__ = "fortune_result"

    id: int (PK)
    service_code: str                 # "today" | "saju" | "match" | "dream"
    user_key: str                     # 동일인 식별 해시 (SHA256)
    date: date                        # 운세 기준 날짜
    request_payload: JSON             # 입력 정보 (이름/생년월일/성별/띠)
    result_text: text                 # 운세 결과 전체 텍스트
    is_from_cache: bool               # 캐시 재사용 여부 (로그용)
    created_at: datetime

    # 인덱스: (service_code, user_key, date) UNIQUE
```

**캐싱 로직**:
- 한 사람(`user_key`) + 한 서비스 + 하루에 하나만 저장
- 재조회 시 캐시된 결과 반환

---

### 6.4 AdminUser (관리자 계정)

```python
class AdminUser(Base):
    __tablename__ = "admin_user"

    id: int (PK)
    username: str (unique)            # "admin"
    password_hash: str                # bcrypt 해시
    created_at: datetime
```

**초기 설정**:
- 마이그레이션 시 "admin / 초기비밀번호" seed
- 또는 `.env` 기반 생성

---

## 7. 운세 처리 흐름

### 7.1 공통 함수 (`fortune_service.py`)

#### `build_user_key(input) -> str`
```python
# 입력: 이름(선택), 생년/월/일, 성별, 띠
# 출력: SHA256 해시 문자열
# 목적: 동일인 식별용
```

#### `find_cached_result(service_code, user_key, today) -> FortuneResult?`
```python
# DB에서 (service_code, user_key, date=today) 조회
# 있으면 캐시 반환, 없으면 None
```

#### `create_fortune_result(service_code, input) -> str`
```python
# 1. service_code에 맞는 프롬프트 템플릿 로딩
# 2. 현재: 더미 텍스트 생성
# 3. 추후: Gemini API 호출 → 결과 받기
# 4. DB에 저장
# 5. 결과 텍스트 반환
```

#### `get_or_create_fortune(service_code, input) -> dict`
```python
# 메인 로직:
# 1. user_key 생성
# 2. 캐시 조회
# 3. 없으면 새 생성 + DB 저장
# 4. 결과 반환 (텍스트 + 메타 정보)
```

### 7.2 플로우 차트

```
사용자 입력 (이름, 생년월일, 성별 등)
    ↓
user_key 생성 (SHA256)
    ↓
DB 캐시 조회 (service_code, user_key, today)
    ↓
┌─────────────┬─────────────┐
│  캐시 있음   │  캐시 없음   │
└─────────────┴─────────────┘
       ↓                ↓
  캐시 반환      AI 생성 (Gemini API)
       │                ↓
       │           DB 저장
       │                ↓
       └────────┬───────┘
                ↓
          결과 반환 (템플릿 렌더링)
```

---

## 8. 템플릿 구조

### 8.1 `layout/base.html` (공통 레이아웃)

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ site_config.site_name }}</title>
    <!-- 애드센스 기본 코드 -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{ site_config.adsense_client_id }}"></script>
</head>
<body>
    <!-- 헤더 -->
    <header>
        <h1>{{ site_config.site_name }}</h1>
        <nav>
            <a href="/">홈</a>
            <a href="/fortune/today">오늘의 운세</a>
            <a href="/fortune/saju">정통 사주</a>
            <a href="/fortune/match">사주궁합</a>
            <a href="/fortune/dream">꿈해몽</a>
        </nav>
    </header>

    <!-- 메인 컨텐츠 -->
    {% block content %}{% endblock %}

    <!-- 광고 블록 -->
    {% block ad_main %}{% endblock %}
    {% block ad_result %}{% endblock %}

    <!-- 푸터 -->
    <footer>
        <p>{{ site_config.footer_text }}</p>
    </footer>
</body>
</html>
```

---

### 8.2 `public/index.html` (메인 페이지)

```html
{% extends "layout/base.html" %}

{% block content %}
<!-- 섹션 1: 히어로 -->
<section class="hero">
    <img src="{{ site_config.hero_image_url }}" alt="명월헌">
    <h2>{{ site_config.main_title }}</h2>
    <p>{{ site_config.main_subtitle }}</p>
</section>

<!-- 섹션 2: 4개 서비스 카드 -->
<section class="services">
    {% for service in services %}
    <div class="card">
        <span>{{ service.character_emoji }}</span>
        <h3>{{ service.title }}</h3>
        <p>{{ service.subtitle }}</p>
        <p>{{ service.description }}</p>
        <a href="/fortune/{{ service.code }}">바로 보기</a>
    </div>
    {% endfor %}
</section>

<!-- 섹션 3: 빠른 운세 보기 -->
<section class="quick-fortune">
    <h2>{{ site_config.quick_fortune_title }}</h2>
    <p>{{ site_config.quick_fortune_description }}</p>
    <form method="POST" action="/fortune/today">
        <input type="text" name="name" placeholder="이름 (선택)">
        <input type="date" name="birthdate" required>
        <select name="gender">
            <option value="male">남성</option>
            <option value="female">여성</option>
        </select>
        <button type="submit">오늘의 운세 보기</button>
    </form>
</section>
{% endblock %}
```

---

### 8.3 `public/fortune_form.html` (운세 입력 폼)

```html
{% extends "layout/base.html" %}

{% block content %}
<section class="fortune-form">
    <h1>{{ service.character_emoji }} {{ service.title }}</h1>
    <h2>{{ service.subtitle }}</h2>
    <p>{{ service.description }}</p>

    <form method="POST" action="/fortune/{{ service.code }}">
        <input type="text" name="name" placeholder="이름 (선택)">
        <input type="date" name="birthdate" required>
        <select name="gender">
            <option value="male">남성</option>
            <option value="female">여성</option>
        </select>

        {% if service.code == 'match' %}
        <!-- 궁합일 때만 상대방 정보 입력 -->
        <h3>상대방 정보</h3>
        <input type="text" name="partner_name" placeholder="상대방 이름 (선택)">
        <input type="date" name="partner_birthdate" required>
        <select name="partner_gender">
            <option value="male">남성</option>
            <option value="female">여성</option>
        </select>
        {% endif %}

        {% if service.code == 'dream' %}
        <!-- 꿈해몽일 때만 꿈 내용 입력 -->
        <textarea name="dream_content" placeholder="꿈 내용을 자세히 적어주세요" required></textarea>
        {% endif %}

        <button type="submit">{{ service.character_name }}에게 물어보기</button>
    </form>
</section>
{% endblock %}
```

---

### 8.4 `public/fortune_result.html` (운세 결과)

```html
{% extends "layout/base.html" %}

{% block content %}
<section class="fortune-result">
    <h1>{{ service.character_emoji }} {{ service.title }}</h1>
    <p class="date">{{ today }}</p>

    {% if is_cached %}
    <p class="cache-notice">오늘 이미 보신 운세예요</p>
    {% endif %}

    <div class="result-content">
        {{ result_text|safe }}
    </div>

    <div class="actions">
        <a href="/">메인으로</a>
        <a href="/fortune/{{ service.code }}">다시 보기</a>
    </div>
</section>

{% block ad_result %}
<!-- 애드센스 광고 -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="{{ site_config.adsense_client_id }}"
     data-ad-slot="{{ site_config.adsense_slot_result }}"
     data-ad-format="auto"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
{% endblock %}
{% endblock %}
```

---

## 9. 관리자 페이지

### 9.1 `layout/admin_base.html` (관리자 공통 레이아웃)

```html
<!DOCTYPE html>
<html>
<head>
    <title>명월헌 관리자</title>
</head>
<body>
    <div class="admin-layout">
        <!-- 좌측 사이드바 -->
        <aside class="sidebar">
            <h2>명월헌 관리</h2>
            <nav>
                <a href="/admin">대시보드</a>
                <a href="/admin/settings/site">사이트 설정</a>
                <a href="/admin/settings/services">서비스 설정</a>
                <a href="/admin/logs">조회 로그</a>
                <a href="/admin/logout">로그아웃</a>
            </nav>
        </aside>

        <!-- 우측 컨텐츠 -->
        <main class="content">
            {% block admin_content %}{% endblock %}
        </main>
    </div>
</body>
</html>
```

---

### 9.2 `admin/dashboard.html` (대시보드)

```html
{% extends "layout/admin_base.html" %}

{% block admin_content %}
<h1>대시보드</h1>

<!-- 오늘 통계 카드 -->
<div class="stats">
    <div class="card">
        <h3>오늘 전체 조회</h3>
        <p class="big-number">{{ stats.total_today }}</p>
    </div>

    <div class="card">
        <h3>오늘의 운세</h3>
        <p class="big-number">{{ stats.today_count }}</p>
    </div>

    <div class="card">
        <h3>정통 사주</h3>
        <p class="big-number">{{ stats.saju_count }}</p>
    </div>

    <div class="card">
        <h3>사주궁합</h3>
        <p class="big-number">{{ stats.match_count }}</p>
    </div>

    <div class="card">
        <h3>꿈해몽</h3>
        <p class="big-number">{{ stats.dream_count }}</p>
    </div>
</div>

<!-- 최근 조회 로그 -->
<div class="recent-logs">
    <h2>최근 조회</h2>
    <table>
        <thead>
            <tr>
                <th>시간</th>
                <th>서비스</th>
                <th>연도</th>
                <th>성별</th>
                <th>캐시</th>
            </tr>
        </thead>
        <tbody>
            {% for log in recent_logs %}
            <tr>
                <td>{{ log.created_at }}</td>
                <td>{{ log.service_code }}</td>
                <td>{{ log.request_payload.birthdate[:4] }}</td>
                <td>{{ log.request_payload.gender }}</td>
                <td>{{ "✓" if log.is_from_cache else "✗" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

---

### 9.3 `admin/settings_site.html` (사이트 설정)

```html
{% extends "layout/admin_base.html" %}

{% block admin_content %}
<h1>사이트 설정</h1>

<form method="POST">
    <div class="form-group">
        <label>사이트 이름</label>
        <input type="text" name="site_name" value="{{ config.site_name }}" required>
    </div>

    <div class="form-group">
        <label>메인 타이틀</label>
        <input type="text" name="main_title" value="{{ config.main_title }}" required>
    </div>

    <div class="form-group">
        <label>메인 서브텍스트</label>
        <textarea name="main_subtitle">{{ config.main_subtitle }}</textarea>
    </div>

    <div class="form-group">
        <label>히어로 이미지 URL</label>
        <input type="url" name="hero_image_url" value="{{ config.hero_image_url }}">
    </div>

    <div class="form-group">
        <label>빠른 운세 제목</label>
        <input type="text" name="quick_fortune_title" value="{{ config.quick_fortune_title }}">
    </div>

    <div class="form-group">
        <label>빠른 운세 설명</label>
        <textarea name="quick_fortune_description">{{ config.quick_fortune_description }}</textarea>
    </div>

    <div class="form-group">
        <label>푸터 텍스트</label>
        <textarea name="footer_text">{{ config.footer_text }}</textarea>
    </div>

    <hr>

    <h2>애드센스 설정</h2>

    <div class="form-group">
        <label>Client ID</label>
        <input type="text" name="adsense_client_id" value="{{ config.adsense_client_id }}">
    </div>

    <div class="form-group">
        <label>메인 슬롯 ID</label>
        <input type="text" name="adsense_slot_main" value="{{ config.adsense_slot_main }}">
    </div>

    <div class="form-group">
        <label>결과 슬롯 ID</label>
        <input type="text" name="adsense_slot_result" value="{{ config.adsense_slot_result }}">
    </div>

    <button type="submit">저장</button>
</form>
{% endblock %}
```

---

### 9.4 `admin/settings_services.html` (서비스 설정)

```html
{% extends "layout/admin_base.html" %}

{% block admin_content %}
<h1>서비스 설정</h1>

<table>
    <thead>
        <tr>
            <th>코드</th>
            <th>이모지</th>
            <th>제목</th>
            <th>캐릭터</th>
            <th>활성</th>
            <th>수정</th>
        </tr>
    </thead>
    <tbody>
        {% for service in services %}
        <tr>
            <td>{{ service.code }}</td>
            <td>{{ service.character_emoji }}</td>
            <td>{{ service.title }}</td>
            <td>{{ service.character_name }}</td>
            <td>{{ "✓" if service.is_active else "✗" }}</td>
            <td>
                <a href="/admin/settings/services/{{ service.code }}">수정</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<!-- 서비스별 상세 수정 폼 -->
{% if selected_service %}
<hr>
<h2>{{ selected_service.code }} 수정</h2>
<form method="POST" action="/admin/settings/services/{{ selected_service.code }}">
    <div class="form-group">
        <label>제목</label>
        <input type="text" name="title" value="{{ selected_service.title }}" required>
    </div>

    <div class="form-group">
        <label>서브텍스트</label>
        <input type="text" name="subtitle" value="{{ selected_service.subtitle }}">
    </div>

    <div class="form-group">
        <label>설명</label>
        <textarea name="description">{{ selected_service.description }}</textarea>
    </div>

    <div class="form-group">
        <label>캐릭터 이름</label>
        <input type="text" name="character_name" value="{{ selected_service.character_name }}">
    </div>

    <div class="form-group">
        <label>캐릭터 이모지</label>
        <input type="text" name="character_emoji" value="{{ selected_service.character_emoji }}">
    </div>

    <div class="form-group">
        <label>
            <input type="checkbox" name="is_active" {{ "checked" if selected_service.is_active }}>
            활성화
        </label>
    </div>

    <div class="form-group">
        <label>AI 프롬프트 템플릿 (고급)</label>
        <textarea name="prompt_template" rows="10">{{ selected_service.prompt_template }}</textarea>
        <small>변수: {name}, {birthdate}, {gender}, {zodiac}</small>
    </div>

    <button type="submit">저장</button>
</form>
{% endif %}
{% endblock %}
```

---

## 10. 배포 설정

### 10.1 `requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
google-generativeai==0.3.1
```

---

### 10.2 `render.yaml`

```yaml
services:
  - type: web
    name: myeongwolheon
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port 10000
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: myeongwolheon-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: GEMINI_API_KEY
        sync: false

databases:
  - name: myeongwolheon-db
    databaseName: myeongwolheon
    user: myeongwolheon
```

---

### 10.3 `.env.example`

```env
# 데이터베이스
DATABASE_URL=sqlite:///./myeongwolheon.db
# 배포 시: postgresql://user:pass@host:port/dbname

# 보안
SECRET_KEY=your-secret-key-here-change-this-in-production

# 관리자 초기 계정
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123!

# Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# 환경
ENVIRONMENT=development
# 배포 시: production
```

---

### 10.4 데이터베이스 마이그레이션

#### 초기: SQLite
```python
# app/database.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./myeongwolheon.db"
```

#### 추후: PostgreSQL (Render)
```python
# app/database.py
import os
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## 📌 개발 순서 (권장)

1. ✅ **프로젝트 구조 생성**
   - 폴더/파일 뼈대 만들기

2. ✅ **데이터베이스 모델 작성**
   - SQLAlchemy 모델 4개 작성
   - 초기 seed 데이터 스크립트

3. ✅ **관리자 인증 시스템**
   - 로그인/로그아웃
   - 세션 관리

4. ✅ **공개 라우터 (더미 데이터)**
   - 메인 페이지
   - 각 운세 폼 페이지
   - 결과 페이지 (더미 텍스트)

5. ✅ **관리자 라우터**
   - 대시보드
   - 사이트 설정
   - 서비스 설정

6. ✅ **캐싱 로직 구현**
   - user_key 생성
   - DB 캐시 조회/저장

7. ✅ **Gemini API 연동**
   - AI 프롬프트 생성
   - API 호출
   - 결과 파싱

8. ✅ **템플릿 디자인**
   - CSS 스타일링
   - 반응형 디자인
   - 애드센스 삽입

9. ✅ **테스트 & 배포**
   - 로컬 테스트
   - Render 배포
   - 도메인 연결

---

## 🎯 핵심 기능 요약

| 기능 | 상태 | 설명 |
|------|------|------|
| 4가지 운세 서비스 | ✅ | 오늘의 운세, 사주팔자, 궁합, 꿈해몽 |
| 1일 1회 캐싱 | ✅ | user_key + date 기반 중복 방지 |
| 관리자 설정 | ✅ | 사이트/서비스 모든 텍스트 수정 가능 |
| Gemini AI | 🔄 | 초기: 더미 → 추후: 실제 AI |
| 애드센스 | ✅ | 관리자에서 ID 설정 가능 |
| Render 배포 | ✅ | 단일 Web Service로 운영 |

---

**문서 버전**: 1.0
**최종 수정**: 2025-01-13
**작성자**: Claude Code
