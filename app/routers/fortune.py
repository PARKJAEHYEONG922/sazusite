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

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/fortune/newyear2026", response_class=HTMLResponse)
async def newyear2026_form(
    request: Request,
    db: Session = Depends(get_db)
):
    """2026 신년운세 입력 폼 페이지"""
    site_service = SiteService(db)
    site_config = site_service.get_site_config()

    # 2026 신년운세용 가상 서비스 객체 생성
    class NewYear2026Service:
        service_code = "newyear2026"
        service_name = "2026 신년운세"
        character_name = "야광묘"
        character_image = "/static/images/character_newyear.png"
        description = "2026년 한 해의 운세를 상세히 알려드립니다"
        is_active = True

    service = NewYear2026Service()

    return templates.TemplateResponse(
        "public/fortune_form.html",
        {
            "request": request,
            "site_config": site_config,
            "service": service
        }
    )


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
            "public/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": "서비스를 찾을 수 없거나 비활성화되었습니다."
            },
            status_code=404
        )

    return templates.TemplateResponse(
        "public/fortune_form.html",
        {
            "request": request,
            "site_config": site_config,
            "service": service
        }
    )


@router.post("/fortune/newyear2026", response_class=HTMLResponse)
async def newyear2026_result(
    request: Request,
    name: Optional[str] = Form(None),
    birthdate: date = Form(...),
    gender: str = Form(...),
    db: Session = Depends(get_db)
):
    """2026 신년운세 생성 및 결과 페이지"""
    site_service = SiteService(db)
    site_config = site_service.get_site_config()

    # 2026 신년운세용 가상 서비스 객체 생성
    class NewYear2026Service:
        service_code = "newyear2026"
        service_name = "2026 신년운세"
        character_name = "야광묘"
        character_image = "/static/images/character_newyear.png"
        description = "2026년 한 해의 운세를 상세히 알려드립니다"
        is_active = True

    service = NewYear2026Service()

    # 요청 데이터 구성
    request_data = {
        "name": name,
        "birthdate": birthdate,
        "gender": gender
    }

    # 운세 생성
    fortune_service = FortuneService(db)

    try:
        result = fortune_service.get_or_create_fortune("newyear2026", request_data)

        return templates.TemplateResponse(
            "public/fortune_result.html",
            {
                "request": request,
                "site_config": site_config,
                "service": service,
                "result": result,
                "is_cached": result["is_cached"],
                "today": result["date"]
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            "public/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": f"운세 생성 중 오류가 발생했습니다: {str(e)}"
            },
            status_code=500
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
    site_service = SiteService(db)
    site_config = site_service.get_site_config()
    service = site_service.get_service_by_code(service_code)

    if not service or not service.is_active:
        return templates.TemplateResponse(
            "public/error.html",
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
                "public/error.html",
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
    elif service_code == "match":
        request_data["partner_name"] = partner_name
        request_data["partner_birthdate"] = partner_birthdate
        request_data["partner_gender"] = partner_gender
        request_data["calendar"] = calendar
        request_data["partner_calendar"] = partner_calendar
    elif service_code == "dream":
        request_data["dream_content"] = dream_content

    # 운세 생성
    fortune_service = FortuneService(db)

    try:
        result = fortune_service.get_or_create_fortune(service_code, request_data)

        # 사주 서비스인 경우 전용 템플릿 사용
        template_name = "public/saju_result.html" if service_code == "saju" else "public/fortune_result.html"

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
        return templates.TemplateResponse(
            "public/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": f"운세 생성 중 오류가 발생했습니다: {str(e)}"
            },
            status_code=500
        )
