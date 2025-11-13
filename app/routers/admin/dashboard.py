"""
관리자 대시보드 라우터
"""
from fastapi import APIRouter, Request, Depends, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional

from app.database import get_db
from app.models.fortune_result import FortuneResult
from app.services.site_service import SiteService
from app.utils.security import verify_token

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


def check_admin(admin_token: Optional[str] = Cookie(None)):
    """관리자 인증 확인"""
    if not admin_token:
        return None
    username = verify_token(admin_token)
    return username


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None)
):
    """관리자 대시보드"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    # 오늘 통계
    today = date.today()

    total_today = db.query(FortuneResult).filter(
        FortuneResult.date == today
    ).count()

    # 서비스별 조회수
    stats = {}
    for service_code in ["today", "saju", "match", "dream"]:
        count = db.query(FortuneResult).filter(
            FortuneResult.service_code == service_code,
            FortuneResult.date == today
        ).count()
        stats[f"{service_code}_count"] = count

    # 최근 조회 로그
    recent_logs = db.query(FortuneResult).order_by(
        FortuneResult.created_at.desc()
    ).limit(10).all()

    # 사이트 설정
    site_service = SiteService(db)
    site_config = site_service.get_site_config()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "username": username,
            "site_config": site_config,
            "total_today": total_today,
            "stats": stats,
            "recent_logs": recent_logs
        }
    )


@router.get("/settings/site", response_class=HTMLResponse)
async def site_settings(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None)
):
    """사이트 설정 페이지"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    site_service = SiteService(db)
    site_config = site_service.get_site_config()

    return templates.TemplateResponse(
        "admin/settings_site.html",
        {
            "request": request,
            "username": username,
            "config": site_config,
            "success": None,
            "error": None
        }
    )


@router.post("/settings/site", response_class=HTMLResponse)
async def update_site_settings(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    site_name: str = Form(...),
    main_title: str = Form(...),
    main_subtitle: str = Form(...),
    footer_text: str = Form(...),
    adsense_client_id: Optional[str] = Form(None),
    adsense_slot_main: Optional[str] = Form(None),
    adsense_slot_result: Optional[str] = Form(None)
):
    """사이트 설정 업데이트"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    try:
        site_service = SiteService(db)
        updates = {
            "site_name": site_name,
            "main_title": main_title,
            "main_subtitle": main_subtitle,
            "footer_text": footer_text,
            "adsense_client_id": adsense_client_id if adsense_client_id else None,
            "adsense_slot_main": adsense_slot_main if adsense_slot_main else None,
            "adsense_slot_result": adsense_slot_result if adsense_slot_result else None
        }
        site_config = site_service.update_site_config(updates)

        return templates.TemplateResponse(
            "admin/settings_site.html",
            {
                "request": request,
                "username": username,
                "config": site_config,
                "success": "설정이 성공적으로 저장되었습니다.",
                "error": None
            }
        )
    except Exception as e:
        site_service = SiteService(db)
        site_config = site_service.get_site_config()

        return templates.TemplateResponse(
            "admin/settings_site.html",
            {
                "request": request,
                "username": username,
                "config": site_config,
                "success": None,
                "error": f"저장 중 오류가 발생했습니다: {str(e)}"
            }
        )


@router.get("/settings/services", response_class=HTMLResponse)
async def services_settings(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None)
):
    """서비스 설정 페이지"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    site_service = SiteService(db)
    services = site_service.get_all_services()

    return templates.TemplateResponse(
        "admin/settings_services.html",
        {
            "request": request,
            "username": username,
            "services": services,
            "success": None,
            "error": None
        }
    )


@router.post("/settings/services/{service_code}", response_class=HTMLResponse)
async def update_service_settings(
    request: Request,
    service_code: str,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    title: str = Form(...),
    subtitle: str = Form(...),
    description: str = Form(...),
    character_name: str = Form(...),
    character_emoji: str = Form(...),
    is_active: Optional[str] = Form(None)
):
    """서비스 설정 업데이트"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    try:
        site_service = SiteService(db)
        updates = {
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "character_name": character_name,
            "character_emoji": character_emoji,
            "is_active": is_active == "on"
        }
        site_service.update_service_config(service_code, updates)

        services = site_service.get_all_services()

        return templates.TemplateResponse(
            "admin/settings_services.html",
            {
                "request": request,
                "username": username,
                "services": services,
                "success": f"{title} 설정이 성공적으로 저장되었습니다.",
                "error": None
            }
        )
    except Exception as e:
        site_service = SiteService(db)
        services = site_service.get_all_services()

        return templates.TemplateResponse(
            "admin/settings_services.html",
            {
                "request": request,
                "username": username,
                "services": services,
                "success": None,
                "error": f"저장 중 오류가 발생했습니다: {str(e)}"
            }
        )
