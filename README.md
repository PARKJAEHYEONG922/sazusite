# 🌙 명월헌 (Myeongwolheon) - AI 운세 서비스

FastAPI 기반 AI 운세 서비스입니다. Gemini API를 활용하여 4가지 운세 서비스를 제공합니다.

## ✨ 주요 기능

- 🐱 **오늘의 운세** (야광묘): 행운의 색/숫자/방향
- 👘 **정통 사주팔자** (청월아씨): 성격/2025년운/직업/연애/건강
- 💕 **사주궁합** (월하낭자): 두 사람의 궁합 분석
- ☁️ **꿈해몽** (백운선생): 꿈의 의미 해석

## 🛠 기술 스택

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite (개발) / PostgreSQL (배포)
- **Template**: Jinja2
- **AI**: Google Gemini 2.0 Flash
- **Hosting**: Render (예정)

## 📁 프로젝트 구조

```
myeongwolheon/
├─ app/
│  ├─ main.py              # FastAPI 앱
│  ├─ config.py            # 환경 설정
│  ├─ database.py          # DB 연결
│  ├─ init_db.py           # DB 초기화 스크립트
│  ├─ models/              # SQLAlchemy 모델
│  ├─ schemas/             # Pydantic 스키마
│  ├─ routers/             # API 라우터
│  ├─ services/            # 비즈니스 로직
│  ├─ templates/           # Jinja2 템플릿
│  ├─ static/              # 정적 파일
│  └─ utils/               # 유틸리티
├─ requirements.txt
├─ .env
└─ README.md
```

## 📦 설치 방법

### 1. Python 설치 확인
```bash
python --version  # Python 3.11 이상 필요
```

### 2. 가상환경 생성 (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일을 확인하고 필요시 수정:
```env
GEMINI_API_KEY=your-api-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password
```

### 5. 데이터베이스 초기화
```bash
python -m app.init_db
```

출력 예시:
```
🗄️  데이터베이스 테이블 생성 중...
✅ 테이블 생성 완료!

🌙 사이트 설정 초기화 중...
✅ 사이트 설정 생성 완료!

🎭 서비스 설정 초기화 중...
  ✅ 오늘의 운세 (today) 생성 완료!
  ✅ 정통 사주팔자 (saju) 생성 완료!
  ✅ 사주궁합 (match) 생성 완료!
  ✅ 꿈해몽 (dream) 생성 완료!

👤 관리자 계정 초기화 중...
✅ 관리자 계정 생성 완료!
   ID: admin
   PW: admin1234

==================================================
✅ 데이터베이스 초기화가 완료되었습니다!
==================================================
```

### 6. 서버 실행
```bash
# 개발 서버 (자동 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는
python -m app.main
```

브라우저에서 접속:
- 메인: http://localhost:8000
- API 문서: http://localhost:8000/docs
- API 테스트: http://localhost:8000/api/test

### 3. 애드센스 설정

#### 3-1. HTML 파일 수정
- [public/index.html](public/index.html)
- [public/fortune.html](public/fortune.html)

두 파일에서 다음을 교체:
```html
<!-- 변경 전 -->
ca-pub-YOUR_ADSENSE_ID

<!-- 변경 후 -->
ca-pub-1234567890123456  <!-- 실제 애드센스 ID -->
```

#### 3-2. ads.txt 수정
[public/ads.txt](public/ads.txt) 파일 수정:
```
google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0
```

### 4. Cloudways 배포

#### 4-1. Cloudways 애플리케이션 생성
1. Cloudways 대시보드 로그인
2. "Add Application" 클릭
3. PHP 애플리케이션 선택
4. PHP 버전: 8.2 이상

#### 4-2. 파일 업로드
**방법 A: FTP/SFTP (추천)**
```bash
# FileZilla나 WinSCP 사용
# Cloudways에서 SFTP 정보 확인
호스트: server-xxx.cloudways.com
사용자명: master_xxxxx
포트: 22

# 전체 파일을 public_html 폴더에 업로드
```

**방법 B: Git 배포**
```bash
# Cloudways Git 설정
1. Application Settings > Deployment via Git
2. 브랜치 입력 (main 또는 master)
3. Deploy Now 클릭
```

#### 4-3. 도메인 연결
1. Cloudways: Domain Management
2. Primary Domain 추가
3. DNS 설정 (A 레코드)
4. SSL 인증서 활성화 (무료 Let's Encrypt)

#### 4-4. Redis 활성화 (선택 - 성능 향상)
1. Application Settings > Application Management
2. "Enable Redis" 활성화
3. config.php에서 `USE_REDIS = true` 확인

### 5. 테스트

1. **API 테스트**
   ```
   https://yourdomain.com/api/fortune.php
   ```

2. **프론트엔드 테스트**
   ```
   https://yourdomain.com
   ```

3. **사주 조회 테스트**
   - 생년월일 입력
   - 시간 선택
   - "AI가 내 사주 분석하기" 클릭
   - 30초 내 결과 확인

## 📊 성능 최적화

### 캐싱 확인
```php
// api/fortune.php에서 자동으로 캐싱
// 같은 생년월일시 = 24시간 캐시
```

### 속도 체크리스트
- ✅ Redis 활성화
- ✅ Cloudflare CDN 연결 (선택)
- ✅ 이미지 WebP 변환
- ✅ GZIP 압축 활성화 (.htaccess)

## 💰 수익화 전략

### 애드센스 최적화
1. **광고 배치**
   - 상단 배너 (index.html)
   - 사주 결과 중간 (fortune.html)
   - 하단 고정 광고

2. **클릭률 향상**
   - 자연스러운 광고 배치
   - 콘텐츠 품질 유지
   - 모바일 최적화

### 유튜브 쇼츠 연동
1. **쇼츠 콘텐츠**
   - "오늘의 띠별 운세"
   - "이 사주 특징은?"
   - "2025년 운세 미리보기"

2. **사이트 유도**
   ```
   영상 설명란:
   "자세한 사주 분석은 👉 https://yourdomain.com"

   UTM 추적:
   https://yourdomain.com?utm_source=youtube&utm_medium=shorts&utm_campaign=daily
   ```

## 🛠️ 유지보수

### 로그 확인
```bash
# Cloudways SSH 접속 후
cd logs/
tail -f fortune_$(date +%Y-%m-%d).log
```

### 캐시 초기화 (필요시)
```bash
# Redis 사용 시
redis-cli FLUSHALL

# 파일 캐싱 사용 시
rm -rf cache/*.json
```

### Gemini API 쿼터 확인
```
https://aistudio.google.com/app/apikey
→ API 키 클릭 → Usage 확인
```

## 🔧 트러블슈팅

### "Gemini API 키가 설정되지 않았습니다"
→ [api/config/config.php](api/config/config.php)에서 API 키 확인

### "500 Internal Server Error"
→ PHP 버전 확인 (8.0 이상 필요)
→ logs/ 폴더 권한 확인 (755)

### 사주 결과가 표시되지 않음
→ 브라우저 콘솔(F12) 확인
→ API 엔드포인트 URL 확인

### 광고가 표시되지 않음
→ 애드센스 승인 완료 확인
→ ads.txt 파일 접근 가능 확인
→ 24-48시간 대기 (광고 활성화 시간)

## 📈 분석 도구 추가 (선택)

### Google Analytics 4
```html
<!-- public/index.html, fortune.html <head>에 추가 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## 🎯 다음 단계

1. ✅ 사이트 배포 완료
2. ⏳ 애드센스 광고 활성화 (24-48시간)
3. ⏳ 유튜브 쇼츠 제작 시작
4. ⏳ 첫 방문자 유입 추적
5. ⏳ 수익 발생 모니터링

## 📞 지원

문제가 발생하면:
1. logs/ 폴더의 에러 로그 확인
2. 브라우저 콘솔(F12) 에러 확인
3. Gemini API 쿼터 확인

## 📝 라이선스

개인 프로젝트 - 자유롭게 수정 및 사용 가능

---

**제작일**: 2025
**버전**: 1.0.0
**기술 스택**: PHP 8.2+, Vanilla JS, Tailwind CSS, Gemini 2.0 Flash
