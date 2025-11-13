"""
운세 생성 서비스
"""
from datetime import date, datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.models.fortune_result import FortuneResult
from app.models.service_config import FortuneServiceConfig
from app.utils.hashing import build_user_key, get_zodiac
from app.services.gemini_service import gemini_service
from app.config import get_settings

settings = get_settings()


class FortuneService:
    """운세 생성 및 캐싱 서비스"""

    def __init__(self, db: Session):
        self.db = db

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
        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"
        year = int(str(birthdate)[:4])
        zodiac = get_zodiac(year)
        today_str = date.today().strftime("%Y년 %m월 %d일")

        return f"""당신은 귀여운 {config.character_name} 캐릭터입니다. 친근하고 밝은 말투로 오늘의 운세를 알려주세요.

[의뢰인 정보]
- 이름: {name}
- 생년월일: {birthdate}
- 성별: {gender}
- 띠: {zodiac}
- 오늘 날짜: {today_str}

다음 형식으로 작성해주세요:

**인사말**
{name}님, 안녕하세요! {config.character_name}예요~ 오늘 하루 운세를 봐드릴게요! {config.character_emoji}

**오늘의 기운**
오늘의 전반적인 에너지와 분위기를 설명해주세요. (3-4문장)

**오늘 조심할 것**
오늘 주의해야 할 점을 2-3가지 알려주세요.

**행운의 색**
오늘의 행운의 색 하나 (예: 노란색)

**행운의 숫자**
오늘의 행운의 숫자 하나 (1-99)

**행운의 방향**
오늘의 행운의 방향 하나 (동/서/남/북)

**{config.character_name}의 한마디**
오늘 하루를 응원하는 짧은 메시지 (1-2문장)

[작성 가이드]
- 친근하고 귀여운 말투 ("~예요", "~해요")
- 구체적이고 실용적인 조언
- 긍정적이고 응원하는 톤
- 총 300-400자 내외

위 형식을 정확히 지켜서 작성해주세요!"""

    def build_saju_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """사주팔자 프롬프트"""
        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"
        calendar = "양력" if data.get("calendar", "solar") == "solar" else "음력"
        birth_time = data.get("birth_time", "모름")

        return f"""당신은 30년 경력의 전문 명리학자 {config.character_name}입니다. 전통 사주명리학을 바탕으로 친절하고 정확하게 운세를 풀어주세요.

[기본 정보]
- 이름: {name}
- 생년월일: {birthdate} ({calendar})
- 성별: {gender}
- 태어난 시간: {birth_time}

다음 형식으로 작성해주세요:

**인사말**
{name}님, 안녕하세요. {config.character_name}입니다. 당신의 사주를 깊이 살펴보았습니다.

**1. 전체적인 성격과 특징**
- 타고난 성품과 기질 (4-5문장)
- 장점과 강점
- 주의해야 할 성격적 특징

**2. 2025년 운세**
- 전반적인 흐름
- 좋은 시기와 조심할 시기
- 기회와 도전

**3. 직업운과 재물운**
- 적합한 직업 분야
- 재물을 모으는 방법
- 사업이나 투자 관련 조언

**4. 연애운과 결혼운**
- 이성관계의 특징
- 좋은 인연을 만나는 시기
- 배우자와의 궁합 (일반적인 조언)

**5. 건강운**
- 주의해야 할 건강 부위
- 건강 관리 방법

**6. 한 줄 조언**
- 인생을 살아가는 데 도움이 될 한 마디

[작성 가이드]
- 각 섹션은 **1. 제목** 형식으로 명확히 구분
- 전문적이지만 이해하기 쉬운 표현
- 긍정적이면서도 현실적인 조언
- 존댓말 사용
- 총 1000-1200자 내외

위 형식을 정확히 지켜서 작성해주세요!"""

    def build_match_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """사주궁합 프롬프트"""
        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"

        partner_name = data.get("partner_name", "상대방")
        partner_birthdate = data["partner_birthdate"]
        partner_gender = "남성" if data["partner_gender"] == "male" else "여성"

        return f"""당신은 연애와 인연을 전문으로 보는 {config.character_name}입니다. 두 사람의 궁합을 따뜻하고 섬세하게 풀어주세요.

[첫 번째 분 정보]
- 이름: {name}
- 생년월일: {birthdate}
- 성별: {gender}

[두 번째 분 정보]
- 이름: {partner_name}
- 생년월일: {partner_birthdate}
- 성별: {partner_gender}

다음 형식으로 작성해주세요:

**인사말**
{name}님과 {partner_name}님, 안녕하세요. {config.character_name}입니다. 두 분의 인연을 살펴보았습니다.

**1. 전체적인 궁합도**
- 두 사람의 전반적인 궁합 (70점 만점 형식으로)
- 잘 맞는 부분
- 조심해야 할 부분

**2. 연애운**
- 연애할 때의 케미
- 서로에게 끌리는 이유
- 연애 중 주의사항

**3. 결혼운**
- 결혼 생활의 전망
- 가정을 꾸릴 때의 조화
- 부부로서의 장단점

**4. 소통과 이해**
- 대화 스타일의 차이
- 서로를 이해하는 방법
- 갈등 해결 조언

**5. 조언**
- 두 사람이 행복하기 위한 한 마디

[작성 가이드]
- 따뜻하고 긍정적인 톤
- 현실적이면서도 희망적인 조언
- 존댓말 사용
- 총 800-1000자 내외

위 형식을 정확히 지켜서 작성해주세요!"""

    def build_dream_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """꿈해몽 프롬프트"""
        name = data.get("name", "고객")
        dream_content = data["dream_content"]

        return f"""당신은 꿈 해석의 대가 {config.character_name}입니다. 전통 꿈해몽과 현대 심리학을 결합하여 꿈의 의미를 풀어주세요.

[의뢰인 정보]
- 이름: {name}

[꿈 내용]
{dream_content}

다음 형식으로 작성해주세요:

**인사말**
{name}님, 안녕하세요. {config.character_name}입니다. 흥미로운 꿈을 꾸셨군요.

**1. 꿈의 전체적인 의미**
- 이 꿈이 나타내는 전반적인 메시지 (3-4문장)

**2. 주요 상징 해석**
- 꿈에 나온 주요 상징물/인물/상황의 의미
- 각각이 뜻하는 바

**3. 재물운**
- 이 꿈과 관련된 재물운
- 재물과 관련된 조언

**4. 건강운**
- 이 꿈이 알려주는 건강 관련 메시지
- 주의할 점

**5. 심리 상태**
- 현재 당신의 내면 상태
- 무의식의 메시지

**6. 조언**
- 이 꿈을 바탕으로 한 실천적 조언

[작성 가이드]
- 전문적이지만 이해하기 쉽게
- 긍정적이면서도 실용적인 조언
- 존댓말 사용
- 총 700-900자 내외

위 형식을 정확히 지켜서 작성해주세요!"""

    def format_custom_prompt(self, template: str, data: dict) -> str:
        """커스텀 프롬프트 템플릿 포매팅"""
        return template.format(**data)
