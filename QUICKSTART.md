# 🚀 명월헌 빠른 시작 가이드

## 1분 안에 시작하기

### 1. 서버 실행
```bash
cd C:\사주사이트
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 브라우저 열기
- 메인: http://localhost:8000
- 관리자: http://localhost:8000/admin/login
  - ID: `admin`
  - PW: `admin123`

### 3. 운세 테스트
1. "오늘의 운세" 클릭
2. 정보 입력 (이름, 생년월일, 성별)
3. "야광묘에게 물어보기" 클릭
4. 30초 대기 → AI 생성 운세 확인!

## 주요 URL

| 페이지 | URL | 설명 |
|--------|-----|------|
| 메인 | http://localhost:8000 | 4가지 운세 서비스 |
| 오늘의 운세 | http://localhost:8000/fortune/today | 야광묘 |
| 정통 사주 | http://localhost:8000/fortune/saju | 청월아씨 |
| 사주궁합 | http://localhost:8000/fortune/match | 월하낭자 |
| 꿈해몽 | http://localhost:8000/fortune/dream | 백운선생 |
| 관리자 | http://localhost:8000/admin/login | 대시보드 |
| API 문서 | http://localhost:8000/docs | Swagger UI |

## Gemini API 테스트

```bash
python test_gemini.py
```

출력 예시:
```
Gemini API 테스트 시작...
응답 대기 중...
[성공] Gemini API 응답:
연결 성공!
[OK] Gemini API가 정상 작동합니다!
```

## 문제 해결

### 서버가 시작되지 않을 때
```bash
# 패키지 재설치
pip install -r requirements.txt

# DB 재초기화
python -m app.init_db
```

### Gemini API 오류
1. `.env` 파일에서 `GEMINI_API_KEY` 확인
2. API 키 할당량 확인: https://aistudio.google.com/app/apikey

### 포트 충돌
```bash
# 다른 포트 사용
uvicorn app.main:app --port 8080
```

## 다음 단계

- [ ] 실제 운세 생성 테스트
- [ ] 관리자 페이지 둘러보기
- [ ] Render에 배포
- [ ] 도메인 연결
- [ ] 애드센스 광고 삽입
