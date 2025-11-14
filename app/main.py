"""
명월헌 FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.site_service import SiteService
from app.routers import fortune
from app.routers.admin import auth, dashboard, logs
from app.middleware.logging_middleware import LoggingMiddleware

# FastAPI 앱 생성
app = FastAPI(
    title="명월헌",
    description="AI 기반 운세 서비스",
    version="1.0.0"
)

# 미들웨어 등록
app.add_middleware(LoggingMiddleware)

# 라우터 등록
app.include_router(fortune.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(logs.router)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """메인 페이지"""
    from datetime import date
    site_service = SiteService(db)
    site_config = site_service.get_site_config()
    services = site_service.get_active_services()

    return templates.TemplateResponse(
        "results/index.html",
        {
            "request": request,
            "site_config": site_config,
            "services": services,
            "today": date.today().isoformat()
        }
    )


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "myeongwolheon"}


@app.get("/api/test")
async def api_test():
    """API 테스트"""
    return {
        "success": True,
        "message": "명월헌 API가 정상 작동 중입니다!",
        "version": "1.0.0"
    }


@app.get("/robots.txt", response_class=Response)
async def robots_txt():
    """robots.txt 제공"""
    content = """# robots.txt for 명월헌 (myeongwolheon.kr)
# 검색엔진 크롤러 설정

# 모든 검색엔진 허용
User-agent: *
Allow: /

# 관리자 페이지 차단
Disallow: /admin/
Disallow: /admin

# API 엔드포인트 차단 (검색 결과에 노출 불필요)
Disallow: /api/

# 사이트맵 위치
Sitemap: https://myeongwolheon.kr/sitemap.xml

# 크롤링 속도 제한 (서버 부하 방지)
Crawl-delay: 1
"""
    return Response(content=content, media_type="text/plain")


@app.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(db: Session = Depends(get_db)):
    """동적 sitemap.xml 생성"""
    from datetime import datetime

    site_service = SiteService(db)
    site_config = site_service.get_site_config()

    # 기본 URL (배포 시 자동으로 설정된 도메인 사용)
    base_url = site_config.site_url if site_config and site_config.site_url else "https://myeongwolheon.kr"

    # 현재 날짜 (lastmod 용)
    today = datetime.now().strftime("%Y-%m-%d")

    # 사이트맵 XML 생성
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <!-- 메인 페이지 -->
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>

    <!-- 오늘의 운세 -->
    <url>
        <loc>{base_url}/fortune/today</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>

    <!-- 2026 신년운세 -->
    <url>
        <loc>{base_url}/fortune/newyear2026</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>

    <!-- 정통 사주팔자 -->
    <url>
        <loc>{base_url}/fortune/saju</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- 사주궁합 -->
    <url>
        <loc>{base_url}/fortune/match</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>

    <!-- 꿈해몽 -->
    <url>
        <loc>{base_url}/fortune/dream</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>
"""

    return Response(content=xml_content, media_type="application/xml")


# 앱 시작 시 실행
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    from app.database import create_tables
    from app.utils.env_validator import validate_environment

    # 환경 설정 검증 (필수!) - 인코딩 설정도 내부에서 처리됨
    validate_environment()

    create_tables()
    print("[OK] Myeongwolheon server started!")
    print("[URL] http://localhost:8000")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
