"""
관리자 계정 관리 라우터
"""
from fastapi import APIRouter, Request, Depends, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.admin_user import AdminUser
from app.services.auth_service import AuthService
from app.utils.security import verify_token, get_password_hash, verify_password

router = APIRouter(prefix="/admin", tags=["admin_account"])
templates = Jinja2Templates(directory="app/templates")


def check_admin(admin_token: Optional[str] = Cookie(None)):
    """관리자 인증 확인"""
    if not admin_token:
        return None
    username = verify_token(admin_token)
    return username


@router.get("/settings/account", response_class=HTMLResponse)
async def account_settings(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None)
):
    """계정 설정 페이지"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    return templates.TemplateResponse(
        "admin/settings_account.html",
        {
            "request": request,
            "username": username
        }
    )


@router.post("/settings/account/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """비밀번호 변경"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    # 디버깅 로그
    print(f"\n{'='*60}")
    print(f"[비밀번호 변경 시도]")
    print(f"사용자: {username}")
    print(f"현재 비밀번호 길이: {len(current_password)}")
    print(f"새 비밀번호 길이: {len(new_password)}")
    print(f"비밀번호 확인 길이: {len(confirm_password)}")
    print(f"{'='*60}\n")

    try:
        # 관리자 조회
        admin_user = db.query(AdminUser).filter(
            AdminUser.username == username
        ).first()

        if not admin_user:
            print("❌ [오류] 관리자 사용자를 찾을 수 없음")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [시스템 오류] 관리자를 찾을 수 없습니다."
                }
            )

        # 현재 비밀번호 확인
        print(f"🔐 현재 비밀번호 검증 중...")
        password_match = verify_password(current_password, admin_user.password_hash)
        print(f"검증 결과: {'✅ 일치' if password_match else '❌ 불일치'}")

        if not password_match:
            print("❌ [실패] 현재 비밀번호가 일치하지 않음")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [현재 비밀번호 오류] 현재 비밀번호가 일치하지 않습니다. 다시 확인해주세요."
                }
            )

        # 새 비밀번호 검증
        print(f"🔍 새 비밀번호 유효성 검증 중...")

        if new_password != confirm_password:
            print("❌ [실패] 새 비밀번호와 확인 비밀번호 불일치")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [비밀번호 확인 오류] 새 비밀번호와 비밀번호 확인이 일치하지 않습니다."
                }
            )

        if len(new_password) < 12:
            print(f"❌ [실패] 비밀번호 길이 부족 (현재: {len(new_password)}자)")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": f"❌ [새 비밀번호 오류] 새 비밀번호는 최소 12자 이상이어야 합니다. (현재: {len(new_password)}자)"
                }
            )

        # 비밀번호 복잡도 검증
        if not any(c.isupper() for c in new_password):
            print("❌ [실패] 영문 대문자 미포함")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [새 비밀번호 오류] 새 비밀번호에 영문 대문자를 포함해야 합니다."
                }
            )

        if not any(c.islower() for c in new_password):
            print("❌ [실패] 영문 소문자 미포함")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [새 비밀번호 오류] 새 비밀번호에 영문 소문자를 포함해야 합니다."
                }
            )

        if not any(c.isdigit() for c in new_password):
            print("❌ [실패] 숫자 미포함")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [새 비밀번호 오류] 새 비밀번호에 숫자를 포함해야 합니다."
                }
            )

        if not any(c in "!@#$%^&*()_+-=[]{};<>?,./" for c in new_password):
            print("❌ [실패] 특수문자 미포함")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [새 비밀번호 오류] 새 비밀번호에 특수문자를 포함해야 합니다."
                }
            )

        # 현재 비밀번호와 같은지 확인
        if current_password == new_password:
            print("❌ [실패] 현재 비밀번호와 동일한 비밀번호 사용")
            return templates.TemplateResponse(
                "admin/settings_account.html",
                {
                    "request": request,
                    "username": username,
                    "error": "❌ [새 비밀번호 오류] 현재 비밀번호와 다른 비밀번호를 사용하세요."
                }
            )

        # 비밀번호 업데이트
        print(f"✅ 모든 검증 통과! 비밀번호 변경 중...")
        admin_user.password_hash = get_password_hash(new_password)
        db.commit()
        print(f"✅ [성공] 비밀번호가 성공적으로 변경되었습니다!")
        print(f"{'='*60}\n")

        return templates.TemplateResponse(
            "admin/settings_account.html",
            {
                "request": request,
                "username": username,
                "success": "✅ 비밀번호가 성공적으로 변경되었습니다! 다음 로그인 시 새 비밀번호를 사용하세요."
            }
        )

    except Exception as e:
        db.rollback()
        print(f"❌ [예외 발생] {str(e)}")
        print(f"{'='*60}\n")
        return templates.TemplateResponse(
            "admin/settings_account.html",
            {
                "request": request,
                "username": username,
                "error": f"❌ [시스템 오류] 비밀번호 변경 중 오류가 발생했습니다: {str(e)}"
            }
        )
