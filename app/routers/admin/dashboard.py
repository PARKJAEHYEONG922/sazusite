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

            # SVG는 그대로 저장, 나머지는 WebP 변환
            if file_ext == '.svg':
                new_filename = "site_logo.svg"
                file_path = upload_dir / new_filename
                with file_path.open("wb") as f:
                    f.write(image_data)
            else:
                # 기존 로고 파일들 삭제 (모든 확장자)
                for old_file in upload_dir.glob("site_logo.*"):
                    old_file.unlink()

                # WebP로 변환 및 저장
                output_path = upload_dir / "site_logo"
                convert_to_webp(image_data, output_path, quality=90, max_width=800)
                new_filename = "site_logo.webp"

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

        updates = {
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
