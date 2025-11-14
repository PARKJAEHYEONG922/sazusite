# 🚀 명월헌 서버 배포 가이드

## 📋 목차
1. [배포 전 준비사항](#1-배포-전-준비사항)
2. [서버 환경 설정](#2-서버-환경-설정)
3. [PostgreSQL 설치 및 설정](#3-postgresql-설치-및-설정)
4. [애플리케이션 배포](#4-애플리케이션-배포)
5. [Nginx 설정 (리버스 프록시)](#5-nginx-설정)
6. [HTTPS 인증서 설치 (Let's Encrypt)](#6-https-인증서-설치)
7. [시스템 서비스 등록 (자동 시작)](#7-시스템-서비스-등록)
8. [배포 후 체크리스트](#8-배포-후-체크리스트)
9. [API 키 관리 전략](#9-api-키-관리-전략)

---

## 1. 배포 전 준비사항

### 1.1 서버 요구사항
- **OS**: Ubuntu 20.04 LTS 이상 (또는 CentOS 8+)
- **CPU**: 2 Core 이상
- **RAM**: 2GB 이상 (4GB 권장)
- **디스크**: 20GB 이상
- **도메인**: myeongwolheon.kr (DNS 설정 완료)

### 1.2 필요한 계정 및 키
- [ ] 서버 SSH 접속 정보
- [ ] 도메인 네임서버 설정 권한
- [ ] Gemini API 키 (이미 발급됨: `AIzaSy...`)
- [ ] Google Analytics 추적 ID
- [ ] Google AdSense 클라이언트 ID

### 1.3 로컬에서 마지막 테스트
```bash
# 현재 설정으로 서버 실행 테스트
python -m uvicorn app.main:app --reload

# 브라우저에서 확인
# http://localhost:8000
```

---

## 2. 서버 환경 설정

### 2.1 서버 접속
```bash
# SSH로 서버 접속
ssh root@your-server-ip

# 또는 특정 사용자로 접속
ssh myeongwol@your-server-ip
```

### 2.2 시스템 업데이트
```bash
# 패키지 목록 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3.11 python3.11-venv python3-pip \
    git nginx postgresql postgresql-contrib \
    build-essential libpq-dev certbot python3-certbot-nginx
```

### 2.3 방화벽 설정
```bash
# UFW 방화벽 활성화
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# 포트 확인
sudo ufw status
```

---

## 3. PostgreSQL 설치 및 설정

### 3.1 PostgreSQL 설치 확인
```bash
# PostgreSQL 버전 확인
psql --version
# 출력: psql (PostgreSQL) 14.x

# PostgreSQL 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3.2 데이터베이스 생성
```bash
# PostgreSQL 사용자로 전환
sudo -u postgres psql

# PostgreSQL 콘솔에서 실행:
```

```sql
-- 데이터베이스 사용자 생성
CREATE USER myeongwol_user WITH PASSWORD '강력한비밀번호123!@#';

-- 데이터베이스 생성
CREATE DATABASE myeongwolheon_db OWNER myeongwol_user;

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE myeongwolheon_db TO myeongwol_user;

-- 연결 확인
\c myeongwolheon_db

-- 종료
\q
```

### 3.3 PostgreSQL 접속 테스트
```bash
# 생성한 사용자로 접속 테스트
psql -U myeongwol_user -d myeongwolheon_db -h localhost

# 비밀번호 입력 후 접속되면 성공
# \q로 종료
```

### 3.4 외부 접속 차단 (보안)
```bash
# PostgreSQL 설정 파일 편집
sudo nano /etc/postgresql/14/main/pg_hba.conf

# 맨 아래에 로컬 접속만 허용 (이미 설정되어 있을 수 있음)
# local   all   all   peer
# host    all   all   127.0.0.1/32   md5
# host    all   all   ::1/128        md5

# 외부 접속은 절대 허용하지 마세요!
# PostgreSQL 재시작
sudo systemctl restart postgresql
```

---

## 4. 애플리케이션 배포

### 4.1 배포 디렉토리 생성
```bash
# 애플리케이션 디렉토리 생성
sudo mkdir -p /var/www/myeongwolheon
sudo chown -R $USER:$USER /var/www/myeongwolheon
cd /var/www/myeongwolheon
```

### 4.2 코드 업로드
**방법 1: Git Clone (권장)**
```bash
# Git 리포지토리 클론 (Private 리포지토리인 경우 인증 필요)
git clone https://github.com/yourusername/myeongwolheon.git .

# 또는 특정 브랜치
git clone -b main https://github.com/yourusername/myeongwolheon.git .
```

**방법 2: SCP/SFTP로 직접 업로드**
```bash
# 로컬 컴퓨터에서 실행 (Windows PowerShell 또는 CMD)
scp -r C:\사주사이트\* myeongwol@your-server-ip:/var/www/myeongwolheon/
```

### 4.3 가상환경 생성 및 패키지 설치
```bash
cd /var/www/myeongwolheon

# Python 가상환경 생성
python3.11 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 패키지 설치
pip install -r requirements.txt
```

### 4.4 환경 변수 설정 (`.env` 파일)
```bash
# .env 파일 생성
nano .env
```

아래 내용을 붙여넣고 **반드시 수정**하세요:
```bash
# ========================================
# 프로덕션 환경 설정
# ========================================

# 데이터베이스 (PostgreSQL)
DATABASE_URL=postgresql://myeongwol_user:강력한비밀번호123!@#@localhost:5432/myeongwolheon_db

# 보안
SECRET_KEY=xvXFnPEsLdnkL5HOT0nC2XUGksI35GMV_7tctXb7IeM
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 관리자 계정
ADMIN_USERNAME=admin
ADMIN_PASSWORD=FGYsRoMi87y^K*k$

# Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models

# 환경 (프로덕션!)
ENVIRONMENT=production
DEBUG=False

# 캐시
CACHE_ENABLED=True
CACHE_DURATION_HOURS=24
```

**저장**: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4.5 데이터베이스 초기화
```bash
# 가상환경 활성화 상태에서
cd /var/www/myeongwolheon

# 데이터베이스 테이블 생성 및 초기 데이터 삽입
python app/init_db.py
```

**출력 예시:**
```
[OK] Database tables created!
[OK] Initial admin user created: admin
[OK] Initial site config created
[OK] All services initialized
```

### 4.6 애플리케이션 실행 테스트
```bash
# Uvicorn으로 실행 (테스트)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 브라우저에서 확인: http://your-server-ip:8000
# 정상 작동하면 Ctrl+C로 종료
```

---

## 5. Nginx 설정 (리버스 프록시)

### 5.1 Nginx 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/myeongwolheon
```

아래 내용을 붙여넣기:
```nginx
server {
    listen 80;
    server_name myeongwolheon.kr www.myeongwolheon.kr;

    client_max_body_size 10M;

    # 정적 파일 (이미지, CSS, JS)
    location /static/ {
        alias /var/www/myeongwolheon/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 애플리케이션 프록시
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 지원 (필요시)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 타임아웃 설정 (AI 응답 대기 시간)
        proxy_read_timeout 90s;
        proxy_connect_timeout 90s;
        proxy_send_timeout 90s;
    }

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
}
```

### 5.2 Nginx 설정 활성화
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/myeongwolheon /etc/nginx/sites-enabled/

# 기본 설정 비활성화 (선택)
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# 출력: nginx: configuration file /etc/nginx/nginx.conf test is successful

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 6. HTTPS 인증서 설치 (Let's Encrypt)

### 6.1 Certbot으로 SSL 인증서 발급
```bash
# Certbot 실행 (자동으로 Nginx 설정 업데이트)
sudo certbot --nginx -d myeongwolheon.kr -d www.myeongwolheon.kr

# 이메일 입력: your-email@example.com
# 약관 동의: Y
# 뉴스레터: N (선택)
# Redirect HTTP to HTTPS: 2 (Redirect 선택)
```

### 6.2 인증서 자동 갱신 설정
```bash
# 자동 갱신 테스트
sudo certbot renew --dry-run

# Cron에 자동 갱신 추가 (이미 설정되어 있을 수 있음)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## 7. 시스템 서비스 등록 (자동 시작)

### 7.1 Systemd 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/myeongwolheon.service
```

아래 내용 붙여넣기:
```ini
[Unit]
Description=명월헌 FastAPI Application
After=network.target postgresql.service

[Service]
Type=simple
User=myeongwol
WorkingDirectory=/var/www/myeongwolheon
Environment="PATH=/var/www/myeongwolheon/venv/bin"

ExecStart=/var/www/myeongwolheon/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7.2 서비스 활성화 및 시작
```bash
# 서비스 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start myeongwolheon

# 부팅 시 자동 시작 활성화
sudo systemctl enable myeongwolheon

# 서비스 상태 확인
sudo systemctl status myeongwolheon
```

**정상 작동 확인:**
```
● myeongwolheon.service - 명월헌 FastAPI Application
   Loaded: loaded (/etc/systemd/system/myeongwolheon.service; enabled)
   Active: active (running) since ...
```

### 7.3 서비스 관리 명령어
```bash
# 서비스 재시작
sudo systemctl restart myeongwolheon

# 서비스 중지
sudo systemctl stop myeongwolheon

# 로그 확인
sudo journalctl -u myeongwolheon -f

# 최근 100줄 로그
sudo journalctl -u myeongwolheon -n 100
```

---

## 8. 배포 후 체크리스트

### 8.1 필수 확인 사항
- [ ] https://myeongwolheon.kr 접속 확인
- [ ] HTTPS 인증서 정상 (자물쇠 아이콘)
- [ ] 메인 페이지 로딩 확인
- [ ] 오늘의 운세 테스트 (실제 운세 생성 확인)
- [ ] 관리자 페이지 로그인 (`https://myeongwolheon.kr/admin/login`)
- [ ] Gemini API 정상 작동 확인
- [ ] PostgreSQL 연결 확인

### 8.2 SEO 설정
```bash
# 1. Google Search Console 등록
# https://search.google.com/search-console

# 2. Sitemap 제출
# https://myeongwolheon.kr/sitemap.xml

# 3. robots.txt 확인
# https://myeongwolheon.kr/robots.txt

# 4. Google Analytics 설치
# 관리자 페이지 > 사이트 설정 > 헤더 스크립트에 GA4 코드 추가
```

### 8.3 애드센스 설정
- [ ] Google AdSense 계정 승인 대기
- [ ] 광고 코드 삽입 (관리자 페이지 > 사이트 설정)
- [ ] 광고 표시 확인 (승인 후 24시간 이내)

### 8.4 보안 헤더 추가
```bash
# Nginx 설정에 보안 헤더 추가
sudo nano /etc/nginx/sites-available/myeongwolheon
```

`server` 블록 안에 추가:
```nginx
# 보안 헤더
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

```bash
# Nginx 재시작
sudo systemctl restart nginx
```

---

## 9. API 키 관리 전략

### 9.1 API 키 보안 원칙

#### ✅ 올바른 방법: **서버 환경 변수만 사용**
```bash
# .env 파일에 API 키 저장 (서버 로컬 파일)
GEMINI_API_KEY=AIzaSy...

# 권한 설정 (소유자만 읽기 가능)
chmod 600 /var/www/myeongwolheon/.env
```

#### ❌ 절대 하지 말아야 할 것
- **DB에 API 키 저장** (데이터베이스 해킹 시 유출)
- **관리자 페이지에서 수정 가능** (관리자 계정 탈취 시 위험)
- **Git에 커밋** (.gitignore에 .env 반드시 포함)
- **로그에 출력** (에러 로그에 API 키 노출 금지)

### 9.2 API 키 접근 권한

**현재 구조 (올바름):**
```
서버 시작 시:
.env 파일 → config.py → gemini_service.py → Gemini API 호출
           ↑
      서버 관리자만 접근 가능 (SSH, 파일 권한)
```

**관리자 페이지에서는:**
- ✅ API 사용량 통계 확인 (로그)
- ✅ 서비스 ON/OFF
- ❌ API 키 조회 불가
- ❌ API 키 수정 불가

### 9.3 API 키 교체 방법 (필요 시)

```bash
# 1. 서버 SSH 접속
ssh myeongwol@your-server-ip

# 2. .env 파일 편집
cd /var/www/myeongwolheon
nano .env

# 3. GEMINI_API_KEY 값 변경
GEMINI_API_KEY=새로운_API_키

# 4. 서비스 재시작
sudo systemctl restart myeongwolheon

# 5. 로그 확인 (정상 작동 여부)
sudo journalctl -u myeongwolheon -f
```

### 9.4 API 키 유출 대응

**만약 API 키가 유출되었다면:**
1. 즉시 Google AI Studio에서 해당 키 삭제
2. 새 API 키 발급
3. `.env` 파일 업데이트
4. 서비스 재시작
5. GitHub Secrets Scanning 확인 (Git에 커밋된 적 있는지)

---

## 10. 모니터링 및 유지보수

### 10.1 서버 상태 모니터링
```bash
# CPU, 메모리 사용량
htop

# 디스크 사용량
df -h

# 네트워크 트래픽
sudo iftop

# PostgreSQL 상태
sudo systemctl status postgresql

# Nginx 상태
sudo systemctl status nginx

# 애플리케이션 상태
sudo systemctl status myeongwolheon
```

### 10.2 로그 확인
```bash
# 애플리케이션 로그 (실시간)
sudo journalctl -u myeongwolheon -f

# Nginx 접속 로그
sudo tail -f /var/log/nginx/access.log

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log

# PostgreSQL 로그
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### 10.3 데이터베이스 백업
```bash
# 백업 디렉토리 생성
mkdir -p /var/backups/myeongwolheon

# 데이터베이스 백업
pg_dump -U myeongwol_user -h localhost myeongwolheon_db > \
    /var/backups/myeongwolheon/backup_$(date +%Y%m%d_%H%M%S).sql

# Cron으로 자동 백업 (매일 새벽 3시)
crontab -e

# 아래 줄 추가:
0 3 * * * pg_dump -U myeongwol_user -h localhost myeongwolheon_db > /var/backups/myeongwolheon/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql

# 오래된 백업 자동 삭제 (30일 이상)
0 4 * * * find /var/backups/myeongwolheon -name "backup_*.sql" -mtime +30 -delete
```

### 10.4 업데이트 배포
```bash
# 1. Git Pull (코드 업데이트)
cd /var/www/myeongwolheon
git pull origin main

# 2. 패키지 업데이트 (requirements.txt 변경 시)
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 3. DB 마이그레이션 (스키마 변경 시)
python scripts/migrations/마이그레이션파일.py

# 4. 서비스 재시작
sudo systemctl restart myeongwolheon

# 5. 로그 확인
sudo journalctl -u myeongwolheon -f
```

---

## 11. 트러블슈팅

### 문제 1: 서비스가 시작되지 않음
```bash
# 로그 확인
sudo journalctl -u myeongwolheon -n 50

# 일반적인 원인:
# - .env 파일 없음 또는 잘못된 경로
# - PostgreSQL 연결 실패
# - 포트 8000 이미 사용 중
```

### 문제 2: 502 Bad Gateway
```bash
# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log

# 원인:
# - Uvicorn 서비스 중지됨
# - 포트 번호 불일치
```

### 문제 3: Gemini API 오류
```bash
# API 키 확인
cat /var/www/myeongwolheon/.env | grep GEMINI

# 할당량 확인: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
```

---

## 📞 도움이 필요하시면

- **이메일**: admin@myeongwolheon.kr
- **GitHub Issues**: [리포지토리 주소]
- **문서**: README.md, ARCHITECTURE.md

---

**🎉 배포 완료! 명월헌이 성공적으로 운영되길 바랍니다!**
