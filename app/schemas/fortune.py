"""
운세 관련 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class FortuneRequest(BaseModel):
    """운세 요청 기본 스키마"""
    name: Optional[str] = Field(None, max_length=50, description="이름 (선택)")
    birthdate: date = Field(..., description="생년월일")
    gender: str = Field(..., pattern="^(male|female)$", description="성별")


class TodayFortuneRequest(FortuneRequest):
    """오늘의 운세 요청"""
    pass


class SajuFortuneRequest(FortuneRequest):
    """사주팔자 요청"""
    birth_time: Optional[str] = Field(None, description="태어난 시간 (HH:MM)")
    calendar: str = Field("solar", pattern="^(solar|lunar)$", description="양력/음력")


class MatchFortuneRequest(FortuneRequest):
    """사주궁합 요청"""
    partner_name: Optional[str] = Field(None, max_length=50, description="상대방 이름")
    partner_birthdate: date = Field(..., description="상대방 생년월일")
    partner_gender: str = Field(..., pattern="^(male|female)$", description="상대방 성별")


class DreamFortuneRequest(FortuneRequest):
    """꿈해몽 요청"""
    dream_content: str = Field(..., min_length=10, max_length=1000, description="꿈 내용")


class FortuneResponse(BaseModel):
    """운세 응답"""
    success: bool = True
    service_code: str
    is_cached: bool
    result_text: str
    date: date

    class Config:
        from_attributes = True
