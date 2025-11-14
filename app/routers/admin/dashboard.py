"""
관리자 대시보드 라우터
"""
from fastapi import APIRouter, Request, Depends, Cookie, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from typing import Optional
import os
import shutil
from pathlib import Path
from PIL import Image

from app.database import get_db
from app.models.fortune_result import FortuneResult
from app.services.site_service import SiteService
from app.services.log_service import LogService
from app.utils.security import verify_token
from app.utils.image_utils import convert_to_webp, validate_image_ratio

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
    for service_code in ["today", "saju", "newyear2026", "match", "dream"]:
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

    # 로그 요약 정보 추가
    log_service = LogService(db)
    log_summary = log_service.get_dashboard_summary()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "username": username,
            "site_config": site_config,
            "total_today": total_today,
            "stats": stats,
            "recent_logs": recent_logs,
            "log_summary": log_summary
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
    site_url: Optional[str] = Form(None),
    site_logo_file: Optional[UploadFile] = File(None),
    site_favicon_file: Optional[UploadFile] = File(None),
    main_title: str = Form(...),
    main_subtitle: str = Form(...),
    footer_text: str = Form(...),
    # 배너 1
    banner_file_1: Optional[UploadFile] = File(None),
    banner_pc_file_1: Optional[UploadFile] = File(None),
    banner_title_1: Optional[str] = Form(None),
    banner_subtitle_1: Optional[str] = Form(None),
    banner_description_1: Optional[str] = Form(None),
    banner_link_1: Optional[str] = Form(None),
    # 배너 2
    banner_file_2: Optional[UploadFile] = File(None),
    banner_pc_file_2: Optional[UploadFile] = File(None),
    banner_title_2: Optional[str] = Form(None),
    banner_subtitle_2: Optional[str] = Form(None),
    banner_description_2: Optional[str] = Form(None),
    banner_link_2: Optional[str] = Form(None),
    # 배너 3
    banner_file_3: Optional[UploadFile] = File(None),
    banner_pc_file_3: Optional[UploadFile] = File(None),
    banner_title_3: Optional[str] = Form(None),
    banner_subtitle_3: Optional[str] = Form(None),
    banner_description_3: Optional[str] = Form(None),
    banner_link_3: Optional[str] = Form(None),
    # 배너 4
    banner_file_4: Optional[UploadFile] = File(None),
    banner_pc_file_4: Optional[UploadFile] = File(None),
    banner_title_4: Optional[str] = Form(None),
    banner_subtitle_4: Optional[str] = Form(None),
    banner_description_4: Optional[str] = Form(None),
    banner_link_4: Optional[str] = Form(None),
    # 서브배너 1
    sub_banner_file_1: Optional[UploadFile] = File(None),
    sub_banner_emoji_1: Optional[str] = Form(None),
    sub_banner_title_1: Optional[str] = Form(None),
    sub_banner_subtitle_1: Optional[str] = Form(None),
    sub_banner_description_1: Optional[str] = Form(None),
    sub_banner_link_1: Optional[str] = Form(None),
    # 서브배너 2
    sub_banner_file_2: Optional[UploadFile] = File(None),
    sub_banner_emoji_2: Optional[str] = Form(None),
    sub_banner_title_2: Optional[str] = Form(None),
    sub_banner_subtitle_2: Optional[str] = Form(None),
    sub_banner_description_2: Optional[str] = Form(None),
    sub_banner_link_2: Optional[str] = Form(None),
    # 서브배너 3
    sub_banner_file_3: Optional[UploadFile] = File(None),
    sub_banner_emoji_3: Optional[str] = Form(None),
    sub_banner_title_3: Optional[str] = Form(None),
    sub_banner_subtitle_3: Optional[str] = Form(None),
    sub_banner_description_3: Optional[str] = Form(None),
    sub_banner_link_3: Optional[str] = Form(None),
    # 서브배너 4
    sub_banner_file_4: Optional[UploadFile] = File(None),
    sub_banner_emoji_4: Optional[str] = Form(None),
    sub_banner_title_4: Optional[str] = Form(None),
    sub_banner_subtitle_4: Optional[str] = Form(None),
    sub_banner_description_4: Optional[str] = Form(None),
    sub_banner_link_4: Optional[str] = Form(None),
    # 애드센스
    adsense_client_id: Optional[str] = Form(None),
    adsense_slot_main: Optional[str] = Form(None),
    adsense_slot_result: Optional[str] = Form(None)
):
    """사이트 설정 업데이트"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    try:
        # 업로드 디렉토리 설정
        upload_dir = Path("app/static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 현재 설정 가져오기
        site_service = SiteService(db)
        current_config = site_service.get_site_config()

        # 사이트 로고 처리
        site_logo_url = None
        if site_logo_file and site_logo_file.filename:
            # 파일 확장자 확인
            file_ext = os.path.splitext(site_logo_file.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                raise ValueError("로고: 지원하지 않는 파일 형식입니다. (jpg, png, gif, webp, svg만 가능)")

            # 이미지 데이터 읽기
            image_data = await site_logo_file.read()

            # 기존 로고 파일들 삭제 (모든 확장자)
            for old_file in upload_dir.glob("site_logo.*"):
                old_file.unlink()

            # SVG는 원본 그대로, 나머지는 WebP 변환
            if file_ext == '.svg':
                # SVG는 그대로 저장
                new_filename = f"site_logo{file_ext}"
                file_path = upload_dir / new_filename
                with file_path.open("wb") as f:
                    f.write(image_data)
            else:
                # WebP로 변환하여 저장 (최대 너비 800px)
                from app.utils.image_utils import convert_to_webp
                file_path = convert_to_webp(
                    image_data,
                    upload_dir / "site_logo",
                    quality=90,
                    max_width=800
                )
                new_filename = os.path.basename(file_path)

            # URL 경로 저장 (캐시 우회를 위한 타임스탬프 추가)
            timestamp = int(datetime.now().timestamp())
            site_logo_url = f"/static/uploads/{new_filename}?v={timestamp}"
        else:
            # 파일 업로드가 없으면 기존 값 유지
            if current_config and current_config.site_logo:
                site_logo_url = current_config.site_logo

        # 사이트 파비콘 처리
        site_favicon_url = None
        if site_favicon_file and site_favicon_file.filename:
            # 파일 확장자 확인
            file_ext = os.path.splitext(site_favicon_file.filename)[1].lower()
            if file_ext not in ['.ico', '.png']:
                raise ValueError("파비콘: 지원하지 않는 파일 형식입니다. (.ico 또는 .png만 가능)")

            # 파일명 생성
            new_filename = f"favicon{file_ext}"
            file_path = upload_dir / new_filename

            # 기존 파일 삭제
            if file_path.exists():
                file_path.unlink()

            # 파일 저장
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(site_favicon_file.file, buffer)

            # URL 경로 저장 (캐시 우회를 위한 타임스탬프 추가)
            timestamp = int(datetime.now().timestamp())
            site_favicon_url = f"/static/uploads/{new_filename}?v={timestamp}"
        else:
            # 파일 업로드가 없으면 기존 값 유지
            if current_config and current_config.site_favicon:
                site_favicon_url = current_config.site_favicon

        # 배너 파일 매핑
        banner_files = {
            1: banner_file_1,
            2: banner_file_2,
            3: banner_file_3,
            4: banner_file_4
        }
        banner_pc_files = {
            1: banner_pc_file_1,
            2: banner_pc_file_2,
            3: banner_pc_file_3,
            4: banner_pc_file_4
        }
        banner_titles = {
            1: banner_title_1,
            2: banner_title_2,
            3: banner_title_3,
            4: banner_title_4
        }
        banner_subtitles = {
            1: banner_subtitle_1,
            2: banner_subtitle_2,
            3: banner_subtitle_3,
            4: banner_subtitle_4
        }
        banner_descriptions = {
            1: banner_description_1,
            2: banner_description_2,
            3: banner_description_3,
            4: banner_description_4
        }
        banner_links = {
            1: banner_link_1,
            2: banner_link_2,
            3: banner_link_3,
            4: banner_link_4
        }

        # 배너 설정 처리
        banner_updates = {}
        for i in range(1, 5):
            # 모바일 배너 파일 업로드 처리
            banner_file = banner_files[i]
            if banner_file and banner_file.filename:
                # 파일 확장자 확인
                file_ext = os.path.splitext(banner_file.filename)[1].lower()
                if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    raise ValueError(f"배너 {i}: 지원하지 않는 파일 형식입니다. (jpg, png, gif, webp만 가능)")

                # 이미지 데이터 읽기
                image_data = await banner_file.read()

                # 기존 배너 파일들 삭제 (모든 확장자)
                for old_file in upload_dir.glob(f"banner_{i}.*"):
                    old_file.unlink()

                # WebP로 변환 및 저장 (1200px 최대 너비)
                output_path = upload_dir / f"banner_{i}"
                convert_to_webp(image_data, output_path, quality=90, max_width=1200)

                # URL 경로 저장 (캐시 우회를 위한 타임스탬프 추가)
                timestamp = int(datetime.now().timestamp())
                banner_updates[f"banner_image_{i}"] = f"/static/uploads/banner_{i}.webp?v={timestamp}"
            else:
                # 파일 업로드가 없으면 기존 값 유지
                if current_config:
                    existing_value = getattr(current_config, f"banner_image_{i}", None)
                    if existing_value:
                        banner_updates[f"banner_image_{i}"] = existing_value

            # PC 배너 파일 업로드 처리
            banner_pc_file = banner_pc_files[i]
            if banner_pc_file and banner_pc_file.filename:
                # 파일 확장자 확인
                file_ext = os.path.splitext(banner_pc_file.filename)[1].lower()
                if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    raise ValueError(f"PC 배너 {i}: 지원하지 않는 파일 형식입니다. (jpg, png, gif, webp만 가능)")

                # 이미지 데이터 읽기
                image_data = await banner_pc_file.read()

                # 기존 PC 배너 파일들 삭제 (모든 확장자)
                for old_file in upload_dir.glob(f"banner_pc_{i}.*"):
                    old_file.unlink()

                # WebP로 변환 및 저장 (2100px 최대 너비 - 21:9 와이드 스크린 지원)
                output_path = upload_dir / f"banner_pc_{i}"
                convert_to_webp(image_data, output_path, quality=90, max_width=2100)

                # URL 경로 저장 (캐시 우회를 위한 타임스탬프 추가)
                timestamp = int(datetime.now().timestamp())
                banner_updates[f"banner_image_pc_{i}"] = f"/static/uploads/banner_pc_{i}.webp?v={timestamp}"
            else:
                # 파일 업로드가 없으면 기존 값 유지
                if current_config:
                    existing_value = getattr(current_config, f"banner_image_pc_{i}", None)
                    if existing_value:
                        banner_updates[f"banner_image_pc_{i}"] = existing_value

            # 텍스트 필드 업데이트
            banner_title = banner_titles[i]
            banner_subtitle = banner_subtitles[i]
            banner_description = banner_descriptions[i]
            banner_link = banner_links[i]

            if banner_title:
                banner_updates[f"banner_title_{i}"] = banner_title
            if banner_subtitle:
                banner_updates[f"banner_subtitle_{i}"] = banner_subtitle
            if banner_description:
                banner_updates[f"banner_description_{i}"] = banner_description
            if banner_link:
                banner_updates[f"banner_link_{i}"] = banner_link

        # 서브배너 파일 매핑
        sub_banner_files = {
            1: sub_banner_file_1,
            2: sub_banner_file_2,
            3: sub_banner_file_3,
            4: sub_banner_file_4
        }
        sub_banner_emojis = {
            1: sub_banner_emoji_1,
            2: sub_banner_emoji_2,
            3: sub_banner_emoji_3,
            4: sub_banner_emoji_4
        }
        sub_banner_titles = {
            1: sub_banner_title_1,
            2: sub_banner_title_2,
            3: sub_banner_title_3,
            4: sub_banner_title_4
        }
        sub_banner_subtitles = {
            1: sub_banner_subtitle_1,
            2: sub_banner_subtitle_2,
            3: sub_banner_subtitle_3,
            4: sub_banner_subtitle_4
        }
        sub_banner_descriptions = {
            1: sub_banner_description_1,
            2: sub_banner_description_2,
            3: sub_banner_description_3,
            4: sub_banner_description_4
        }
        sub_banner_links = {
            1: sub_banner_link_1,
            2: sub_banner_link_2,
            3: sub_banner_link_3,
            4: sub_banner_link_4
        }

        # 서브배너 설정 처리
        sub_banner_updates = {}
        for i in range(1, 5):
            # 파일 업로드 처리 (이미지 및 비디오)
            sub_banner_file = sub_banner_files[i]
            if sub_banner_file and sub_banner_file.filename:
                # 파일 확장자 확인
                file_ext = os.path.splitext(sub_banner_file.filename)[1].lower()
                if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm']:
                    raise ValueError(f"서브배너 {i}: 지원하지 않는 파일 형식입니다. (이미지: jpg, png, gif, webp / 동영상: mp4, webm)")

                # 기존 서브배너 파일들 삭제 (모든 확장자)
                for old_file in upload_dir.glob(f"sub_banner_{i}.*"):
                    old_file.unlink()

                # 동영상은 그대로 저장, 이미지는 WebP로 변환
                if file_ext in ['.mp4', '.webm']:
                    # 동영상 파일은 그대로 저장
                    new_filename = f"sub_banner_{i}{file_ext}"
                    file_path = upload_dir / new_filename
                    with file_path.open("wb") as buffer:
                        shutil.copyfileobj(sub_banner_file.file, buffer)
                else:
                    # 이미지는 WebP로 변환
                    image_data = await sub_banner_file.read()
                    output_path = upload_dir / f"sub_banner_{i}"
                    convert_to_webp(image_data, output_path, quality=90, max_width=1200)
                    new_filename = f"sub_banner_{i}.webp"

                # URL 경로 저장 (캐시 우회를 위한 타임스탬프 추가)
                timestamp = int(datetime.now().timestamp())
                sub_banner_updates[f"sub_banner_image_{i}"] = f"/static/uploads/{new_filename}?v={timestamp}"
            else:
                # 파일 업로드가 없으면 기존 값 유지
                if current_config:
                    existing_value = getattr(current_config, f"sub_banner_image_{i}", None)
                    if existing_value:
                        sub_banner_updates[f"sub_banner_image_{i}"] = existing_value

            # 텍스트 필드 업데이트
            sub_banner_emoji = sub_banner_emojis[i]
            sub_banner_title = sub_banner_titles[i]
            sub_banner_subtitle = sub_banner_subtitles[i]
            sub_banner_description = sub_banner_descriptions[i]
            sub_banner_link = sub_banner_links[i]

            if sub_banner_emoji:
                sub_banner_updates[f"sub_banner_emoji_{i}"] = sub_banner_emoji
            if sub_banner_title:
                sub_banner_updates[f"sub_banner_title_{i}"] = sub_banner_title
            if sub_banner_subtitle:
                sub_banner_updates[f"sub_banner_subtitle_{i}"] = sub_banner_subtitle
            if sub_banner_description:
                sub_banner_updates[f"sub_banner_description_{i}"] = sub_banner_description
            if sub_banner_link:
                sub_banner_updates[f"sub_banner_link_{i}"] = sub_banner_link

        updates = {
            "site_name": site_name,
            "site_url": site_url if site_url else None,
            "site_logo": site_logo_url,
            "site_favicon": site_favicon_url,
            "main_title": main_title,
            "main_subtitle": main_subtitle,
            "footer_text": footer_text,
            **banner_updates,
            **sub_banner_updates,
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


@router.get("/settings/pages", response_class=HTMLResponse)
async def pages_settings(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None)
):
    """페이지 설정"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    site_service = SiteService(db)
    services = site_service.get_all_services()
    site_config = site_service.get_site_config()

    return templates.TemplateResponse(
        "admin/settings_pages.html",
        {
            "request": request,
            "username": username,
            "site_config": site_config,
            "services": services,
            "success": None,
            "error": None
        }
    )

# 하위 호환성을 위한 리다이렉트
@router.get("/settings/services", response_class=HTMLResponse)
async def services_settings_redirect():
    """기존 URL에서 새 URL로 리다이렉트"""
    return RedirectResponse(url="/admin/settings/pages", status_code=301)


@router.post("/settings/pages/create", response_class=HTMLResponse)
async def create_page(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    code: str = Form(...),
    title: str = Form(...),
    subtitle: str = Form(...),
    description: str = Form(...),
    character_name: str = Form(...),
    character_emoji: str = Form(...)
):
    """새 페이지 생성"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    try:
        site_service = SiteService(db)

        # 코드 검증 (영문, 숫자, 언더스코어만 허용)
        import re
        if not re.match(r'^[a-z0-9_]+$', code):
            raise ValueError("코드는 영문 소문자, 숫자, 언더스코어(_)만 사용할 수 있습니다.")

        # 새 페이지 생성
        service_data = {
            "code": code,
            "url_path": f"/pages/{code}",  # 입력 페이지 경로
            "result_url_path": f"/results/{code}",  # 결과 페이지 경로
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "character_name": character_name,
            "character_emoji": character_emoji,
            "is_active": True
        }
        site_service.create_service(service_data)

        # 템플릿 파일 자동 생성 (pages 폴더에)
        template_dir = Path("app/templates/pages")
        template_dir.mkdir(parents=True, exist_ok=True)

        template_file = template_dir / f"{code}.html"
        if not template_file.exists():
            template_content = f'''{{%% extends "layout/base.html" %%}}

{{%% block title %%}}{title} - {{{{ site_config.site_name if site_config else "명월헌" }}}}{{%% endblock %%}}

{{%% block content %%}}
<div class="container mx-auto px-4 py-8">
    <!-- 캐릭터 이미지 영역 -->
    <div class="character-section text-center mb-8">
        {{%% if service and service.character_form_image %%}}
            {{%% if service.character_form_image.endswith(('.mp4', '.webm')) or '.mp4?' in service.character_form_image or '.webm?' in service.character_form_image %%}}
                <video class="character-image mx-auto" autoplay loop muted playsinline style="max-width: 300px; height: auto;">
                    <source src="{{{{ service.character_form_image }}}}" type="video/{{{{ 'mp4' if '.mp4' in service.character_form_image else 'webm' }}}}">
                </video>
            {{%% else %%}}
                <img src="{{{{ service.character_form_image }}}}" alt="{{{{ service.character_name }}}}" class="character-image mx-auto" style="max-width: 300px; height: auto;">
            {{%% endif %%}}
        {{%% elif service and service.character_emoji %%}}
            <div class="character-emoji text-8xl mb-4">{{{{ service.character_emoji }}}}</div>
        {{%% endif %%}}

        <h1 class="text-4xl font-bold mb-4">{{{{ service.title if service else "{title}" }}}}</h1>
        <p class="text-xl text-gray-600 mb-2">{{{{ service.subtitle if service else "{subtitle}" }}}}</p>
        <p class="text-gray-500">{{{{ service.description if service else "{description}" }}}}</p>
    </div>

    <!-- 여기부터 커스텀 영역 -->
    <!-- 아래에 원하는 입력 폼이나 기능을 추가하세요 -->

    <div class="custom-content max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8 mt-8">
        <div class="text-center text-gray-500">
            <p class="text-lg mb-4">🛠️ 이 영역은 커스텀 코드를 작성하는 공간입니다</p>
            <p class="text-sm">템플릿 파일: <code class="bg-gray-100 px-2 py-1 rounded">app/templates/pages/{code}.html</code></p>
            <p class="text-sm mt-2">이 파일을 수정하여 입력 폼이나 기능을 추가하세요.</p>
        </div>
    </div>

    <!-- 커스텀 영역 끝 -->
</div>
{{%% endblock %%}}
'''
            with template_file.open("w", encoding="utf-8") as f:
                f.write(template_content)

        # 2. 결과 페이지 템플릿 생성 (results 폴더에)
        results_dir = Path("app/templates/results")
        results_dir.mkdir(parents=True, exist_ok=True)

        result_template_file = results_dir / f"{code}.html"
        if not result_template_file.exists():
            result_template_content = f'''{{%% extends "layout/base.html" %%}}

{{%% block title %%}}{{{{ service.title }}}} 결과 - {{{{ site_config.site_name if site_config else "명월헌" }}}}{{%% endblock %%}}

{{%% block meta_description %%}}{{{{ request_data.name if request_data and request_data.name else '고객' }}}}님의 {{{{ service.title }}}} 풀이 결과입니다. {{{{ service.character_name }}}}이 자세히 풀어드렸습니다.{{%% endblock %%}}

{{%% block meta_keywords %%}}{{{{ service.title }}}}, 운세, 사주, 운세 결과{{%% endblock %%}}

{{%% block og_title %%}}{{{{ request_data.name if request_data and request_data.name else '고객' }}}}님의 {{{{ service.title }}}} 결과{{%% endblock %%}}

{{%% block og_description %%}}{{{{ service.character_name }}}}이 자세히 풀어드린 {{{{ service.title }}}} 결과를 확인하세요.{{%% endblock %%}}

{{%% block og_image %%}}{{{{ service.character_image if service.character_image else url_for('static', path='/images/og-default.jpg') }}}}{{%% endblock %%}}

{{%% block extra_css %%}}
<style>
    .result-header {{
        text-align: center;
        padding: 100px 20px 40px;
        margin-top: 60px;
    }}

    .character-emoji {{
        font-size: 60px;
        margin-bottom: 15px;
    }}

    .character-image {{
        width: 100%;
        max-width: 500px;
        height: auto;
        aspect-ratio: 3 / 4;
        object-fit: cover;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        margin: 0 auto 20px;
        display: block;
    }}

    @media (max-width: 768px) {{
        .character-image {{
            max-width: 90vw;
        }}
    }}

    .result-title {{
        font-size: 32px;
        margin-bottom: 10px;
    }}

    .result-date {{
        color: #5a4a3a;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        margin-top: 5px;
    }}

    .cache-notice {{
        display: inline-block;
        padding: 8px 16px;
        background: rgba(76, 175, 80, 0.2);
        border: 1px solid #4CAF50;
        border-radius: 20px;
        color: #4CAF50;
        font-size: 14px;
        margin-top: 10px;
    }}

    .result-container {{
        max-width: 1100px;
        margin: 40px auto;
        padding: 0 20px;
    }}

    .section-box {{
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}

    .section-title {{
        font-size: 24px;
        font-weight: 700;
        color: #5a4a3a;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0e6d6;
    }}

    .content-text {{
        line-height: 1.8;
        color: #4a4a4a;
        white-space: pre-wrap;
    }}

    .back-button {{
        display: inline-block;
        padding: 12px 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 20px auto;
        display: block;
        width: fit-content;
    }}

    .back-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }}
</style>
{{%% endblock %%}}

{{%% block content %%}}
<!-- 결과 헤더 -->
<div class="result-header">
    {{%% if service.character_image %%}}
        {{%% if service.character_image.endswith(('.mp4', '.webm')) or '.mp4?' in service.character_image or '.webm?' in service.character_image %%}}
            <video class="character-image" autoplay loop muted playsinline>
                <source src="{{{{ service.character_image }}}}" type="video/{{{{ 'mp4' if '.mp4' in service.character_image else 'webm' }}}}">
            </video>
        {{%% else %%}}
            <img src="{{{{ service.character_image }}}}" alt="{{{{ service.character_name }}}}" class="character-image">
        {{%% endif %%}}
    {{%% elif service.character_emoji %%}}
        <div class="character-emoji">{{{{ service.character_emoji }}}}</div>
    {{%% endif %%}}

    <h1 class="result-title">{{{{ service.character_name }}}}의 {{{{ service.title }}}}</h1>

    {{%% if request_data and request_data.name %%}}
        <p class="result-date">{{{{ request_data.name }}}}님의 운세</p>
    {{%% endif %%}}

    {{%% if today %%}}
        <p class="result-date">{{{{ today }}}}</p>
    {{%% endif %%}}

    {{%% if is_cached %%}}
        <span class="cache-notice">💾 저장된 결과</span>
    {{%% endif %%}}
</div>

<!-- 결과 내용 -->
<div class="result-container">
    <!-- 여기부터 커스텀 결과 영역 -->
    <div class="section-box">
        <h2 class="section-title">🔮 결과</h2>
        <div class="content-text">
            {{%% if result and result.content %%}}
                {{{{ result.content | safe }}}}
            {{%% else %%}}
                <p style="text-align: center; color: #999; padding: 40px;">
                    🛠️ 이 영역은 커스텀 결과를 표시하는 공간입니다<br>
                    템플릿 파일: <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px;">app/templates/results/{code}_result.html</code><br>
                    <small style="margin-top: 10px; display: block;">이 파일을 수정하여 결과를 커스터마이징하세요.</small>
                </p>
            {{%% endif %%}}
        </div>
    </div>

    <!-- 다시 보기 버튼 -->
    <a href="{{{{ service.url_path }}}}" class="back-button">다시 보기</a>
</div>
{{%% endblock %%}}
'''
            with result_template_file.open("w", encoding="utf-8") as f:
                f.write(result_template_content)

        return RedirectResponse(
            url=f"/admin/settings/pages?success=new_page_created",
            status_code=303
        )
    except Exception as e:
        site_service = SiteService(db)
        services = site_service.get_all_services()
        site_config = site_service.get_site_config()

        return templates.TemplateResponse(
            "admin/settings_pages.html",
            {
                "request": request,
                "username": username,
                "site_config": site_config,
                "services": services,
                "success": None,
                "error": f"페이지 생성 중 오류가 발생했습니다: {str(e)}"
            }
        )


@router.post("/settings/pages/{service_code}/delete", response_class=HTMLResponse)
async def delete_page(
    request: Request,
    service_code: str,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None)
):
    """페이지 삭제"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    try:
        site_service = SiteService(db)
        site_service.delete_service(service_code)

        # 관련 이미지 파일도 삭제
        upload_dir = Path("app/static/uploads")
        for pattern in [f"character_{service_code}.*", f"character_form_{service_code}.*"]:
            for old_file in upload_dir.glob(pattern):
                old_file.unlink()

        return RedirectResponse(
            url=f"/admin/settings/pages?success=page_deleted",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/admin/settings/pages?error={str(e)}",
            status_code=303
        )


@router.post("/settings/pages/{service_code}", response_class=HTMLResponse)
async def update_service_settings(
    request: Request,
    service_code: str,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    url_path: Optional[str] = Form(None),
    title: str = Form(...),
    subtitle: str = Form(...),
    description: str = Form(...),
    character_name: str = Form(...),
    character_emoji: str = Form(...),
    character_image_file: Optional[UploadFile] = File(None),
    character_form_image_file: Optional[UploadFile] = File(None),
    is_active: Optional[str] = Form(None)
):
    """서비스 설정 업데이트"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    try:
        site_service = SiteService(db)

        # 캐릭터 이미지/영상 업로드 처리
        character_image_url = None
        if character_image_file and character_image_file.filename:
            # 업로드 디렉토리 설정
            upload_dir = Path("app/static/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)

            # 파일 확장자 확인
            file_ext = os.path.splitext(character_image_file.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm']:
                raise ValueError("지원하지 않는 파일 형식입니다. (이미지: jpg, png, gif, webp / 동영상: mp4, webm)")

            # 이미지 데이터 읽기
            image_data = await character_image_file.read()

            # 동영상은 그대로 저장, 이미지는 WebP로 변환
            if file_ext in ['.mp4', '.webm']:
                # 동영상 파일 비율 검증 및 저장
                temp_filename = f"temp_character_{service_code}{file_ext}"
                temp_path = upload_dir / temp_filename
                with temp_path.open("wb") as buffer:
                    buffer.write(image_data)

                # 모든 확장자의 기존 파일 삭제
                for old_file in upload_dir.glob(f"character_{service_code}.*"):
                    old_file.unlink()

                # 최종 경로로 이동
                final_filename = f"character_{service_code}{file_ext}"
                final_path = upload_dir / final_filename
                temp_path.rename(final_path)
            else:
                # 이미지 비율 검증 (3:4 비율 권장, ±10% 허용)
                target_ratio = 3 / 4
                if not validate_image_ratio(image_data, target_ratio, tolerance=0.10):
                    from app.utils.image_utils import get_image_dimensions
                    width, height = get_image_dimensions(image_data)
                    aspect_ratio = width / height
                    raise ValueError(f"이미지 비율이 3:4에 가깝지 않습니다. 현재 비율: {width}:{height} ({aspect_ratio:.2f})")

                # 모든 확장자의 기존 파일 삭제
                for old_file in upload_dir.glob(f"character_{service_code}.*"):
                    old_file.unlink()

                # WebP로 변환 및 저장
                output_path = upload_dir / f"character_{service_code}"
                convert_to_webp(image_data, output_path, quality=85, max_width=400)
                final_filename = f"character_{service_code}.webp"

            # URL 경로 저장 (캐시 우회를 위한 타임스탬프 추가)
            timestamp = int(datetime.now().timestamp())
            character_image_url = f"/static/uploads/{final_filename}?v={timestamp}"
        else:
            # 파일 업로드가 없으면 기존 값 유지
            current_service = site_service.get_service_by_code(service_code)
            if current_service and current_service.character_image:
                character_image_url = current_service.character_image

        # 시작 페이지 캐릭터 이미지/영상 업로드 처리
        character_form_image_url = None
        if character_form_image_file and character_form_image_file.filename:
            # 업로드 디렉토리 설정
            upload_dir = Path("app/static/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)

            # 파일 확장자 확인
            file_ext = os.path.splitext(character_form_image_file.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm']:
                raise ValueError("지원하지 않는 파일 형식입니다. (이미지: jpg, png, gif, webp / 동영상: mp4, webm)")

            # 이미지 데이터 읽기
            image_data = await character_form_image_file.read()

            # 동영상은 그대로 저장, 이미지는 WebP로 변환
            if file_ext in ['.mp4', '.webm']:
                # 동영상 파일 비율 검증 및 저장
                temp_filename = f"temp_character_form_{service_code}{file_ext}"
                temp_path = upload_dir / temp_filename
                with temp_path.open("wb") as buffer:
                    buffer.write(image_data)

                # 모든 확장자의 기존 파일 삭제
                for old_file in upload_dir.glob(f"character_form_{service_code}.*"):
                    old_file.unlink()

                # 최종 경로로 이동
                final_filename = f"character_form_{service_code}{file_ext}"
                final_path = upload_dir / final_filename
                temp_path.rename(final_path)
            else:
                # 이미지 비율 검증 (3:4 비율 권장, ±10% 허용)
                target_ratio = 3 / 4
                if not validate_image_ratio(image_data, target_ratio, tolerance=0.10):
                    from app.utils.image_utils import get_image_dimensions
                    width, height = get_image_dimensions(image_data)
                    aspect_ratio = width / height
                    raise ValueError(f"이미지 비율이 3:4에 가깝지 않습니다. 현재 비율: {width}:{height} ({aspect_ratio:.2f})")

                # 모든 확장자의 기존 파일 삭제
                for old_file in upload_dir.glob(f"character_form_{service_code}.*"):
                    old_file.unlink()

                # WebP로 변환 및 저장
                output_path = upload_dir / f"character_form_{service_code}"
                convert_to_webp(image_data, output_path, quality=85, max_width=400)
                final_filename = f"character_form_{service_code}.webp"

            # URL 경로 저장 (캐시 우회를 위한 타임스탬프 추가)
            timestamp = int(datetime.now().timestamp())
            character_form_image_url = f"/static/uploads/{final_filename}?v={timestamp}"
        else:
            # 파일 업로드가 없으면 기존 값 유지
            current_service = site_service.get_service_by_code(service_code)
            if current_service and current_service.character_form_image:
                character_form_image_url = current_service.character_form_image

        # URL 경로 검증
        if url_path:
            url_path = url_path.strip()
            if not url_path.startswith('/'):
                url_path = '/' + url_path

        updates = {
            "url_path": url_path if url_path else f"/fortune/{service_code}",
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "character_name": character_name,
            "character_emoji": character_emoji,
            "character_image": character_image_url,
            "character_form_image": character_form_image_url,
            "is_active": is_active == "on"
        }
        site_service.update_service_config(service_code, updates)

        services = site_service.get_all_services()
        site_config = site_service.get_site_config()

        return templates.TemplateResponse(
            "admin/settings_pages.html",
            {
                "request": request,
                "username": username,
                "site_config": site_config,
                "services": services,
                "success": f"{title} 설정이 성공적으로 저장되었습니다.",
                "error": None
            }
        )
    except Exception as e:
        site_service = SiteService(db)
        services = site_service.get_all_services()
        site_config = site_service.get_site_config()

        return templates.TemplateResponse(
            "admin/settings_pages.html",
            {
                "request": request,
                "username": username,
                "site_config": site_config,
                "services": services,
                "success": None,
                "error": f"저장 중 오류가 발생했습니다: {str(e)}"
            }
        )


@router.get("/settings/seo", response_class=HTMLResponse)
async def settings_seo(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None)
):
    """SEO 설정 페이지"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    site_service = SiteService(db)
    config = site_service.get_site_config()

    return templates.TemplateResponse(
        "admin/settings_seo.html",
        {
            "request": request,
            "username": username,
            "config": config,
            "success": None,
            "error": None
        }
    )


@router.post("/settings/seo", response_class=HTMLResponse)
async def update_seo_settings(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    seo_title: Optional[str] = Form(None),
    seo_description: Optional[str] = Form(None),
    seo_keywords: Optional[str] = Form(None),
    seo_author: Optional[str] = Form(None),
    seo_og_image_file: Optional[UploadFile] = File(None),
    header_script: Optional[str] = Form(None),
    footer_script: Optional[str] = Form(None)
):
    """SEO 설정 업데이트"""
    username = check_admin(admin_token)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=303)

    try:
        site_service = SiteService(db)
        current_config = site_service.get_site_config()

        # OG 이미지 업로드 처리
        seo_og_image_url = None
        if seo_og_image_file and seo_og_image_file.filename:
            # 업로드 디렉토리 설정
            upload_dir = Path("app/static/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)

            # 파일 확장자 확인
            file_ext = os.path.splitext(seo_og_image_file.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise ValueError("OG 이미지: 지원하지 않는 파일 형식입니다. (jpg, png, gif, webp만 가능)")

            # 이미지 데이터 읽기
            image_data = await seo_og_image_file.read()

            # 이미지 비율 검증 (2:1 비율 권장, ±15% 허용)
            target_ratio = 1200 / 630  # 약 1.9:1
            if not validate_image_ratio(image_data, target_ratio, tolerance=0.15):
                from app.utils.image_utils import get_image_dimensions
                width, height = get_image_dimensions(image_data)
                aspect_ratio = width / height
                raise ValueError(f"OG 이미지 비율이 권장 비율(1200x630, 약 2:1)에 가깝지 않습니다. 현재 크기: {width}x{height} (비율: {aspect_ratio:.2f})")

            # 기존 OG 이미지 파일들 삭제 (모든 확장자)
            for old_file in upload_dir.glob("og_image.*"):
                old_file.unlink()

            # WebP로 변환 및 저장 (1200px 최대 너비)
            output_path = upload_dir / "og_image"
            convert_to_webp(image_data, output_path, quality=90, max_width=1200)

            # URL 경로 저장
            timestamp = int(datetime.now().timestamp())
            seo_og_image_url = f"/static/uploads/og_image.webp?v={timestamp}"
        else:
            # 파일 업로드가 없으면 기존 값 유지
            if current_config and current_config.seo_og_image:
                seo_og_image_url = current_config.seo_og_image

        updates = {
            "seo_title": seo_title if seo_title else None,
            "seo_description": seo_description if seo_description else None,
            "seo_keywords": seo_keywords if seo_keywords else None,
            "seo_author": seo_author if seo_author else "명월헌",
            "seo_og_image": seo_og_image_url,
            "header_script": header_script if header_script else None,
            "footer_script": footer_script if footer_script else None
        }

        site_service.update_site_config(updates)
        config = site_service.get_site_config()

        return templates.TemplateResponse(
            "admin/settings_seo.html",
            {
                "request": request,
                "username": username,
                "config": config,
                "success": "SEO 설정이 성공적으로 저장되었습니다.",
                "error": None
            }
        )
    except Exception as e:
        site_service = SiteService(db)
        config = site_service.get_site_config()

        return templates.TemplateResponse(
            "admin/settings_seo.html",
            {
                "request": request,
                "username": username,
                "config": config,
                "success": None,
                "error": f"저장 중 오류가 발생했습니다: {str(e)}"
            }
        )
