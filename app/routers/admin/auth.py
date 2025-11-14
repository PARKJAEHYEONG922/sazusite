"""
관리자 인증 라우터
"""
from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService
from app.utils.security import create_access_token
from app.middleware.rate_limiter import admin_rate_limiter

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """관리자 로그인 페이지"""
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request}
    )


@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """관리자 로그인 처리"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(username, password)

    if not user:
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": {},
                "error": "아이디 또는 비밀번호가 올바르지 않습니다."
            },
            status_code=401
        )

    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.username})

    # 대시보드로 리다이렉트
    redirect = RedirectResponse(url="/admin/dashboard", status_code=303)
    redirect.set_cookie(
        key="admin_token",
        value=access_token,
        httponly=True,
        max_age=86400  # 24시간
    )
    return redirect


@router.get("/logout")
async def logout():
    """관리자 로그아웃"""
    redirect = RedirectResponse(url="/admin/login", status_code=303)
    redirect.delete_cookie("admin_token")
    return redirect
