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
from app.services.saju_calculator import SajuCalculator
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
    ) -> tuple[FortuneResult, Optional[Dict]]:
        """
        새로운 운세 생성

        Args:
            service_code: 서비스 코드
            user_key: 사용자 식별 키
            request_data: 요청 데이터

        Returns:
            (생성된 운세 결과, 사주 데이터 또는 None)
        """
        saju_data = None

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

            return fortune_result, saju_data

        # 서비스 설정 조회
        service_config = self.db.query(FortuneServiceConfig).filter(
            FortuneServiceConfig.code == service_code
        ).first()

        if not service_config or not service_config.is_active:
            raise ValueError(f"서비스를 찾을 수 없거나 비활성화되었습니다: {service_code}")

        # 사주 서비스인 경우 사주 계산
        if service_code == "saju":
            calculator = SajuCalculator()
            birthdate = datetime.fromisoformat(str(request_data["birthdate"])).date()
            birth_time = request_data.get("birth_time")
            calendar_type = request_data.get("calendar", "solar")
            gender = request_data["gender"]
            name = request_data.get("name", "고객")

            saju_data = calculator.calculate_saju(
                birthdate=birthdate,
                birth_time=birth_time,
                calendar_type=calendar_type,
                gender=gender
            )

            # 이름을 사주 데이터에 추가
            saju_data["name"] = name

            # 사주 데이터를 request_data에 추가
            request_data["saju_data"] = saju_data

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

        return fortune_result, saju_data

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
            운세 결과 딕셔너리 (사주인 경우 saju_data 포함)
        """
        # user_key 생성
        user_key = self.generate_user_key(service_code, request_data)

        # 오늘 날짜
        today = date.today()

        # 캐시 조회
        cached = self.find_cached_result(service_code, user_key, today)

        if cached:
            result = {
                "service_code": service_code,
                "is_cached": True,
                "result_text": cached.result_text,
                "date": cached.date
            }

            # 캐시된 결과의 경우 사주 서비스면 다시 계산
            if service_code == "saju":
                calculator = SajuCalculator()
                birthdate = datetime.fromisoformat(str(request_data["birthdate"])).date()
                birth_time = request_data.get("birth_time")
                calendar_type = request_data.get("calendar", "solar")
                gender = request_data["gender"]
                name = request_data.get("name", "고객")

                saju_data = calculator.calculate_saju(
                    birthdate=birthdate,
                    birth_time=birth_time,
                    calendar_type=calendar_type,
                    gender=gender
                )

                # 이름을 사주 데이터에 추가
                saju_data["name"] = name

                result["saju_data"] = saju_data

            # 오늘의 운세인 경우 daily_fortune_info 추가 (캐시에서도 계산)
            if service_code == "today":
                calculator = SajuCalculator()
                daily_info = calculator.get_daily_fortune_info(today)
                result["daily_fortune_info"] = daily_info

            # 궁합인 경우 compatibility_info 추가 (캐시에서도 계산)
            if service_code == "match":
                calculator = SajuCalculator()
                birthdate_obj = datetime.fromisoformat(str(request_data["birthdate"])).date()
                partner_birthdate_obj = datetime.fromisoformat(str(request_data["partner_birthdate"])).date()
                compatibility = calculator.calculate_compatibility(
                    birthdate_obj, request_data["gender"],
                    partner_birthdate_obj, request_data["partner_gender"]
                )
                result["compatibility_info"] = compatibility

            # 신년운세인 경우 year_fortune_info 추가 (캐시에서도 계산)
            if service_code == "newyear2026":
                calculator = SajuCalculator()
                year_info = calculator.get_year_fortune_info(2026)
                result["year_fortune_info"] = year_info

            return result

        # 새로 생성
        new_result, saju_data = self.create_fortune_result(service_code, user_key, request_data)

        result = {
            "service_code": service_code,
            "is_cached": False,
            "result_text": new_result.result_text,
            "date": new_result.date
        }

        if saju_data:
            result["saju_data"] = saju_data

        # 오늘의 운세인 경우 daily_fortune_info 추가
        if service_code == "today" and "daily_fortune_info" in request_data:
            result["daily_fortune_info"] = request_data["daily_fortune_info"]

        # 궁합인 경우 compatibility_info 추가
        if service_code == "match" and "compatibility_info" in request_data:
            result["compatibility_info"] = request_data["compatibility_info"]

        # 신년운세인 경우 year_fortune_info 추가
        if service_code == "newyear2026" and "year_fortune_info" in request_data:
            result["year_fortune_info"] = request_data["year_fortune_info"]

        return result

    def generate_user_key(self, service_code: str, request_data: dict) -> str:
        """
        user_key 생성

        Args:
            service_code: 서비스 코드
            request_data: 요청 데이터

        Returns:
            SHA256 해시 문자열
        """
        # 꿈해몽은 꿈 내용으로 키 생성
        if service_code == "dream":
            dream_content = request_data.get("dream_content", "")
            # 꿈 내용을 해시화하여 user_key로 사용
            import hashlib
            return hashlib.sha256(dream_content.encode()).hexdigest()

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

        # 오늘의 길흉일 정보 계산
        calculator = SajuCalculator()
        daily_info = calculator.get_daily_fortune_info(date.today())

        # 계산된 데이터를 data에 추가 (결과 화면에서 사용)
        data['daily_fortune_info'] = daily_info

        return template.format(
            character_name=config.character_name,
            character_emoji=config.character_emoji,
            name=name,
            birthdate=birthdate,
            gender=gender,
            birth_time=birth_time,
            zodiac=zodiac,
            today=today_str,
            today_ganzhi=daily_info['ganzhi_kr'],
            today_ganzhi_hanja=daily_info['ganzhi_full'],
            today_ohang=daily_info['ohang'],
            today_sinsal=daily_info['sinsal'],
            today_luck=daily_info['luck_level'],
            good_activities=', '.join(daily_info['good_activities']),
            bad_activities=', '.join(daily_info['bad_activities'])
        )

    def build_saju_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """사주팔자 프롬프트"""
        template = self._load_prompt_template("saju")

        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"
        calendar = "양력" if data.get("calendar", "solar") == "solar" else "음력"
        birth_time = data.get("birth_time", "모름")

        # 사주 계산 데이터 포맷팅
        saju_info = ""
        if "saju_data" in data:
            sd = data["saju_data"]
            pillars = sd.get("pillars", {})

            # 사주팔자
            cheongan = pillars.get("cheongan", [])
            jiji = pillars.get("jiji", [])
            sipsung = pillars.get("sipsung", [])
            sipiunsung = pillars.get("sipiunsung", [])

            saju_info += f"\n[사주 정보]\n"
            saju_info += f"- 사주팔자: 시주({cheongan[0]}{jiji[0]}) 일주({cheongan[1]}{jiji[1]}) 월주({cheongan[2]}{jiji[2]}) 년주({cheongan[3]}{jiji[3]})\n"
            saju_info += f"- 일간: {sd.get('day_gan')}\n"
            saju_info += f"- 십성: 시({sipsung[0]}) 일({sipsung[1]}) 월({sipsung[2]}) 년({sipsung[3]})\n"
            saju_info += f"- 십이운성: 시({sipiunsung[0]}) 일({sipiunsung[1]}) 월({sipiunsung[2]}) 년({sipiunsung[3]})\n"

            # 오행 분석
            ohang = sd.get("ohang", {})
            saju_info += f"\n[오행 분석]\n"
            for elem, elem_name in [('木', '목'), ('火', '화'), ('土', '토'), ('金', '금'), ('水', '수')]:
                if elem in ohang:
                    info = ohang[elem]
                    saju_info += f"- {elem_name}({elem}): {info['count']}개 ({info['percent']:.1f}%) - {info['status']}\n"

            # 신강신약 및 용신
            strength = sd.get("strength", {})
            yongsin = sd.get("yongsin", {})
            saju_info += f"\n[신강신약 & 용신]\n"
            saju_info += f"- 신강신약: {strength.get('level', '중화')}\n"
            saju_info += f"- 용신: {yongsin.get('yongsin')}\n"
            saju_info += f"- 희신: {yongsin.get('heesin')}\n"
            saju_info += f"- 기신: {yongsin.get('gisin')}\n"

        return template.format(
            character_name=config.character_name,
            name=name,
            birthdate=birthdate,
            gender=gender,
            calendar=calendar,
            birth_time=birth_time
        ) + saju_info

    def build_match_prompt(self, data: dict, config: FortuneServiceConfig) -> str:
        """사주궁합 프롬프트"""
        template = self._load_prompt_template("match")

        name = data.get("name", "고객")
        birthdate = data["birthdate"]
        gender = "남성" if data["gender"] == "male" else "여성"

        partner_name = data.get("partner_name", "상대방")
        partner_birthdate = data["partner_birthdate"]
        partner_gender = "남성" if data["partner_gender"] == "male" else "여성"

        # 궁합 분석 계산
        calculator = SajuCalculator()
        birthdate_obj = datetime.fromisoformat(str(birthdate)).date()
        partner_birthdate_obj = datetime.fromisoformat(str(partner_birthdate)).date()

        compatibility = calculator.calculate_compatibility(
            birthdate_obj, data["gender"],
            partner_birthdate_obj, data["partner_gender"]
        )

        # 계산된 데이터를 data에 추가 (결과 화면에서 사용)
        data['compatibility_info'] = compatibility

        return template.format(
            character_name=config.character_name,
            name=name,
            birthdate=birthdate,
            gender=gender,
            partner_name=partner_name,
            partner_birthdate=partner_birthdate,
            partner_gender=partner_gender,
            compatibility_score=compatibility['score'],
            compatibility_level=compatibility['level'],
            person1_ilju=compatibility['person1']['day_pillar'],
            person1_ohang=compatibility['person1']['ohang'],
            person2_ilju=compatibility['person2']['day_pillar'],
            person2_ohang=compatibility['person2']['ohang'],
            ohang_relation_type=compatibility['ohang_relation']['type'],
            ohang_relation_desc=compatibility['ohang_relation']['description'],
            ilju_relation=compatibility['ilju_compatibility']['gan_relation'],
            ilju_desc=compatibility['ilju_compatibility']['description'],
            jiji_relation_type=compatibility['jiji_relation']['type'],
            jiji_relation_desc=compatibility['jiji_relation']['description']
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
        birth_time = data.get("birth_time", "모름")
        year = int(str(birthdate)[:4])
        zodiac = get_zodiac(year)

        # 2026년 간지 및 길일 정보 계산
        calculator = SajuCalculator()
        year_info = calculator.get_year_fortune_info(2026)

        # 계산된 데이터를 data에 추가 (결과 화면에서 사용)
        data['year_fortune_info'] = year_info

        return template.format(
            name=name,
            birthdate=birthdate,
            gender=gender,
            birth_time=birth_time,
            zodiac=zodiac,
            year_ganzhi_kr=year_info['ganzhi_kr'],
            year_ganzhi_hanja=year_info['ganzhi_hanja'],
            year_ohang=year_info['ohang'],
            year_description=year_info['description']
        )

    def format_custom_prompt(self, template: str, data: dict) -> str:
        """커스텀 프롬프트 템플릿 포매팅"""
        return template.format(**data)
