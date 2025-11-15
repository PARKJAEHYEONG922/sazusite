"""
관리자 - 로그 조회 라우터
"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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
    period: int = 7,
    message: str = None,
    error: str = None,
    db: Session = Depends(get_db),
    admin=Depends(check_admin)
):
    """로그 조회 페이지"""
    site_service = SiteService(db)
    log_service = LogService(db)

    # period=0이면 전체 조회 (큰 숫자로 설정)
    days = 36500 if period == 0 else period  # 100년 = 전체로 간주

    # 탭별 데이터 조회
    if tab == "errors":
        recent_errors = log_service.get_recent_errors(limit=1000, hours=days*24)
        error_stats = log_service.get_error_stats_by_type(hours=days*24)
        error_count_period = log_service.get_error_count(hours=days*24)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "username": admin if admin else "Admin",
                "tab": tab,
                "period": period,
                "errors": recent_errors,
                "error_stats": error_stats,
                "error_count_24h": error_count_period,
                "message": message,
                "error": error
            }
        )

    elif tab == "api":
        recent_api = log_service.get_recent_api_usage(limit=1000, days=days)
        api_stats = log_service.get_api_usage_stats(days=days)
        api_by_service = log_service.get_api_usage_by_service(days=days)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "username": admin if admin else "Admin",
                "tab": tab,
                "period": period,
                "api_logs": recent_api,
                "api_stats": api_stats,
                "api_by_service": api_by_service,
                "message": message,
                "error": error
            }
        )

    elif tab == "access":
        # 최근 접속 내역은 처음 50개만 (더보기로 추가 로드)
        recent_access = log_service.get_recent_access(limit=50, offset=0)
        access_stats = log_service.get_access_stats(days=days)
        popular_services = log_service.get_popular_services(days=days)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "username": admin if admin else "Admin",
                "tab": tab,
                "period": period,
                "access_logs": recent_access,
                "access_stats": access_stats,
                "popular_services": popular_services,
                "message": message,
                "error": error
            }
        )

    elif tab == "rate-limit":
        recent_violations = log_service.get_recent_rate_limit_violations(limit=1000, days=days)
        rate_limit_stats = log_service.get_rate_limit_stats(days=days)
        top_violators = log_service.get_top_violators(days=days, limit=10)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "username": admin if admin else "Admin",
                "tab": tab,
                "period": period,
                "rate_limit_logs": recent_violations,
                "rate_limit_stats": rate_limit_stats,
                "top_violators": top_violators,
                "message": message,
                "error": error
            }
        )

    elif tab == "fortune-errors":
        fortune_errors = log_service.get_fortune_errors(limit=1000, days=days)
        fortune_error_stats = log_service.get_fortune_error_stats(days=days)

        return templates.TemplateResponse(
            "admin/logs.html",
            {
                "request": request,
                "site_config": site_service.get_site_config(),
                "admin": admin,
                "username": admin if admin else "Admin",
                "tab": tab,
                "period": period,
                "fortune_errors": fortune_errors,
                "fortune_error_stats": fortune_error_stats,
                "message": message,
                "error": error
            }
        )

    # 기본값: 에러 탭
    return templates.TemplateResponse(
        "admin/logs.html",
        {
            "request": request,
            "site_config": site_service.get_site_config(),
            "admin": admin,
            "username": admin if admin else "Admin",
            "tab": "errors",
            "period": period,
            "errors": log_service.get_recent_errors(limit=1000, hours=days*24),
            "error_stats": log_service.get_error_stats_by_type(hours=days*24),
            "error_count_24h": log_service.get_error_count(hours=days*24),
            "message": message,
            "error": error
        }
    )


@router.post("/admin/logs/delete/{log_type}")
async def delete_logs_by_type(
    log_type: str,
    request: Request,
    days: int = Form(...),
    period: int = Form(default=7),
    db: Session = Depends(get_db),
    admin=Depends(check_admin)
):
    """특정 타입의 로그 삭제"""
    try:
        log_service = LogService(db)

        # 로그 타입별 삭제
        deleted_count = 0
        if log_type == "errors":
            deleted_count = log_service.delete_error_logs(days)
            message = f"{deleted_count}개의 에러 로그가 삭제되었습니다. ({days}일 이상 경과)"
        elif log_type == "api":
            deleted_count = log_service.delete_api_logs(days)
            message = f"{deleted_count}개의 API 로그가 삭제되었습니다. ({days}일 이상 경과)"
        elif log_type == "access":
            deleted_count = log_service.delete_access_logs(days)
            message = f"{deleted_count}개의 접속 로그가 삭제되었습니다. ({days}일 이상 경과)"
        elif log_type == "rate-limit":
            deleted_count = log_service.delete_rate_limit_logs(days)
            message = f"{deleted_count}개의 Rate Limit 로그가 삭제되었습니다. ({days}일 이상 경과)"
        elif log_type == "fortune-errors":
            deleted_count = log_service.delete_fortune_errors(days)
            message = f"{deleted_count}개의 운세 생성 에러가 삭제되었습니다. ({days}일 이상 경과)"
        else:
            message = "잘못된 로그 타입입니다."

        # 탭으로 리다이렉트 (현재 period 유지)
        return RedirectResponse(
            url=f"/admin/logs?tab={log_type}&period={period}&message={message}",
            status_code=303
        )

    except Exception as e:
        error_msg = f"로그 삭제 중 오류가 발생했습니다: {str(e)}"
        return RedirectResponse(
            url=f"/admin/logs?tab={log_type}&period={period}&error={error_msg}",
            status_code=303
        )


@router.get("/admin/logs/load-more/{log_type}")
async def load_more_logs(
    log_type: str,
    offset: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin=Depends(check_admin)
):
    """더보기 - 로그 추가 로드 (AJAX)"""
    try:
        log_service = LogService(db)

        if log_type == "access":
            logs = log_service.get_recent_access(limit=limit, offset=offset)
            return JSONResponse({
                "success": True,
                "logs": [
                    {
                        "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "client_ip": log.client_ip,
                        "method": log.method,
                        "url": log.url,
                        "status_code": log.status_code,
                        "response_time_ms": log.response_time_ms,
                        "user_agent": log.user_agent,
                        "is_fortune_request": log.is_fortune_request,
                        "service_code": log.service_code
                    }
                    for log in logs
                ],
                "has_more": len(logs) == limit
            })

        elif log_type == "errors":
            logs = log_service.get_recent_errors(limit=limit, offset=offset)
            return JSONResponse({
                "success": True,
                "logs": [
                    {
                        "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "error_type": log.error_type,
                        "message": log.error_message,
                        "traceback": log.stack_trace,
                        "client_ip": log.client_ip,
                        "url": log.url
                    }
                    for log in logs
                ],
                "has_more": len(logs) == limit
            })

        elif log_type == "api":
            logs = log_service.get_recent_api_usage(limit=limit, offset=offset)
            return JSONResponse({
                "success": True,
                "logs": [
                    {
                        "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "service_code": log.service_code,
                        "model_name": log.model,
                        "input_tokens": log.prompt_tokens,
                        "output_tokens": log.completion_tokens,
                        "estimated_cost": round(log.estimated_cost or 0, 4),
                        "cache_hit": log.cache_hit,
                        "response_time_ms": log.response_time_ms
                    }
                    for log in logs
                ],
                "has_more": len(logs) == limit
            })

        elif log_type == "rate-limit":
            logs = log_service.get_recent_rate_limit_violations(limit=limit, offset=offset)
            return JSONResponse({
                "success": True,
                "logs": [
                    {
                        "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "client_ip": log.client_ip,
                        "limit_type": log.limit_type,
                        "url": log.url,
                        "attempt_count": log.current_count
                    }
                    for log in logs
                ],
                "has_more": len(logs) == limit
            })

        elif log_type == "fortune-errors":
            logs = log_service.get_fortune_errors(limit=limit, offset=offset)
            return JSONResponse({
                "success": True,
                "logs": [
                    {
                        "created_at": log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "service_code": log.service_code,
                        "share_code": log.share_code,
                        "error_message": log.error_message
                    }
                    for log in logs
                ],
                "has_more": len(logs) == limit
            })

        else:
            return JSONResponse({"success": False, "error": "잘못된 로그 타입"}, status_code=400)

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
