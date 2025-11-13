"""
관리자 관련 스키마
"""
from pydantic import BaseModel, Field


class AdminLogin(BaseModel):
    """관리자 로그인"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class AdminToken(BaseModel):
    """관리자 토큰"""
    access_token: str
    token_type: str = "bearer"
