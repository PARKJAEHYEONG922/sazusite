"""
명월헌 FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.site_service import SiteService
from app.routers import fortune
from app.routers.admin import auth, dashboard

# FastAPI 앱 생성
app = FastAPI(
    title="명월헌",
    description="AI 기반 운세 서비스",
    version="1.0.0"
)

# 라우터 등록
app.include_router(fortune.router)
app.include_router(auth.router)
app.include_router(dashboard.router)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """메인 페이지"""
    site_service = SiteService(db)
    site_config = site_service.get_site_config()
    services = site_service.get_active_services()

    return templates.TemplateResponse(
        "public/index.html",
        {
            "request": request,
            "site_config": site_config,
            "services": services
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


# 앱 시작 시 실행
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    from app.database import create_tables
    import sys
    import io
    # Windows 인코딩 문제 해결
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    create_tables()
    print("[OK] Myeongwolheon server started!")
    print("[URL] http://localhost:8000")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
