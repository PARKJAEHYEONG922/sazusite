"""
운세 생성 서비스
"""
from datetime import date, datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from app.models.fortune_result import FortuneResult
from app.models.service_config import FortuneServiceConfig
from app.utils.hashing import build_user_key, get_zodiac
from app.services.gemini_service import gemini_service
from app.config import get_settings

settings = get_settings()

# 프롬프트 디렉토리 경로
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class FortuneService:
    """운세 생성 및 캐싱 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self._prompt_cache = {}

    def _load_prompt_template(self, service_code: str) -> str:
        """프롬프트 템플릿 파일 로드"""
        if service_code in self._prompt_cache:
            return self._prompt_cache[service_code]

        prompt_file = PROMPTS_DIR / f"{service_code}.txt"

        if not prompt_file.exists():
            raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {prompt_file}")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            template = f.read()

        self._prompt_cache[service_code] = template
        return template

    def find_cached_result(
        self,
        service_code: str,
        user_key: str,
        target_date: date
    ) -> Optional[FortuneResult]:
        """
        캐시된 운세 결과 조회

        Args:
            service_code: 서비스 코드 (today, saju, match, dream)
            user_key: 사용자 식별 키
            target_date: 조회 날짜

        Returns:
            캐시된 결과 or None
        """
        if not settings.cache_enabled:
            return None

        return self.db.query(FortuneResult).filter(
            FortuneResult.service_code == service_code,
            FortuneResult.user_key == user_key,
            FortuneResult.date == target_date
        ).first()

    def create_fortune_result(
        self,
        service_code: str,
        user_key: str,
        request_data: dict
    ) -> FortuneResult:
        """
        새로운 운세 생성

        Args:
            service_code: 서비스 코드
            user_key: 사용자 식별 키
            request_data: 요청 데이터

        Returns:
            생성된 운세 결과
        """
        # 2026 신년운세는 별도 처리
        if service_code == "newyear2026":
            prompt = self.build_newyear2026_prompt(request_data)
            result_text = gemini_service.generate_content(prompt)

            serializable_data = self._make_json_serializable(request_data)

            fortune_result = FortuneResult(
                service_code=service_code,
                user_key=user_key,
                date=date.today(),
                request_payload=serializable_data,
                result_text=result_text,
                is_from_cache=False
            )

            self.db.add(fortune_result)
            self.db.commit()
            self.db.refresh(fortune_result)

            return fortune_result

        # 서비스 설정 조회
        service_config = self.db.query(FortuneServiceConfig).filter(
            FortuneServiceConfig.code == service_code
        ).first()

        if not service_config or not service_config.is_active:
            raise ValueError(f"서비스를 찾을 수 없거나 비활성화되었습니다: {service_code}")

        # 프롬프트 생성
        prompt = self.build_prompt(service_code, service_config, request_data)

        # Gemini API 호출
        result_text = gemini_service.generate_content(prompt)

        # request_data를 JSON 직렬화 가능하게 변환 (date 객체를 문자열로)
        serializable_data = self._make_json_serializable(request_data)

        # DB 저장
        fortune_result = FortuneResult(
            service_code=service_code,
            user_key=user_key,
            date=date.today(),
            request_payload=serializable_data,
            result_text=result_text,
            is_from_cache=False
        )

        self.db.add(fortune_result)
        self.db.commit()
        self.db.refresh(fortune_result)

        return fortune_result

    def _make_json_serializable(self, data: dict) -> dict:
        """
        딕셔너리의 date/datetime 객체를 문자열로 변환

        Args:
            data: 원본 딕셔너리

        Returns:
            JSON 직렬화 가능한 딕셔너리
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, (date, datetime)):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = self._make_json_serializable(value)
            else:
                result[key] = value
        return result

    def get_or_create_fortune(
        self,
        service_code: str,
        request_data: dict
    ) -> Dict:
        """
        운세 조회 또는 생성 (메인 로직)

        Args:
            service_code: 서비스 코드
            request_data: 요청 데이터

        Returns:
            운세 결과 딕셔너리
        """
        # user_key 생성
        user_key = self.generate_user_key(service_code, request_data)

        # 오늘 날짜
        today = date.today()

        # 캐시 조회
        cached = self.find_cached_result(service_code, user_key, today)

        if cached:
            return {
                "service_code": service_code,
                "is_cached": True,
                "result_text": cached.result_text,
                "date": cached.date
            }

        # 새로 생성
        new_result = self.create_fortune_result(service_code, user_key, request_data)

        return {
            "service_code": service_code,
            "is_cached": False,
            "result_text": new_result.result_text,
            "date": new_result.date
        }

    def generate_user_key(self, service_code: str, request_data: dict) -> str:
        """
        user_key 생성

        Args:
            service_code: 서비스 코드
            request_data: 요청 데이터

        Returns:
            SHA256 해시 문자열
        """
        name = request_data.get("name")
        birthdate = datetime.fromisoformat(str(request_data["birthdate"])).date()
        gender = request_data["gender"]

        # 궁합일 경우 상대방 생년월일도 포함
        partner_birthdate = None
        if service_code == "match" and "partner_birthdate" in request_data:
            partner_birthdate = datetime.fromisoformat(str(request_data["partner_birthdate"])).date()

        return build_user_key(name, birthdate, gender, partner_birthdate)

    def build_prompt(
        self,
        service_code: str,
        service_config: FortuneServiceConfig,
        request_data: dict
    ) -> str:
        """
        서비스별 프롬프트 생성

        Args:
            service_code: 서비스 코드
            service_config: 서비스 설정
            request_data: 요청 데이터

        Returns:
            프롬프트 문자열
        """
        # 커스텀 프롬프트 템플릿이 있으면 사용
        if service_config.prompt_template:
            return self.format_custom_prompt(service_config.prompt_template, request_data)

        # 기본 프롬프트
        if service_code == "today":
            return self.build_today_prompt(request_data, service_config)
        elif service_code == "saju":
            return self.build_saju_prompt(request_data, service_config)
        elif service_code == "match":
            return self.build_match_prompt(request_data, service_config)
        elif service_code == "dream":
            return self.build_dream_prompt(request_data, service_config)
        else:
            raise ValueError(f"알 수 없는 서비스 코드: {service_code}")

    def build_today_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """오늘의 운세 프롬프트"""
        template = self._load_prompt_template("today")

        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"
        birth_time = data.get("birth_time", "모름")
        year = int(str(birthdate)[:4])
        zodiac = get_zodiac(year)
        today_str = date.today().strftime("%Y년 %m월 %d일")

        return template.format(
            character_name=config.character_name,
            character_emoji=config.character_emoji,
            name=name,
            birthdate=birthdate,
            gender=gender,
            birth_time=birth_time,
            zodiac=zodiac,
            today=today_str
        )

    def build_saju_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """사주팔자 프롬프트"""
        template = self._load_prompt_template("saju")

        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"
        calendar = "양력" if data.get("calendar", "solar") == "solar" else "음력"
        birth_time = data.get("birth_time", "모름")

        return template.format(
            character_name=config.character_name,
            name=name,
            birthdate=birthdate,
            gender=gender,
            calendar=calendar,
            birth_time=birth_time
        )

    def build_match_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """사주궁합 프롬프트"""
        template = self._load_prompt_template("match")

        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"

        partner_name = data.get("partner_name", "상대방")
        partner_birthdate = data["partner_birthdate"]
        partner_gender = "남성" if data["partner_gender"] == "male" else "여성"

        return template.format(
            character_name=config.character_name,
            name=name,
            birthdate=birthdate,
            gender=gender,
            partner_name=partner_name,
            partner_birthdate=partner_birthdate,
            partner_gender=partner_gender
        )

    def build_dream_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """꿈해몽 프롬프트"""
        template = self._load_prompt_template("dream")

        name = data.get("name", "고객")
        dream_content = data["dream_content"]

        return template.format(
            character_name=config.character_name,
            name=name,
            dream_content=dream_content
        )

    def build_newyear2026_prompt(self, data: dict) -> str:
        """2026 신년운세 프롬프트"""
        template = self._load_prompt_template("newyear2026")

        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"
        year = int(str(birthdate)[:4])
        zodiac = get_zodiac(year)

        return template.format(
            name=name,
            birthdate=birthdate,
            gender=gender,
            zodiac=zodiac
        )

    def format_custom_prompt(self, template: str, data: dict) -> str:
        """커스텀 프롬프트 템플릿 포매팅"""
        return template.format(**data)
