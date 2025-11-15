"""
운세 생성 서비스
"""
from datetime import date, datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from pathlib import Path
import random
import string

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

    def __init__(self, db: Session, client_ip: Optional[str] = None):
        self.db = db
        self.client_ip = client_ip
        self._prompt_cache = {}

    def _generate_unique_share_code(self, length=8, max_attempts=100) -> str:
        """
        중복되지 않는 고유한 공유 코드 생성

        Args:
            length: 코드 길이 (기본 8자)
            max_attempts: 최대 시도 횟수

        Returns:
            고유한 share_code 문자열

        Raises:
            RuntimeError: max_attempts 초과 시
        """
        chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9 (62가지)

        for attempt in range(max_attempts):
            code = ''.join(random.choices(chars, k=length))

            # DB에서 중복 체크
            existing = self.db.query(FortuneResult).filter(
                FortuneResult.share_code == code
            ).first()

            if not existing:
                return code

        # 100번 시도해도 중복이면 길이를 늘려서 재시도
        return self._generate_unique_share_code(length + 1, max_attempts)

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
        request_data: dict,
        share_code: str = None
    ) -> tuple[FortuneResult, Optional[Dict]]:
        """
        새로운 운세 생성

        Args:
            service_code: 서비스 코드
            user_key: 사용자 식별 키
            request_data: 요청 데이터
            share_code: 미리 생성된 share_code (선택적)

        Returns:
            (생성된 운세 결과, 사주 데이터 또는 None)
        """
        saju_data = None

        # 2026 신년운세는 별도 처리
        if service_code == "newyear2026":
            prompt = self.build_newyear2026_prompt(request_data)
            result_text = gemini_service.generate_content(prompt, service_code=service_code, db=self.db, client_ip=self.client_ip)

            serializable_data = self._make_json_serializable(request_data)

            # share_code가 없으면 생성
            if not share_code:
                share_code = self._generate_unique_share_code()

            fortune_result = FortuneResult(
                service_code=service_code,
                user_key=user_key,
                share_code=share_code,
                date=date.today(),
                request_payload=serializable_data,
                result_text=result_text,
                status="completed",
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
        result_text = gemini_service.generate_content(prompt, service_code=service_code, db=self.db, client_ip=self.client_ip)

        # request_data를 JSON 직렬화 가능하게 변환 (date 객체를 문자열로)
        serializable_data = self._make_json_serializable(request_data)

        # share_code가 없으면 생성
        if not share_code:
            share_code = self._generate_unique_share_code()

        # DB 저장
        fortune_result = FortuneResult(
            service_code=service_code,
            user_key=user_key,
            share_code=share_code,
            date=date.today(),
            request_payload=serializable_data,
            result_text=result_text,
            status="completed",
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
        request_data: dict,
        share_code: str = None
    ) -> Dict:
        """
        운세 조회 또는 생성 (메인 로직)

        Args:
            service_code: 서비스 코드
            request_data: 요청 데이터
            share_code: 미리 생성된 share_code (선택적)

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
            # share_code가 전달되었으면 새 레코드 생성 (공유용)
            if share_code:
                new_record = FortuneResult(
                    service_code=service_code,
                    user_key=user_key,
                    share_code=share_code,
                    date=today,
                    request_payload=cached.request_payload,
                    result_text=cached.result_text,
                    status="completed",
                    is_from_cache=True
                )
                self.db.add(new_record)
                self.db.commit()
                self.db.refresh(new_record)

                result = {
                    "id": new_record.id,
                    "share_code": new_record.share_code,
                    "service_code": service_code,
                    "is_cached": True,
                    "result_text": cached.result_text,
                    "date": cached.date
                }
            else:
                # share_code가 없으면 캐시된 레코드 그대로 사용
                result = {
                    "id": cached.id,
                    "share_code": cached.share_code,
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
        new_result, saju_data = self.create_fortune_result(service_code, user_key, request_data, share_code=share_code)

        result = {
            "id": new_result.id,
            "share_code": new_result.share_code,
            "service_code": service_code,
            "is_cached": False,
            "result_text": new_result.result_text,
            "date": new_result.date
        }

        if saju_data:
            result["saju_data"] = saju_data

        # 오늘의 운세인 경우 daily_fortune_info와 saju_data 추가
        if service_code == "today":
            if "daily_fortune_info" in request_data:
                result["daily_fortune_info"] = request_data["daily_fortune_info"]
            if "saju_data" in request_data:
                result["saju_data"] = request_data["saju_data"]

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
        birth_time = request_data.get("birth_time")  # 출생시간 추가

        # 궁합일 경우 상대방 정보 모두 포함
        partner_birthdate = None
        partner_name = None
        partner_gender = None
        partner_birth_time = None
        partner_calendar = None

        if service_code == "match":
            if "partner_birthdate" in request_data:
                partner_birthdate = datetime.fromisoformat(str(request_data["partner_birthdate"])).date()
            partner_name = request_data.get("partner_name")
            partner_gender = request_data.get("partner_gender")
            partner_birth_time = request_data.get("partner_birth_time")
            partner_calendar = request_data.get("partner_calendar")

        return build_user_key(
            name, birthdate, gender, partner_birthdate, birth_time,
            partner_name, partner_gender, partner_birth_time, partner_calendar
        )

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
        calendar = data.get("calendar", "solar")
        calendar_text = "양력" if calendar == "solar" else "음력"
        year = int(str(birthdate)[:4])
        zodiac = get_zodiac(year)
        today_str = date.today().strftime("%Y년 %m월 %d일")

        calculator = SajuCalculator()

        # 본인 사주팔자 계산
        birthdate_obj = datetime.fromisoformat(str(birthdate)).date()
        saju_data = calculator.calculate_saju(birthdate_obj, birth_time, calendar, data["gender"])

        # 오늘의 길흉일 정보 계산
        daily_info = calculator.get_daily_fortune_info(date.today())

        # 계산된 데이터를 data에 추가 (결과 화면에서 사용)
        data['daily_fortune_info'] = daily_info
        data['saju_data'] = saju_data

        # 사주 정보 텍스트 구성
        pillars = saju_data['pillars']
        saju_info = f"""
[본인의 사주팔자]
- 년주(年柱): {pillars['cheongan'][3]}{pillars['jiji'][3]}
- 월주(月柱): {pillars['cheongan'][2]}{pillars['jiji'][2]}
- 일주(日柱): {pillars['cheongan'][1]}{pillars['jiji'][1]} ← 일간(日干): {pillars['cheongan'][1]} (본인의 핵심)
- 시주(時柱): {pillars['cheongan'][0]}{pillars['jiji'][0]}
- 오행 분포: {saju_data['ohang']}
- 신강신약: {saju_data['strength']}
"""

        return template.format(
            character_name=config.character_name,
            character_emoji=config.character_emoji,
            name=name,
            birthdate=birthdate,
            gender=gender,
            birth_time=birth_time,
            calendar=calendar_text,
            zodiac=zodiac,
            today=today_str,
            saju_info=saju_info,
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

            # 합충형파해 분석 추가
            hap_chung = sd.get("hap_chung_hyeong_pa_hae", {})
            if hap_chung:
                saju_info += f"\n[합충형파해]\n"
                saju_info += f"- 요약: {hap_chung.get('summary', '없음')}\n"

                if hap_chung.get('cheongan_hap'):
                    saju_info += "- 천간합: "
                    for item in hap_chung['cheongan_hap']:
                        saju_info += f"{item['description']} "
                    saju_info += "\n"

                if hap_chung.get('jiji_yukhap'):
                    saju_info += "- 지지육합: "
                    for item in hap_chung['jiji_yukhap']:
                        saju_info += f"{item['description']} "
                    saju_info += "\n"

                if hap_chung.get('jiji_samhap'):
                    saju_info += "- 지지삼합: "
                    for item in hap_chung['jiji_samhap']:
                        saju_info += f"{item['description']} "
                    saju_info += "\n"

                if hap_chung.get('jiji_chung'):
                    saju_info += "- 지지충: "
                    for item in hap_chung['jiji_chung']:
                        saju_info += f"{item['description']} "
                    saju_info += "\n"

                if hap_chung.get('jiji_hyeong'):
                    saju_info += "- 지지형: "
                    for item in hap_chung['jiji_hyeong']:
                        saju_info += f"{item['description']} "
                    saju_info += "\n"

                if hap_chung.get('jiji_hae'):
                    saju_info += "- 지지해: "
                    for item in hap_chung['jiji_hae']:
                        saju_info += f"{item['description']} "
                    saju_info += "\n"

            # 신살 분석 추가
            sinsals = sd.get("sinsals", {})
            if sinsals:
                saju_info += f"\n[신살]\n"

                if sinsals.get('beneficial'):
                    saju_info += "- 길신: "
                    for item in sinsals['beneficial']:
                        saju_info += f"{item['name']}({item['description']}) "
                    saju_info += "\n"

                if sinsals.get('neutral'):
                    saju_info += "- 중립신살: "
                    for item in sinsals['neutral']:
                        saju_info += f"{item['name']}({item['description']}) "
                    saju_info += "\n"

                if sinsals.get('harmful'):
                    saju_info += "- 흉신: "
                    for item in sinsals['harmful']:
                        saju_info += f"{item['name']}({item['description']}) "
                    saju_info += "\n"

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
        birth_time = data.get("birth_time", "모름")
        calendar = data.get("calendar", "solar")
        calendar_text = "양력" if calendar == "solar" else "음력"

        partner_name = data.get("partner_name", "상대방")
        partner_birthdate = data["partner_birthdate"]
        partner_gender = "남성" if data["partner_gender"] == "male" else "여성"
        partner_birth_time = data.get("partner_birth_time", "모름")
        partner_calendar = data.get("partner_calendar", "solar")
        partner_calendar_text = "양력" if partner_calendar == "solar" else "음력"

        calculator = SajuCalculator()
        birthdate_obj = datetime.fromisoformat(str(birthdate)).date()
        partner_birthdate_obj = datetime.fromisoformat(str(partner_birthdate)).date()

        # 본인 사주 계산
        person1_saju = calculator.calculate_saju(birthdate_obj, birth_time, calendar, data["gender"])

        # 상대방 사주 계산
        person2_saju = calculator.calculate_saju(partner_birthdate_obj, partner_birth_time, partner_calendar, data["partner_gender"])

        # 궁합 분석 계산
        compatibility = calculator.calculate_compatibility(
            birthdate_obj, data["gender"],
            partner_birthdate_obj, data["partner_gender"]
        )

        # 계산된 데이터를 data에 추가 (결과 화면에서 사용)
        data['compatibility_info'] = compatibility
        data['person1_saju'] = person1_saju
        data['person2_saju'] = person2_saju

        # 본인 사주 정보 텍스트 구성
        p1_pillars = person1_saju['pillars']
        person1_info = f"""
[{name}님의 사주팔자]
- 년주: {p1_pillars['cheongan'][3]}{p1_pillars['jiji'][3]}
- 월주: {p1_pillars['cheongan'][2]}{p1_pillars['jiji'][2]}
- 일주: {p1_pillars['cheongan'][1]}{p1_pillars['jiji'][1]} ← 일간: {p1_pillars['cheongan'][1]}
- 시주: {p1_pillars['cheongan'][0]}{p1_pillars['jiji'][0]}
- 오행: {person1_saju['ohang']}
- 신강신약: {person1_saju['strength']}
"""

        # 상대방 사주 정보 텍스트 구성
        p2_pillars = person2_saju['pillars']
        person2_info = f"""
[{partner_name}님의 사주팔자]
- 년주: {p2_pillars['cheongan'][3]}{p2_pillars['jiji'][3]}
- 월주: {p2_pillars['cheongan'][2]}{p2_pillars['jiji'][2]}
- 일주: {p2_pillars['cheongan'][1]}{p2_pillars['jiji'][1]} ← 일간: {p2_pillars['cheongan'][1]}
- 시주: {p2_pillars['cheongan'][0]}{p2_pillars['jiji'][0]}
- 오행: {person2_saju['ohang']}
- 신강신약: {person2_saju['strength']}
"""

        # 두 사람의 합충형파해 분석
        hap_chung_analysis = ""

        # 본인 합충형파해
        p1_hap = person1_saju.get("hap_chung_hyeong_pa_hae", {})
        if p1_hap.get('summary'):
            hap_chung_analysis += f"\n[{name}님 사주 내부 관계]\n"
            hap_chung_analysis += f"- {p1_hap.get('summary')}\n"

        # 상대방 합충형파해
        p2_hap = person2_saju.get("hap_chung_hyeong_pa_hae", {})
        if p2_hap.get('summary'):
            hap_chung_analysis += f"\n[{partner_name}님 사주 내부 관계]\n"
            hap_chung_analysis += f"- {p2_hap.get('summary')}\n"

        # 두 사람의 신살
        sinsal_analysis = ""

        # 본인 신살
        p1_sinsals = person1_saju.get("sinsals", {})
        if p1_sinsals.get('beneficial') or p1_sinsals.get('harmful'):
            sinsal_analysis += f"\n[{name}님의 신살]\n"
            if p1_sinsals.get('beneficial'):
                sinsal_analysis += "- 길신: "
                for item in p1_sinsals['beneficial']:
                    sinsal_analysis += f"{item['name']} "
                sinsal_analysis += "\n"
            if p1_sinsals.get('harmful'):
                sinsal_analysis += "- 흉신: "
                for item in p1_sinsals['harmful']:
                    sinsal_analysis += f"{item['name']} "
                sinsal_analysis += "\n"

        # 상대방 신살
        p2_sinsals = person2_saju.get("sinsals", {})
        if p2_sinsals.get('beneficial') or p2_sinsals.get('harmful'):
            sinsal_analysis += f"\n[{partner_name}님의 신살]\n"
            if p2_sinsals.get('beneficial'):
                sinsal_analysis += "- 길신: "
                for item in p2_sinsals['beneficial']:
                    sinsal_analysis += f"{item['name']} "
                sinsal_analysis += "\n"
            if p2_sinsals.get('harmful'):
                sinsal_analysis += "- 흉신: "
                for item in p2_sinsals['harmful']:
                    sinsal_analysis += f"{item['name']} "
                sinsal_analysis += "\n"

        # 시간 정보 텍스트 생성
        birth_time_text = f"- 태어난 시간: {birth_time}"
        partner_birth_time_text = f"- 태어난 시간: {partner_birth_time}"

        return template.format(
            character_name=config.character_name,
            name=name,
            birthdate=birthdate,
            gender=gender,
            calendar=calendar_text,
            birth_time=birth_time_text,
            partner_name=partner_name,
            partner_birthdate=partner_birthdate,
            partner_gender=partner_gender,
            partner_calendar=partner_calendar_text,
            partner_birth_time=partner_birth_time_text,
            person1_info=person1_info,
            person2_info=person2_info,
            hap_chung_analysis=hap_chung_analysis,
            sinsal_analysis=sinsal_analysis,
            compatibility_score=compatibility['score'],
            compatibility_level=compatibility['level'],
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
