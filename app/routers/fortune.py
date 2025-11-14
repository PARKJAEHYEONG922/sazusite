"""
운세 생성 공개 라우터
"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional

from app.database import get_db
from app.services.fortune_service import FortuneService
from app.services.site_service import SiteService
from app.middleware import rate_limiter
from app.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/fortune/{service_code}", response_class=HTMLResponse)
async def fortune_form(
    request: Request,
    service_code: str,
    db: Session = Depends(get_db)
):
    """운세 입력 폼 페이지"""
    site_service = SiteService(db)
    site_config = site_service.get_site_config()
    service = site_service.get_service_by_code(service_code)

    if not service or not service.is_active:
        return templates.TemplateResponse(
            "results/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": "서비스를 찾을 수 없거나 비활성화되었습니다."
            },
            status_code=404
        )

    # 개별 시작 페이지 템플릿 사용 (각 서비스마다 pages/{code}.html)
    template_name = f"pages/{service_code}.html"

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "site_config": site_config,
            "service": service
        }
    )


@router.post("/fortune/{service_code}", response_class=HTMLResponse)
async def fortune_result(
    request: Request,
    service_code: str,
    name: Optional[str] = Form(None),
    birthdate: Optional[date] = Form(None),
    gender: Optional[str] = Form(None),
    birth_time: Optional[str] = Form(None),
    calendar: str = Form("solar"),
    partner_name: Optional[str] = Form(None),
    partner_birthdate: Optional[date] = Form(None),
    partner_gender: Optional[str] = Form(None),
    partner_calendar: str = Form("solar"),
    dream_content: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """운세 생성 및 결과 페이지"""
    # Rate Limiting 체크 (API 비용 폭탄 방지) + 위반 로깅
    rate_limiter.check_rate_limit(request, db)

    site_service = SiteService(db)
    site_config = site_service.get_site_config()
    service = site_service.get_service_by_code(service_code)

    if not service or not service.is_active:
        return templates.TemplateResponse(
            "results/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": "서비스를 찾을 수 없거나 비활성화되었습니다."
            },
            status_code=404
        )

    # 꿈해몽이 아닌 서비스는 생년월일과 성별 필수
    if service_code != "dream":
        if not birthdate or not gender:
            return templates.TemplateResponse(
                "results/error.html",
                {
                    "request": request,
                    "site_config": site_config,
                    "message": "생년월일과 성별은 필수 입력 항목입니다."
                },
                status_code=400
            )

    # 요청 데이터 구성
    request_data = {
        "name": name,
        "birthdate": birthdate,
        "gender": gender
    }

    # 서비스별 추가 데이터
    if service_code == "today":
        request_data["birth_time"] = birth_time
        request_data["calendar"] = calendar
    elif service_code == "saju":
        request_data["birth_time"] = birth_time
        request_data["calendar"] = calendar
    elif service_code == "newyear2026":
        request_data["birth_time"] = birth_time
    elif service_code == "match":
        request_data["partner_name"] = partner_name
        request_data["partner_birthdate"] = partner_birthdate
        request_data["partner_gender"] = partner_gender
        request_data["calendar"] = calendar
        request_data["partner_calendar"] = partner_calendar
    elif service_code == "dream":
        request_data["dream_content"] = dream_content

    # 운세 생성
    client_ip = request.client.host if request.client else "unknown"
    fortune_service = FortuneService(db, client_ip=client_ip)

    try:
        result = fortune_service.get_or_create_fortune(service_code, request_data)

        # 개별 결과 템플릿 사용 (각 서비스마다 results/{code}_result.html)
        template_name = f"results/{service_code}_result.html"

        return templates.TemplateResponse(
            template_name,
            {
                "request": request,
                "site_config": site_config,
                "service": service,
                "result": result,
                "request_data": request_data,
                "is_cached": result["is_cached"],
                "today": result["date"]
            }
        )

    except Exception as e:
        # 에러 로깅 (DB에 저장)
        from app.utils.logger import log_exception
        log_exception(db, e, request, service_code=service_code)

        # 개발 환경에서만 상세 에러 표시, 프로덕션에서는 숨김
        if settings.environment == "development":
            error_message = f"운세 생성 중 오류가 발생했습니다: {str(e)}"
        else:
            error_message = "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            # 프로덕션 환경에서는 서버 로그에도 기록
            import logging
            logging.error(f"Fortune generation error: {str(e)}", exc_info=True)

        return templates.TemplateResponse(
            "results/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": error_message
            },
            status_code=500
        )
