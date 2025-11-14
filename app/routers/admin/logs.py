"""
관리자 - 로그 조회 라우터
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.site_service import SiteService
from app.services.log_service import LogService
from app.routers.admin.dashboard import check_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/logs", response_class=HTMLResponse)
async def logs_page(
    request: Request,
    tab: str = "errors",
    db: Session = Depends(get_db),
    admin=Depends(check_admin)
):
    """로그 조회 페이지"""
    site_service = SiteService(db)
    log_service = LogService(db)

    # 탭별 데이터 조회
    if tab == "errors":
        recent_errors = log_service.get_recent_errors(limit=50)
        error_stats = log_service.get_error_stats_by_type(hours=24)
        error_count_24h = log_service.get_error_count(hours=24)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "tab": tab,
                "errors": recent_errors,
                "error_stats": error_stats,
                "error_count_24h": error_count_24h
            }
        )

    elif tab == "api":
        recent_api = log_service.get_recent_api_usage(limit=50)
        api_stats = log_service.get_api_usage_stats(days=7)
        api_by_service = log_service.get_api_usage_by_service(days=7)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "tab": tab,
                "api_logs": recent_api,
                "api_stats": api_stats,
                "api_by_service": api_by_service
            }
        )

    elif tab == "access":
        recent_access = log_service.get_recent_access(limit=50)
        access_stats = log_service.get_access_stats(days=7)
        popular_services = log_service.get_popular_services(days=7)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "tab": tab,
                "access_logs": recent_access,
                "access_stats": access_stats,
                "popular_services": popular_services
            }
        )

    elif tab == "rate-limit":
        recent_violations = log_service.get_recent_rate_limit_violations(limit=50)
        rate_limit_stats = log_service.get_rate_limit_stats(days=7)
        top_violators = log_service.get_top_violators(days=7, limit=10)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "tab": tab,
                "rate_limit_logs": recent_violations,
                "rate_limit_stats": rate_limit_stats,
                "top_violators": top_violators
            }
        )

    # 기본값: 에러 탭
    return templates.TemplateResponse(
        "admin/logs.html",
        {
            "request": request,
            "site_config": site_service.get_site_config(),
            "admin": admin,
            "tab": "errors",
            "errors": log_service.get_recent_errors(limit=50),
            "error_stats": log_service.get_error_stats_by_type(hours=24),
            "error_count_24h": log_service.get_error_count(hours=24)
        }
    )
