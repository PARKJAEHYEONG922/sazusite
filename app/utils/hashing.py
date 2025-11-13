"""
user_key 생성 유틸리티
"""
import hashlib
from datetime import date
from typing import Optional


def build_user_key(
    name: Optional[str],
    birthdate: date,
    gender: str,
    partner_birthdate: Optional[date] = None
) -> str:
    """
    동일인 식별용 user_key 생성

    Args:
        name: 이름 (선택)
        birthdate: 생년월일
        gender: 성별
        partner_birthdate: 상대방 생년월일 (궁합용)

    Returns:
        SHA256 해시 문자열
    """
    # 입력 데이터를 문자열로 결합
    data_parts = [
        name or "",
        birthdate.isoformat(),
        gender
    ]

    if partner_birthdate:
        data_parts.append(partner_birthdate.isoformat())

    combined = "|".join(data_parts)

    # SHA256 해시 생성
    hash_object = hashlib.sha256(combined.encode('utf-8'))
    user_key = hash_object.hexdigest()

    return user_key


def get_zodiac(year: int) -> str:
    """
    연도로 띠 계산

    Args:
        year: 연도

    Returns:
        띠 이름
    """
    zodiacs = ["원숭이", "닭", "개", "돼지", "쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양"]
    return zodiacs[year % 12]
