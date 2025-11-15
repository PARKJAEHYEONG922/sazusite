"""
운세 생성 공개 라우터
"""
from fastapi import APIRouter, Request, Depends, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
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


@router.get("/loading/{service_code}/{share_code}", response_class=HTMLResponse)
async def loading_page(
    request: Request,
    service_code: str,
    share_code: str,
    db: Session = Depends(get_db)
):
    """로딩 페이지 (광고 표시 + 자동 리디렉션)"""
    site_service = SiteService(db)
    site_config = site_service.get_site_config()
    service = site_service.get_service_by_code(service_code)

    if not service:
        return templates.TemplateResponse(
            "results/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": "서비스를 찾을 수 없습니다."
            },
            status_code=404
        )

    # 결과 페이지 URL 생성
    result_url = f"/pages/results/{service_code}/{share_code}"

    return templates.TemplateResponse(
        "loading.html",
        {
            "request": request,
            "site_config": site_config,
            "service": service,
            "share_code": share_code,
            "result_url": result_url
        }
    )


@router.get("/api/fortune/status/{share_code}")
async def check_fortune_status(
    share_code: str,
    db: Session = Depends(get_db)
):
    """운세 생성 상태 체크 API (AJAX 폴링용)"""
    from app.models import FortuneResult

    result = db.query(FortuneResult).filter(
        FortuneResult.share_code == share_code
    ).first()

    # 레코드가 아직 없으면 pending 상태 반환 (404 대신 200 OK)
    if not result:
        return JSONResponse(content={
            "status": "pending",
            "message": "운세 생성을 준비 중입니다..."
        })

    # 에러 상태 체크
    if result.status == "error":
        return JSONResponse(content={
            "status": "error",
            "message": result.error_message or "AI 분석 중 오류가 발생했습니다."
        })

    # 완료 상태 체크
    if result.result_text or result.status == "completed":
        return JSONResponse(content={
            "status": "completed",
            "message": "분석이 완료되었습니다!"
        })

    # 처리 중
    return JSONResponse(content={
        "status": result.status or "processing",
        "message": "분석 중입니다..."
    })


@router.get("/pages/results/{service_code}/{share_code}", response_class=HTMLResponse)
async def view_fortune_result(
    request: Request,
    service_code: str,
    share_code: str,
    db: Session = Depends(get_db)
):
    """저장된 운세 결과 조회 (공유용 고유 URL)"""
    from app.models.fortune_result import FortuneResult

    site_service = SiteService(db)
    site_config = site_service.get_site_config()
    service = site_service.get_service_by_code(service_code)

    if not service:
        return templates.TemplateResponse(
            "results/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": "서비스를 찾을 수 없습니다."
            },
            status_code=404
        )

    # DB에서 share_code로 결과 조회
    fortune_result = db.query(FortuneResult).filter(
        FortuneResult.share_code == share_code,
        FortuneResult.service_code == service_code
    ).first()

    if not fortune_result:
        return templates.TemplateResponse(
            "results/error.html",
            {
                "request": request,
                "site_config": site_config,
                "message": "운세 결과를 찾을 수 없습니다."
            },
            status_code=404
        )

    # 결과 데이터 구성 (템플릿에서 사용하는 키 이름에 맞춤)
    result = {
        "id": fortune_result.id,
        "share_code": fortune_result.share_code,
        "result_text": fortune_result.result_text,
        "date": fortune_result.date.isoformat(),
        "is_cached": fortune_result.is_from_cache  # DB에서 실제 캐시 여부 가져오기
    }

    # 사주 서비스인 경우 사주 계산 데이터 추가
    if service_code == "saju":
        from app.services.saju_calculator import SajuCalculator
        from datetime import datetime

        calculator = SajuCalculator()
        request_data = fortune_result.request_payload
        birthdate = datetime.fromisoformat(str(request_data["birthdate"])).date()
        birth_time = request_data.get("birth_time")
        calendar_type = request_data.get("calendar", "solar")
        gender = request_data["gender"]
        name = request_data.get("name", "고객")

        saju_data = calculator.calculate_saju(
            birthdate=birthdate,
            birth_time=birth_time,
            calendar_type=calendar_type,
            gender=gender
        )
        saju_data["name"] = name
        result["saju_data"] = saju_data

    # 개별 결과 템플릿 사용
    template_name = f"results/{service_code}_result.html"

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "site_config": site_config,
            "service": service,
            "result": result,
            "request_data": fortune_result.request_payload,
            "data": fortune_result.request_payload,  # 템플릿 호환성을 위해 data도 전달
            "is_cached": fortune_result.is_from_cache,  # DB에서 실제 캐시 여부 가져오기
            "today": fortune_result.date  # date 객체 그대로 전달 (템플릿에서 strftime 사용)
        }
    )


@router.post("/fortune/{service_code}")
async def fortune_result(
    request: Request,
    service_code: str,
    background_tasks: BackgroundTasks,
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
    """운세 생성 및 결과 페이지 (비동기 처리)"""
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

    # 캐시 확인 (동기)
    client_ip = request.client.host if request.client else "unknown"
    fortune_service = FortuneService(db, client_ip=client_ip)

    # user_key 생성
    user_key = fortune_service.generate_user_key(service_code, request_data)

    # 오늘 날짜로 캐시 조회
    from datetime import date as dt_date
    today = dt_date.today()
    cached = fortune_service.find_cached_result(service_code, user_key, today)

    import logging
    logging.warning(f"[DEBUG] Cache check - service: {service_code}, user_key: {user_key[:20]}..., found: {cached is not None}")

    if cached:
        # 캐시가 있으면 바로 결과 페이지로 리다이렉트 (로딩 페이지 건너뛰기)
        redirect_url = f"/pages/results/{service_code}/{cached.share_code}"
        logging.warning(f"[DEBUG] Cache HIT! Redirecting to: {redirect_url}")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=redirect_url, status_code=303)

    # 캐시가 없으면 새로 생성 (비동기)
    import secrets
    share_code = secrets.token_urlsafe(8)

    # 백그라운드에서 운세 생성 (비동기)
    def generate_fortune_bg():
        # 새로운 DB 세션 생성 (백그라운드 태스크용)
        from app.database import SessionLocal
        from app.models import FortuneResult
        import logging

        bg_db = SessionLocal()
        try:
            fortune_service = FortuneService(bg_db, client_ip=client_ip)
            fortune_service.get_or_create_fortune(service_code, request_data, share_code=share_code)
            bg_db.commit()
        except Exception as e:
            bg_db.rollback()
            logging.error(f"Background fortune generation error: {str(e)}", exc_info=True)

            # DB에 에러 상태 기록
            try:
                # share_code로 레코드 찾기 (이미 생성된 경우)
                result = bg_db.query(FortuneResult).filter(
                    FortuneResult.share_code == share_code
                ).first()

                if result:
                    # 기존 레코드 업데이트
                    result.status = "error"
                    result.error_message = f"AI 분석 중 오류가 발생했습니다: {str(e)}"
                else:
                    # 새 에러 레코드 생성
                    from datetime import date as dt_date
                    # request_data를 JSON 직렬화 가능한 형태로 변환
                    serializable_data = fortune_service._make_json_serializable(request_data)
                    error_result = FortuneResult(
                        service_code=service_code,
                        user_key="error",  # 임시 키
                        share_code=share_code,
                        date=dt_date.today(),
                        request_payload=serializable_data,
                        result_text=None,
                        status="error",
                        error_message=f"AI 분석 중 오류가 발생했습니다: {str(e)}",
                        is_from_cache=False
                    )
                    bg_db.add(error_result)

                bg_db.commit()
            except Exception as db_error:
                logging.error(f"Failed to save error status to DB: {str(db_error)}", exc_info=True)
                bg_db.rollback()
        finally:
            bg_db.close()

    # 백그라운드 태스크 등록
    background_tasks.add_task(generate_fortune_bg)

    # 즉시 로딩 페이지로 리디렉션 (광고 표시)
    redirect_url = f"/loading/{service_code}/{share_code}"
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=redirect_url, status_code=303)
