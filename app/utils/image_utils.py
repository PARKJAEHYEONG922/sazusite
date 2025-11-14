"""
이미지 처리 유틸리티
WebP 변환, 리사이징, 최적화
"""
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import io


def convert_to_webp(
    image_data: bytes,
    output_path: Path,
    quality: int = 85,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None
) -> str:
    """
    이미지를 WebP 포맷으로 변환

    Args:
        image_data: 원본 이미지 바이트
        output_path: 저장 경로 (확장자 제외)
        quality: WebP 품질 (0-100, 기본 85)
        max_width: 최대 너비 (None이면 원본 유지)
        max_height: 최대 높이 (None이면 원본 유지)

    Returns:
        str: 저장된 파일의 상대 경로
    """
    # 이미지 열기
    img = Image.open(io.BytesIO(image_data))

    # 이미지 모드 변환 (WebP는 RGB와 RGBA 모두 지원)
    if img.mode == 'P':
        # 팔레트 모드는 RGBA로 변환 (투명도 보존)
        img = img.convert('RGBA')
    elif img.mode == 'LA':
        # 그레이스케일+알파는 RGBA로 변환
        img = img.convert('RGBA')
    elif img.mode not in ('RGB', 'RGBA'):
        # 그 외 모드는 RGB로 변환
        img = img.convert('RGB')

    # 리사이징 (비율 유지)
    if max_width or max_height:
        img = resize_image(img, max_width, max_height)

    # WebP로 저장 (투명도 보존)
    output_file = output_path.parent / f"{output_path.stem}.webp"

    # RGBA 모드인 경우 투명도를 보존하기 위한 옵션 추가
    save_kwargs = {
        'format': 'WEBP',
        'quality': quality,
        'method': 6
    }

    # 투명도가 있는 이미지는 lossless 모드 사용 (투명도 완벽 보존)
    if img.mode == 'RGBA':
        save_kwargs['lossless'] = True

    img.save(output_file, **save_kwargs)

    return str(output_file)


def resize_image(
    img: Image.Image,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None
) -> Image.Image:
    """
    이미지 리사이징 (비율 유지)

    Args:
        img: PIL Image 객체
        max_width: 최대 너비
        max_height: 최대 높이

    Returns:
        Image.Image: 리사이징된 이미지
    """
    original_width, original_height = img.size

    # 리사이징 비율 계산
    ratio = 1.0
    if max_width and original_width > max_width:
        ratio = min(ratio, max_width / original_width)
    if max_height and original_height > max_height:
        ratio = min(ratio, max_height / original_height)

    # 리사이징 필요한 경우만 처리
    if ratio < 1.0:
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return img


def get_image_dimensions(image_data: bytes) -> Tuple[int, int]:
    """
    이미지 크기 반환

    Args:
        image_data: 이미지 바이트

    Returns:
        Tuple[int, int]: (width, height)
    """
    img = Image.open(io.BytesIO(image_data))
    return img.size


def validate_image_ratio(
    image_data: bytes,
    target_ratio: float,
    tolerance: float = 0.15
) -> bool:
    """
    이미지 비율 검증

    Args:
        image_data: 이미지 바이트
        target_ratio: 목표 비율 (예: 16/9)
        tolerance: 허용 오차 (기본 15%)

    Returns:
        bool: 비율이 적합한지 여부
    """
    width, height = get_image_dimensions(image_data)
    actual_ratio = width / height

    min_ratio = target_ratio * (1 - tolerance)
    max_ratio = target_ratio * (1 + tolerance)

    return min_ratio <= actual_ratio <= max_ratio
