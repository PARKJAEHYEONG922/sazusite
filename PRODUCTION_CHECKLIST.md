# 🚀 프로덕션 배포 체크리스트

## 📋 배포 전 필수 확인사항

### 1. 서버 환경 준비
- [ ] Ubuntu/CentOS 서버 준비 완료
- [ ] 도메인 연결 완료
- [ ] SSH 접속 가능 확인
- [ ] 방화벽 설정 (80, 443 포트 열기)

### 2. PostgreSQL 설치 및 설정

#### PostgreSQL 설치 (Ubuntu 기준)
```bash
# PostgreSQL 설치
sudo apt update
sudo apt install postgresql postgresql-contrib

# PostgreSQL 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 버전 확인
psql --version
```

#### 데이터베이스 및 사용자 생성
```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 생성
CREATE DATABASE myeongwolheon_db;

# 사용자 생성 및 권한 부여
CREATE USER myeongwol_user WITH PASSWORD '강력한비밀번호여기입력';
ALTER ROLE myeongwol_user SET client_encoding TO 'utf8';
ALTER ROLE myeongwol_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE myeongwol_user SET timezone TO 'Asia/Seoul';
GRANT ALL PRIVILEGES ON DATABASE myeongwolheon_db TO myeongwol_user;

# PostgreSQL 13 이상인 경우 추가 권한 필요
\c myeongwolheon_db
GRANT ALL ON SCHEMA public TO myeongwol_user;

# 종료
\q
```

### 3. .env 파일 설정

서버에서 `.env` 파일을 다음과 같이 수정:

```env
# ========================================
# 데이터베이스 설정
# ========================================
DATABASE_URL=postgresql://myeongwol_user:실제비밀번호@localhost:5432/myeongwolheon_db

# ========================================
# 보안 설정
# ========================================
SECRET_KEY=xvXFnPEsLdnkL5HOT0nC2XUGksI35GMV_7tctXb7IeM
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ========================================
# 관리자 계정 설정
# ========================================
ADMIN_USERNAME=admin
ADMIN_PASSWORD=실제_설정한_비밀번호

# ========================================
# Gemini API 설정
# ========================================
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models

# ========================================
# 환경 설정 (프로덕션)
# ========================================
ENVIRONMENT=production
DEBUG=False

# ========================================
# 캐시 설정
# ========================================
CACHE_ENABLED=True
CACHE_DURATION_HOURS=24
```

### 4. 프로젝트 배포

#### 프로젝트 업로드
```bash
# Git 사용 시
git clone https://github.com/your-username/myeongwolheon.git
cd myeongwolheon

# 또는 FTP/SCP로 직접 업로드
```

#### Python 가상환경 설정
```bash
# Python 3.10 이상 설치 확인
python3 --version

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

#### 데이터베이스 초기화
```bash
# 가상환경 활성화 상태에서
python -c "from app.database import init_db; init_db()"
```

### 5. Nginx 설정

#### Nginx 설치
```bash
sudo apt install nginx
```

#### 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/myeongwolheon
```

다음 내용 입력:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/username/myeongwolheon/app/static;
        expires 30d;
    }
}
```

#### Nginx 활성화
```bash
sudo ln -s /etc/nginx/sites-available/myeongwolheon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Systemd 서비스 설정

#### 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/myeongwolheon.service
```

다음 내용 입력:
```ini
[Unit]
Description=Myeongwolheon FastAPI Application
After=network.target

[Service]
Type=notify
User=username
Group=www-data
WorkingDirectory=/home/username/myeongwolheon
Environment="PATH=/home/username/myeongwolheon/venv/bin"
ExecStart=/home/username/myeongwolheon/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 서비스 시작
```bash
sudo systemctl daemon-reload
sudo systemctl start myeongwolheon
sudo systemctl enable myeongwolheon
sudo systemctl status myeongwolheon
```

### 7. SSL 인증서 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

### 8. 방화벽 설정

```bash
# UFW 방화벽 설정
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
sudo ufw status
```

## 🧪 배포 후 테스트

### 1. 기본 접속 테스트
- [ ] http://도메인 접속 확인
- [ ] https://도메인 접속 확인 (SSL)
- [ ] 메인 페이지 로딩 확인

### 2. 관리자 기능 테스트
- [ ] /admin/login 접속
- [ ] 관리자 로그인 (admin / 설정한_비밀번호)
- [ ] 대시보드 접속 확인
- [ ] 사이트 설정 저장 테스트
- [ ] 비밀번호 변경 테스트
- [ ] 로그 모니터링 확인

### 3. 사주 서비스 테스트
- [ ] 정통사주 입력 및 결과 확인
- [ ] 궁합 입력 및 결과 확인
- [ ] 이미지 업로드 테스트
- [ ] WebP 변환 동작 확인

### 4. 성능 테스트
- [ ] 페이지 로딩 속도 확인
- [ ] 이미지 최적화 확인
- [ ] Rate Limiting 동작 확인

### 5. SEO 확인
- [ ] 메타 태그 확인 (View Page Source)
- [ ] robots.txt 확인
- [ ] sitemap.xml 생성 및 확인
- [ ] Google Search Console 등록
- [ ] Google Analytics 설정

## 🔍 문제 해결

### 로그 확인
```bash
# 애플리케이션 로그
sudo journalctl -u myeongwolheon -f

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log

# PostgreSQL 로그
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 서비스 재시작
```bash
# FastAPI 애플리케이션
sudo systemctl restart myeongwolheon

# Nginx
sudo systemctl restart nginx

# PostgreSQL
sudo systemctl restart postgresql
```

### 데이터베이스 백업
```bash
# 백업
pg_dump -U myeongwol_user -h localhost myeongwolheon_db > backup_$(date +%Y%m%d).sql

# 복원
psql -U myeongwol_user -h localhost myeongwolheon_db < backup_20250114.sql
```

## ⚠️ 보안 체크리스트

- [ ] .env 파일 권한 설정 (chmod 600 .env)
- [ ] DEBUG=False 확인
- [ ] ENVIRONMENT=production 확인
- [ ] 강력한 비밀번호 사용 확인
- [ ] SSH 키 기반 인증 사용
- [ ] 정기적인 백업 설정
- [ ] fail2ban 설치 (무차별 대입 공격 방지)
- [ ] PostgreSQL 외부 접속 차단 확인

## 📊 모니터링

### 추가 설치 권장
```bash
# 시스템 모니터링
sudo apt install htop

# 로그 모니터링
sudo apt install logwatch
```

## 🎯 완료!

모든 체크리스트를 완료하셨다면 배포 완료입니다!

사이트 주소: https://your-domain.com
관리자 페이지: https://your-domain.com/admin
