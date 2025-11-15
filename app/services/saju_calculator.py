"""
사주팔자 계산 서비스
"""
from datetime import datetime, date
from typing import Dict, List, Tuple
from app.utils.korean_lunar_calendar import KoreanLunarCalendar


class SajuCalculator:
    """사주팔자 계산 클래스"""

    # 천간 (天干) - 10개
    CHEONGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    CHEONGAN_KR = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']

    # 지지 (地支) - 12개
    JIJI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    JIJI_KR = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

    # 오행 (五行)
    OHANG = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水',
        '寅': '木', '卯': '木',
        '巳': '火', '午': '火',
        '辰': '土', '戌': '土', '丑': '土', '未': '土',
        '申': '金', '酉': '金',
        '子': '水', '亥': '水'
    }

    # 십성 (十星) - 일간 기준
    SIPSUNG_MAP = {
        ('甲', '甲'): '比肩', ('甲', '乙'): '劫財', ('甲', '丙'): '食神', ('甲', '丁'): '傷官',
        ('甲', '戊'): '偏財', ('甲', '己'): '正財', ('甲', '庚'): '偏官', ('甲', '辛'): '正官',
        ('甲', '壬'): '偏印', ('甲', '癸'): '正印',

        ('乙', '甲'): '劫財', ('乙', '乙'): '比肩', ('乙', '丙'): '傷官', ('乙', '丁'): '食神',
        ('乙', '戊'): '正財', ('乙', '己'): '偏財', ('乙', '庚'): '正官', ('乙', '辛'): '偏官',
        ('乙', '壬'): '正印', ('乙', '癸'): '偏印',

        ('丙', '甲'): '偏印', ('丙', '乙'): '正印', ('丙', '丙'): '比肩', ('丙', '丁'): '劫財',
        ('丙', '戊'): '食神', ('丙', '己'): '傷官', ('丙', '庚'): '偏財', ('丙', '辛'): '正財',
        ('丙', '壬'): '偏官', ('丙', '癸'): '正官',

        ('丁', '甲'): '正印', ('丁', '乙'): '偏印', ('丁', '丙'): '劫財', ('丁', '丁'): '比肩',
        ('丁', '戊'): '傷官', ('丁', '己'): '食神', ('丁', '庚'): '正財', ('丁', '辛'): '偏財',
        ('丁', '壬'): '正官', ('丁', '癸'): '偏官',

        ('戊', '甲'): '偏官', ('戊', '乙'): '正官', ('戊', '丙'): '偏印', ('戊', '丁'): '正印',
        ('戊', '戊'): '比肩', ('戊', '己'): '劫財', ('戊', '庚'): '食神', ('戊', '辛'): '傷官',
        ('戊', '壬'): '偏財', ('戊', '癸'): '正財',

        ('己', '甲'): '正官', ('己', '乙'): '偏官', ('己', '丙'): '正印', ('己', '丁'): '偏印',
        ('己', '戊'): '劫財', ('己', '己'): '比肩', ('己', '庚'): '傷官', ('己', '辛'): '食神',
        ('己', '壬'): '正財', ('己', '癸'): '偏財',

        ('庚', '甲'): '偏財', ('庚', '乙'): '正財', ('庚', '丙'): '偏官', ('庚', '丁'): '正官',
        ('庚', '戊'): '偏印', ('庚', '己'): '正印', ('庚', '庚'): '比肩', ('庚', '辛'): '劫財',
        ('庚', '壬'): '食神', ('庚', '癸'): '傷官',

        ('辛', '甲'): '正財', ('辛', '乙'): '偏財', ('辛', '丙'): '正官', ('辛', '丁'): '偏官',
        ('辛', '戊'): '正印', ('辛', '己'): '偏印', ('辛', '庚'): '劫財', ('辛', '辛'): '比肩',
        ('辛', '壬'): '傷官', ('辛', '癸'): '食神',

        ('壬', '甲'): '食神', ('壬', '乙'): '傷官', ('壬', '丙'): '偏財', ('壬', '丁'): '正財',
        ('壬', '戊'): '偏官', ('壬', '己'): '正官', ('壬', '庚'): '偏印', ('壬', '辛'): '正印',
        ('壬', '壬'): '比肩', ('壬', '癸'): '劫財',

        ('癸', '甲'): '傷官', ('癸', '乙'): '食神', ('癸', '丙'): '正財', ('癸', '丁'): '偏財',
        ('癸', '戊'): '正官', ('癸', '己'): '偏官', ('癸', '庚'): '正印', ('癸', '辛'): '偏印',
        ('癸', '壬'): '劫財', ('癸', '癸'): '比肩',
    }

    # 십이운성 (十二運星)
    SIPIUNSUNG_MAP = {
        '甲': {'寅': '建祿', '卯': '帝旺', '辰': '衰', '巳': '病', '午': '死', '未': '墓',
              '申': '絶', '酉': '胎', '戌': '養', '亥': '長生', '子': '沐浴', '丑': '冠帶'},
        '乙': {'寅': '帝旺', '卯': '建祿', '辰': '衰', '巳': '病', '午': '死', '未': '墓',
              '申': '絶', '酉': '胎', '戌': '養', '亥': '長生', '子': '沐浴', '丑': '冠帶'},
        '丙': {'寅': '長生', '卯': '沐浴', '辰': '冠帶', '巳': '建祿', '午': '帝旺', '未': '衰',
              '申': '病', '酉': '死', '戌': '墓', '亥': '絶', '子': '胎', '丑': '養'},
        '丁': {'寅': '長生', '卯': '沐浴', '辰': '冠帶', '巳': '建祿', '午': '帝旺', '未': '衰',
              '申': '病', '酉': '死', '戌': '墓', '亥': '絶', '子': '胎', '丑': '養'},
        '戊': {'寅': '長生', '卯': '沐浴', '辰': '冠帶', '巳': '建祿', '午': '帝旺', '未': '衰',
              '申': '病', '酉': '死', '戌': '墓', '亥': '絶', '子': '胎', '丑': '養'},
        '己': {'寅': '長生', '卯': '沐浴', '辰': '冠帶', '巳': '建祿', '午': '帝旺', '未': '衰',
              '申': '病', '酉': '死', '戌': '墓', '亥': '絶', '子': '胎', '丑': '養'},
        '庚': {'寅': '絶', '卯': '胎', '辰': '養', '巳': '長生', '午': '沐浴', '未': '冠帶',
              '申': '建祿', '酉': '帝旺', '戌': '衰', '亥': '病', '子': '死', '丑': '墓'},
        '辛': {'寅': '絶', '卯': '胎', '辰': '養', '巳': '長生', '午': '沐浴', '未': '冠帶',
              '申': '建祿', '酉': '帝旺', '戌': '衰', '亥': '病', '子': '死', '丑': '墓'},
        '壬': {'寅': '病', '卯': '死', '辰': '墓', '巳': '絶', '午': '胎', '未': '養',
              '申': '長生', '酉': '沐浴', '戌': '冠帶', '亥': '建祿', '子': '帝旺', '丑': '衰'},
        '癸': {'寅': '病', '卯': '死', '辰': '墓', '巳': '絶', '午': '胎', '未': '養',
              '申': '長生', '酉': '沐浴', '戌': '冠帶', '亥': '建祿', '子': '帝旺', '丑': '衰'},
    }

    def __init__(self):
        self.calendar = KoreanLunarCalendar()

    def get_ganzhi(self, year: int, month: int, day: int, hour: int = 0) -> Dict[str, Tuple[str, str]]:
        """
        년월일시의 간지를 계산

        Args:
            year: 년도
            month: 월
            day: 일
            hour: 시 (0-23)

        Returns:
            {'year': (천간, 지지), 'month': (천간, 지지), 'day': (천간, 지지), 'hour': (천간, 지지)}
        """
        # 년주 계산 (입춘 기준)
        year_gan = self.CHEONGAN[(year - 4) % 10]
        year_ji = self.JIJI[(year - 4) % 12]

        # 월주 계산 (절입 기준)
        month_index = (year * 12 + month + 11) % 60
        month_gan = self.CHEONGAN[month_index % 10]
        month_ji = self.JIJI[(month - 1) % 12]

        # 일주 계산
        base_date = datetime(1900, 1, 1)
        target_date = datetime(year, month, day)
        days_diff = (target_date - base_date).days
        day_index = (days_diff + 16) % 60  # 1900-01-01 = 甲戌일
        day_gan = self.CHEONGAN[day_index % 10]
        day_ji = self.JIJI[day_index % 12]

        # 시주 계산
        hour_ji_index = ((hour + 1) // 2) % 12
        hour_ji = self.JIJI[hour_ji_index]

        # 시간의 천간은 일간에 따라 결정
        day_gan_index = self.CHEONGAN.index(day_gan)
        hour_gan_index = (day_gan_index % 5) * 2 + hour_ji_index
        hour_gan = self.CHEONGAN[hour_gan_index % 10]

        return {
            'year': (year_gan, year_ji),
            'month': (month_gan, month_ji),
            'day': (day_gan, day_ji),
            'hour': (hour_gan, hour_ji)
        }

    def calculate_saju(self, birthdate: date, birth_time: str = None,
                      calendar_type: str = 'solar', gender: str = 'male') -> Dict:
        """
        사주팔자 계산

        Args:
            birthdate: 생년월일
            birth_time: 태어난 시간 (HH:MM 형식 또는 "23-01" 형식)
            calendar_type: 'solar' 또는 'lunar'
            gender: 'male' 또는 'female'

        Returns:
            사주 데이터
        """
        year = birthdate.year
        month = birthdate.month
        day = birthdate.day

        # 음력인 경우 양력으로 변환
        if calendar_type == 'lunar':
            self.calendar.setLunarDate(year, month, day, False)
            solar = self.calendar.SolarIsoFormat().split('-')
            year, month, day = int(solar[0]), int(solar[1]), int(solar[2])

        # 시간 파싱
        hour = 0
        if birth_time and birth_time != '미상':
            if '-' in birth_time:
                hour = int(birth_time.split('-')[0])
            elif ':' in birth_time:
                hour = int(birth_time.split(':')[0])
            else:
                # 단순 숫자 형식 (예: "23", "01")
                hour = int(birth_time)

        # 간지 계산
        ganzhi = self.get_ganzhi(year, month, day, hour)

        # 일간 (나를 나타내는 천간)
        day_gan = ganzhi['day'][0]

        # 사주팔자 구성
        pillars = {
            'year': ganzhi['year'],
            'month': ganzhi['month'],
            'day': ganzhi['day'],
            'hour': ganzhi['hour']
        }

        # 십성 계산
        sipsung = {
            'year': self.get_sipsung(day_gan, pillars['year'][0]),
            'month': self.get_sipsung(day_gan, pillars['month'][0]),
            'day': '日干',
            'hour': self.get_sipsung(day_gan, pillars['hour'][0])
        }

        # 지지의 십성
        sipsung_jiji = {
            'year': self.get_sipsung_jiji(day_gan, pillars['year'][1]),
            'month': self.get_sipsung_jiji(day_gan, pillars['month'][1]),
            'day': self.get_sipsung_jiji(day_gan, pillars['day'][1]),
            'hour': self.get_sipsung_jiji(day_gan, pillars['hour'][1])
        }

        # 십이운성
        sipiunsung = {
            'year': self.get_sipiunsung(day_gan, pillars['year'][1]),
            'month': self.get_sipiunsung(day_gan, pillars['month'][1]),
            'day': self.get_sipiunsung(day_gan, pillars['day'][1]),
            'hour': self.get_sipiunsung(day_gan, pillars['hour'][1])
        }

        # 오행 분석
        ohang_analysis = self.analyze_ohang(pillars)

        # 대운 계산 (생월과 생일 정보 전달)
        daeun = self.calculate_daeun(year, pillars['month'][0], pillars['month'][1], gender, month, day)

        # 신강신약 계산
        strength = self.calculate_strength(pillars, ohang_analysis)

        # 용신 계산
        yongsin = self.calculate_yongsin(day_gan, ohang_analysis, strength)

        # 합충형파해 계산
        hap_chung = self.calculate_hap_chung_hyeong_pa_hae(pillars)

        # 신살 계산
        sinsals = self.calculate_sinsals(pillars)

        return {
            'pillars': {
                'cheongan': [pillars['hour'][0], pillars['day'][0],
                           pillars['month'][0], pillars['year'][0]],
                'jiji': [pillars['hour'][1], pillars['day'][1],
                        pillars['month'][1], pillars['year'][1]],
                'sipsung': [sipsung['hour'], sipsung['day'],
                          sipsung['month'], sipsung['year']],
                'sipsung_jiji': [sipsung_jiji['hour'], sipsung_jiji['day'],
                               sipsung_jiji['month'], sipsung_jiji['year']],
                'sipiunsung': [sipiunsung['hour'], sipiunsung['day'],
                             sipiunsung['month'], sipiunsung['year']]
            },
            'day_gan': day_gan,
            'ohang': ohang_analysis,
            'daeun': daeun,
            'strength': strength,
            'yongsin': yongsin,
            'hap_chung_hyeong_pa_hae': hap_chung,  # 합충형파해 추가
            'sinsals': sinsals  # 신살 추가
        }

    def get_sipsung(self, day_gan: str, target_gan: str) -> str:
        """십성 구하기"""
        key = (day_gan, target_gan)
        return self.SIPSUNG_MAP.get(key, '')

    def get_sipsung_jiji(self, day_gan: str, jiji: str) -> str:
        """지지의 주요 십성 구하기 (지장간 중 본기 기준)"""
        # 지장간 본기
        jiji_bongi = {
            '子': '癸', '丑': '己', '寅': '甲', '卯': '乙',
            '辰': '戊', '巳': '丙', '午': '丁', '未': '己',
            '申': '庚', '酉': '辛', '戌': '戊', '亥': '壬'
        }
        bongi = jiji_bongi.get(jiji, '')
        return self.get_sipsung(day_gan, bongi)

    def get_sipiunsung(self, day_gan: str, jiji: str) -> str:
        """십이운성 구하기"""
        if day_gan in self.SIPIUNSUNG_MAP:
            return self.SIPIUNSUNG_MAP[day_gan].get(jiji, '')
        return ''

    def analyze_ohang(self, pillars: Dict) -> Dict:
        """오행 분석"""
        ohang_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}

        # 천간 오행
        for pillar in ['hour', 'day', 'month', 'year']:
            gan = pillars[pillar][0]
            if gan in self.OHANG:
                ohang_count[self.OHANG[gan]] += 1

        # 지지 오행
        for pillar in ['hour', 'day', 'month', 'year']:
            ji = pillars[pillar][1]
            if ji in self.OHANG:
                ohang_count[self.OHANG[ji]] += 1

        # 총 개수
        total = sum(ohang_count.values())

        # 퍼센트 계산
        ohang_percent = {}
        for ohang, count in ohang_count.items():
            percent = round((count / total * 100), 1) if total > 0 else 0
            status = self.get_ohang_status(percent)
            ohang_percent[ohang] = {
                'count': count,
                'percent': percent,
                'status': status
            }

        return ohang_percent

    def get_ohang_status(self, percent: float) -> str:
        """오행 상태 판단"""
        if percent < 10:
            return '부족'
        elif percent < 15:
            return '약함'
        elif percent < 25:
            return '적정'
        elif percent < 35:
            return '발달'
        else:
            return '과다'

    def calculate_daeun(self, birth_year: int, month_gan: str, month_ji: str,
                       gender: str, birth_month: int = 1, birth_day: int = 1) -> Dict:
        """대운 계산"""
        # 양남음녀는 순행, 음남양녀는 역행
        year_gan_index = (birth_year - 4) % 10
        is_yang_year = year_gan_index % 2 == 0
        is_male = gender == 'male'

        is_forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

        # 대운 시작 나이 계산 (절기 기준 간략화)
        # 실제로는 생월생일에 따라 다음/이전 절기까지 일수를 계산하지만,
        # 여기서는 생월을 기준으로 근사치 계산
        # 생월 초순(1-10일): 1~3세, 중순(11-20일): 4~6세, 하순(21-31일): 7~9세
        if birth_day <= 10:
            start_age = 2
        elif birth_day <= 20:
            start_age = 5
        else:
            start_age = 8

        # 대운 주기 생성
        month_gan_index = self.CHEONGAN.index(month_gan)
        month_ji_index = self.JIJI.index(month_ji)

        periods = []
        current_year = birth_year + start_age

        for i in range(7):  # 7개 대운 생성
            if is_forward:
                daeun_gan = self.CHEONGAN[(month_gan_index + i + 1) % 10]
                daeun_ji = self.JIJI[(month_ji_index + i + 1) % 12]
            else:
                daeun_gan = self.CHEONGAN[(month_gan_index - i - 1) % 10]
                daeun_ji = self.JIJI[(month_ji_index - i - 1) % 12]

            periods.append({
                'year': current_year,
                'age': start_age + i * 10,
                'gan': daeun_gan,
                'ji': daeun_ji
            })
            current_year += 10

        return {
            'start_age': start_age,
            'periods': periods
        }

    def calculate_strength(self, pillars: Dict, ohang_analysis: Dict) -> Dict:
        """신강신약 계산"""
        day_gan = pillars['day'][0]
        day_gan_ohang = self.OHANG[day_gan]

        # 일간과 같은 오행의 비율
        same_ohang_percent = ohang_analysis[day_gan_ohang]['percent']

        # 신강신약 레벨 결정
        if same_ohang_percent < 8:
            level = '극약'
            position = 5
        elif same_ohang_percent < 12:
            level = '태약'
            position = 15
        elif same_ohang_percent < 18:
            level = '신약'
            position = 30
        elif same_ohang_percent < 28:
            level = '중화'
            position = 50
        elif same_ohang_percent < 35:
            level = '신강'
            position = 70
        elif same_ohang_percent < 42:
            level = '태강'
            position = 85
        else:
            level = '극왕'
            position = 95

        return {
            'level': level,
            'position': position
        }

    def calculate_yongsin(self, day_gan: str, ohang_analysis: Dict, strength: Dict) -> Dict:
        """용신 계산"""
        day_gan_ohang = self.OHANG[day_gan]

        # 오행 상생상극 관계
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 생
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}    # 극

        # 신약한 경우 - 나를 생하는 오행이 용신
        if strength['level'] in ['극약', '태약', '신약']:
            reverse_sheng = {v: k for k, v in sheng.items()}
            yongsin_ohang = reverse_sheng.get(day_gan_ohang, '水')
            heesin_ohang = day_gan_ohang  # 희신은 나와 같은 오행

            # 기신은 나를 극하는 오행
            reverse_ke = {v: k for k, v in ke.items()}
            gisin_ohang = reverse_ke.get(day_gan_ohang, '土')

        # 신강한 경우 - 나를 설기하는 오행이 용신
        else:
            yongsin_ohang = sheng.get(day_gan_ohang, '水')  # 내가 생하는 오행
            heesin_ohang = ke.get(day_gan_ohang, '土')      # 희신은 나를 극하는 오행
            gisin_ohang = day_gan_ohang                      # 기신은 나와 같은 오행

        # 오행을 한글로 변환
        ohang_kr = {'木': '목', '火': '화', '土': '토', '金': '금', '水': '수'}

        return {
            'yongsin': ohang_kr.get(yongsin_ohang, '수'),
            'heesin': ohang_kr.get(heesin_ohang, '금'),
            'gisin': ohang_kr.get(gisin_ohang, '토')
        }

    def get_daily_fortune_info(self, target_date: date) -> Dict:
        """
        특정 날짜의 길흉일 정보 계산

        Args:
            target_date: 조회할 날짜

        Returns:
            {
                'ganzhi': (천간, 지지),
                'ganzhi_kr': '갑자',
                'ohang': '木',
                'luck_level': '대길' | '중길' | '소길' | '평' | '소흉' | '중흉' | '대흉',
                'good_activities': ['이사', '계약', ...],
                'bad_activities': ['결혼', '개업', ...],
                'description': '설명'
            }
        """
        year = target_date.year
        month = target_date.month
        day = target_date.day

        # 일주 간지 계산
        base_date = datetime(1900, 1, 1)
        target_datetime = datetime(year, month, day)
        days_diff = (target_datetime - base_date).days
        day_index = (days_diff + 16) % 60
        day_gan = self.CHEONGAN[day_index % 10]
        day_ji = self.JIJI[day_index % 12]

        # 한글 간지
        gan_kr = self.CHEONGAN_KR[day_index % 10]
        ji_kr = self.JIJI_KR[day_index % 12]
        ganzhi_kr = f'{gan_kr}{ji_kr}'

        # 오행
        day_ohang = self.OHANG[day_gan]

        # 12신살 계산 (지지 기반)
        ji_index = self.JIJI.index(day_ji)

        # 12신살 순서: 청룡, 명당, 천형, 주작, 금궤, 천덕, 백호, 옥당, 천뢰, 현무, 사명, 구진
        sinsals = ['청룡', '명당', '천형', '주작', '금궤', '천덕',
                   '백호', '옥당', '천뢰', '현무', '사명', '구진']

        # 월건 기준으로 12신살 시작점 조정 (간략화)
        start_index = (month - 1) % 12
        sinsal_index = (ji_index + start_index) % 12
        sinsal = sinsals[sinsal_index]

        # 길흉 판단
        luck_level = self._determine_luck_level(sinsal, day_gan, day_ji)

        # 좋은 일 / 나쁜 일
        good_activities, bad_activities = self._get_activities(sinsal, day_ji)

        # 설명
        description = self._get_luck_description(sinsal, luck_level)

        return {
            'ganzhi': (day_gan, day_ji),
            'ganzhi_kr': ganzhi_kr,
            'ganzhi_full': f'{day_gan}{day_ji}',
            'ohang': day_ohang,
            'sinsal': sinsal,
            'luck_level': luck_level,
            'good_activities': good_activities,
            'bad_activities': bad_activities,
            'description': description
        }

    def _determine_luck_level(self, sinsal: str, gan: str, ji: str) -> str:
        """길흉 등급 판단"""
        # 대길일
        if sinsal in ['청룡', '명당', '금궤', '천덕', '옥당']:
            return '대길'
        # 중길일
        elif sinsal in ['사명']:
            return '중길'
        # 흉일
        elif sinsal in ['천형', '백호', '천뢰', '현무']:
            return '대흉'
        # 소흉일
        elif sinsal in ['주작', '구진']:
            return '중흉'
        else:
            return '평'

    def _get_activities(self, sinsal: str, ji: str) -> tuple[list, list]:
        """좋은 일과 나쁜 일 판단"""
        good = []
        bad = []

        # 신살별 좋은 일
        if sinsal in ['청룡', '명당']:
            good = ['이사', '입주', '계약', '거래', '여행', '상담']
        elif sinsal in ['금궤', '천덕']:
            good = ['재물관리', '투자', '저축', '구매']
        elif sinsal in ['옥당']:
            good = ['시험', '면접', '발표', '학업']
        elif sinsal in ['사명']:
            good = ['대인관계', '모임', '상담']

        # 신살별 나쁜 일
        if sinsal in ['천형', '백호']:
            bad = ['수술', '소송', '분쟁', '이사', '개업']
        elif sinsal in ['주작']:
            bad = ['계약', '약속', '중요한 결정']
        elif sinsal in ['천뢰', '현무']:
            bad = ['여행', '이동', '새로운 시작']
        elif sinsal in ['구진']:
            bad = ['재물 거래', '투자', '대출']

        # 기본값
        if not good:
            good = ['일상 업무', '휴식']
        if not bad:
            bad = ['무리한 일']

        return good, bad

    def _get_luck_description(self, sinsal: str, luck_level: str) -> str:
        """길흉 설명"""
        descriptions = {
            '청룡': '청룡의 기운이 함께하는 날입니다. 만사형통하며 하는 일마다 길한 날입니다.',
            '명당': '명당의 밝은 기운이 가득한 날입니다. 좋은 소식과 기회가 찾아올 수 있습니다.',
            '천형': '천형살이 있는 날로 분쟁이나 구설수를 조심해야 합니다.',
            '주작': '주작의 날로 말조심이 필요하며, 중요한 결정은 미루는 것이 좋습니다.',
            '금궤': '금궤의 재물운이 함께하는 날입니다. 재물과 관련된 일이 길합니다.',
            '천덕': '천덕의 복이 깃든 날입니다. 덕을 쌓는 일에 좋은 날입니다.',
            '백호': '백호살이 있는 날로 급한 일이나 위험한 일은 피하는 것이 좋습니다.',
            '옥당': '옥당의 학문 기운이 있는 날입니다. 공부나 시험에 좋은 날입니다.',
            '천뢰': '천뢰의 기운이 있어 조심스러운 행동이 필요한 날입니다.',
            '현무': '현무의 날로 은밀한 일은 좋으나 큰 일은 삼가는 것이 좋습니다.',
            '사명': '사명의 날로 사람을 만나거나 인연을 맺기에 좋은 날입니다.',
            '구진': '구진의 날로 재물 관리에 신중을 기해야 합니다.'
        }
        return descriptions.get(sinsal, '평범한 날입니다.')

    def calculate_compatibility(self, birthdate1: date, gender1: str, birthdate2: date, gender2: str) -> Dict:
        """
        두 사람의 사주 궁합 분석

        Args:
            birthdate1: 첫 번째 사람 생년월일
            gender1: 첫 번째 사람 성별
            birthdate2: 두 번째 사람 생년월일
            gender2: 두 번째 사람 성별

        Returns:
            궁합 분석 정보
        """
        # 각자의 사주 계산
        saju1 = self.calculate_saju(birthdate1, None, 'solar', gender1)
        saju2 = self.calculate_saju(birthdate2, None, 'solar', gender2)

        # 일주 추출
        day_gan1 = saju1['pillars']['cheongan'][2]
        day_ji1 = saju1['pillars']['jiji'][2]
        day_gan2 = saju2['pillars']['cheongan'][2]
        day_ji2 = saju2['pillars']['jiji'][2]

        # 일간(日干)의 오행 추출 (CHEONGAN은 이미 한자)
        ohang1 = self.OHANG.get(day_gan1, '土')
        ohang2 = self.OHANG.get(day_gan2, '土')

        # 오행 상생상극 판단
        ohang_relation = self._get_ohang_relation(ohang1, ohang2)

        # 일주 궁합 판단
        ilju_compatibility = self._get_ilju_compatibility(day_gan1, day_ji1, day_gan2, day_ji2)

        # 지지 육합/삼합/충/형/해 판단
        jiji_relation = self._get_jiji_relation(day_ji1, day_ji2)

        # 총 궁합 점수 계산 (100점 만점)
        score = self._calculate_compatibility_score(ohang_relation, ilju_compatibility, jiji_relation)

        return {
            'person1': {
                'day_pillar': f'{day_gan1}{day_ji1}',
                'ohang': ohang1
            },
            'person2': {
                'day_pillar': f'{day_gan2}{day_ji2}',
                'ohang': ohang2
            },
            'ohang_relation': ohang_relation,
            'ilju_compatibility': ilju_compatibility,
            'jiji_relation': jiji_relation,
            'score': score,
            'level': self._get_compatibility_level(score)
        }

    def _get_ohang_relation(self, ohang1: str, ohang2: str) -> Dict:
        """오행 상생상극 관계"""
        # 상생: 木生火, 火生土, 土生金, 金生水, 水生木
        saengsaeng = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }

        # 상극: 木克土, 土克水, 水克火, 火克金, 金克木
        sanggeuk = {
            '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
        }

        relation_type = '비화'  # 기본값: 같은 오행 (比和)
        description = f'{ohang1}와 {ohang2}는 같은 오행으로 서로 비슷한 성향을 가집니다.'
        score = 70

        if ohang1 != ohang2:
            if saengsaeng.get(ohang1) == ohang2:
                relation_type = '상생'
                description = f'{ohang1}가 {ohang2}를 생하는 관계입니다. 한 분이 다른 분을 도와주는 좋은 인연입니다.'
                score = 90
            elif saengsaeng.get(ohang2) == ohang1:
                relation_type = '상생'
                description = f'{ohang2}가 {ohang1}를 생하는 관계입니다. 서로 도움이 되는 좋은 인연입니다.'
                score = 90
            elif sanggeuk.get(ohang1) == ohang2:
                relation_type = '상극'
                description = f'{ohang1}가 {ohang2}를 극하는 관계입니다. 서로 다른 성향이지만 배려하면 좋은 관계가 됩니다.'
                score = 50
            elif sanggeuk.get(ohang2) == ohang1:
                relation_type = '상극'
                description = f'{ohang2}가 {ohang1}를 극하는 관계입니다. 차이를 이해하고 존중하는 것이 중요합니다.'
                score = 50
            else:
                relation_type = '중립'
                description = f'{ohang1}와 {ohang2}는 직접적인 상생상극 관계는 아니지만 조화를 이룰 수 있습니다.'
                score = 65

        return {
            'type': relation_type,
            'description': description,
            'score': score
        }

    def _get_ilju_compatibility(self, gan1: str, ji1: str, gan2: str, ji2: str) -> Dict:
        """일주 궁합 분석"""
        # 천간 합: 갑기합토, 을경합금, 병신합수, 정임합목, 무계합화
        cheongan_hap = {
            ('甲', '己'): ('土', '좋은 궁합'),
            ('乙', '庚'): ('金', '좋은 궁합'),
            ('丙', '辛'): ('水', '좋은 궁합'),
            ('丁', '壬'): ('木', '좋은 궁합'),
            ('戊', '癸'): ('火', '좋은 궁합')
        }

        gan_relation = '일반'
        gan_desc = '천간이 특별한 합을 이루지는 않지만 나쁘지 않은 관계입니다.'

        for (g1, g2), (result, desc) in cheongan_hap.items():
            if (gan1 == g1 and gan2 == g2) or (gan1 == g2 and gan2 == g1):
                gan_relation = '천간합'
                gan_desc = f'천간이 합을 이루어 {result}로 화합니다. {desc}입니다.'
                break

        if gan1 == gan2:
            gan_relation = '천간동일'
            gan_desc = '천간이 같아 비슷한 성향과 생각을 가지고 있습니다.'

        return {
            'gan_relation': gan_relation,
            'description': gan_desc
        }

    def _get_jiji_relation(self, ji1: str, ji2: str) -> Dict:
        """지지 관계 분석 (육합, 삼합, 충, 형, 해)"""
        # 육합: 子丑, 寅亥, 卯戌, 辰酉, 巳申, 午未
        yukhap = [
            ('子', '丑'), ('寅', '亥'), ('卯', '戌'),
            ('辰', '酉'), ('巳', '申'), ('午', '未')
        ]

        # 충: 子午, 丑未, 寅申, 卯酉, 辰戌, 巳亥
        chung = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]

        relation_type = '일반'
        description = '지지가 특별한 관계를 이루지는 않습니다.'
        score = 70

        # 육합 체크
        for j1, j2 in yukhap:
            if (ji1 == j1 and ji2 == j2) or (ji1 == j2 and ji2 == j1):
                relation_type = '육합'
                description = '지지가 육합을 이루어 서로를 잘 돕는 매우 좋은 관계입니다.'
                score = 95
                break

        # 충 체크
        for j1, j2 in chung:
            if (ji1 == j1 and ji2 == j2) or (ji1 == j2 and ji2 == j1):
                relation_type = '충'
                description = '지지가 충을 이룹니다. 서로 다른 성향이 부딪힐 수 있으나 이해하면 보완관계가 됩니다.'
                score = 45
                break

        # 같은 지지
        if ji1 == ji2:
            relation_type = '지지동일'
            description = '지지가 같아 비슷한 생활 패턴과 가치관을 가집니다.'
            score = 75

        return {
            'type': relation_type,
            'description': description,
            'score': score
        }

    def _calculate_compatibility_score(self, ohang_rel: Dict, ilju_comp: Dict, jiji_rel: Dict) -> int:
        """궁합 총점 계산"""
        # 오행 40%, 지지 관계 40%, 천간 20% 비중
        score = int(
            ohang_rel['score'] * 0.4 +
            jiji_rel['score'] * 0.4 +
            70 * 0.2  # 천간은 기본 70점
        )

        # 천간합이 있으면 +10점
        if ilju_comp['gan_relation'] == '천간합':
            score += 10

        return min(100, max(0, score))

    def _get_compatibility_level(self, score: int) -> str:
        """궁합 레벨 판정"""
        if score >= 90:
            return '천생연분'
        elif score >= 80:
            return '매우 좋음'
        elif score >= 70:
            return '좋음'
        elif score >= 60:
            return '보통'
        elif score >= 50:
            return '노력 필요'
        else:
            return '많은 이해 필요'

    def get_year_fortune_info(self, year: int) -> Dict:
        """
        특정 년도의 천간지지와 길일 정보

        Args:
            year: 년도 (예: 2026)

        Returns:
            년도 간지 정보 및 길일 목록
        """
        # 년 간지 계산 (1984년 = 갑자년 기준)
        base_year = 1984
        year_diff = year - base_year
        year_index = year_diff % 60

        year_gan = self.CHEONGAN[year_index % 10]
        year_ji = self.JIJI[year_index % 12]
        year_gan_kr = self.CHEONGAN_KR[year_index % 10]
        year_ji_kr = self.JIJI_KR[year_index % 12]

        # 년의 오행
        ohang_map = {
            '甲': '木', '乙': '木',
            '丙': '火', '丁': '火',
            '戊': '土', '己': '土',
            '庚': '金', '辛': '金',
            '壬': '水', '癸': '水'
        }
        year_ohang = ohang_map.get(year_gan, '土')

        # 월별 간지 계산 (간단 버전 - 정월 기준)
        monthly_ganzhi = self._calculate_monthly_ganzhi(year, year_gan)

        # 대길일 찾기 (청룡, 명당, 금궤, 천덕 날)
        lucky_days = self._find_lucky_days(year)

        return {
            'year': year,
            'ganzhi_kr': f'{year_gan_kr}{year_ji_kr}',
            'ganzhi_hanja': f'{year_gan}{year_ji}',
            'ganzhi_full': f'{year_gan}{year_ji}({year_gan_kr}{year_ji_kr})년',
            'ohang': year_ohang,
            'monthly_ganzhi': monthly_ganzhi,
            'lucky_days': lucky_days,
            'description': f'{year}년은 {year_gan}{year_ji}년으로, {year_ohang}의 기운이 강한 해입니다.'
        }

    def _calculate_monthly_ganzhi(self, year: int, year_gan: str) -> list:
        """월별 간지 계산"""
        # 월건 계산 (갑기년은 병인월로 시작)
        month_start_gan = {
            '甲': 2, '己': 2,  # 병(丙)
            '乙': 4, '庚': 4,  # 무(戊)
            '丙': 6, '辛': 6,  # 경(庚)
            '丁': 8, '壬': 8,  # 임(壬)
            '戊': 0, '癸': 0   # 갑(甲)
        }

        start_gan_idx = month_start_gan.get(year_gan, 0)
        month_ji_start = 2  # 인월(寅月)부터 시작

        monthly = []
        for month in range(1, 13):
            gan_idx = (start_gan_idx + month - 1) % 10
            ji_idx = (month_ji_start + month - 1) % 12

            monthly.append({
                'month': month,
                'ganzhi_kr': f'{self.CHEONGAN_KR[gan_idx]}{self.JIJI_KR[ji_idx]}',
                'ganzhi_hanja': f'{self.CHEONGAN[gan_idx]}{self.JIJI[ji_idx]}'
            })

        return monthly

    def _find_lucky_days(self, year: int) -> list:
        """년도의 대길일 찾기 (샘플)"""
        from datetime import date as dt_date, timedelta

        lucky_days = []
        start_date = dt_date(year, 1, 1)

        # 1년간 순회하며 청룡, 명당, 금궤, 천덕 날 찾기
        for day_offset in range(0, 365, 10):  # 성능을 위해 10일마다만 체크
            check_date = start_date + timedelta(days=day_offset)
            if check_date.year != year:
                break

            daily_info = self.get_daily_fortune_info(check_date)

            if daily_info['sinsal'] in ['청룡', '명당', '금궤', '천덕']:
                if len(lucky_days) < 12:  # 최대 12개만
                    lucky_days.append({
                        'date': check_date.strftime('%m월 %d일'),
                        'ganzhi': daily_info['ganzhi_kr'],
                        'sinsal': daily_info['sinsal']
                    })

        return lucky_days

    def calculate_hap_chung_hyeong_pa_hae(self, pillars: Dict) -> Dict:
        """
        합충형파해 분석 (사주 내부의 관계)

        Args:
            pillars: 사주 기둥 정보 {'year': [간, 지], 'month': [간, 지], ...}

        Returns:
            합충형파해 분석 결과
        """
        result = {
            'cheongan_hap': [],      # 천간합
            'jiji_yukhap': [],        # 지지 육합
            'jiji_samhap': [],        # 지지 삼합
            'jiji_chung': [],         # 지지 충
            'jiji_hyeong': [],        # 지지 형
            'jiji_hae': [],           # 지지 해
            'summary': ''
        }

        # 천간 추출
        gans = [pillars['year'][0], pillars['month'][0], pillars['day'][0], pillars['hour'][0]]
        gan_positions = ['년간', '월간', '일간', '시간']

        # 지지 추출
        jis = [pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]]
        ji_positions = ['년지', '월지', '일지', '시지']

        # === 천간합 체크 ===
        cheongan_hap_pairs = {
            ('甲', '己'): '토',
            ('乙', '庚'): '금',
            ('丙', '辛'): '수',
            ('丁', '壬'): '목',
            ('戊', '癸'): '화'
        }

        for i in range(len(gans)):
            for j in range(i + 1, len(gans)):
                pair = (gans[i], gans[j])
                reverse_pair = (gans[j], gans[i])

                if pair in cheongan_hap_pairs:
                    result['cheongan_hap'].append({
                        'positions': [gan_positions[i], gan_positions[j]],
                        'gans': [gans[i], gans[j]],
                        'result': cheongan_hap_pairs[pair],
                        'description': f'{gan_positions[i]}({gans[i]})과 {gan_positions[j]}({gans[j]})이 합하여 {cheongan_hap_pairs[pair]}으로 화합니다.'
                    })
                elif reverse_pair in cheongan_hap_pairs:
                    result['cheongan_hap'].append({
                        'positions': [gan_positions[i], gan_positions[j]],
                        'gans': [gans[i], gans[j]],
                        'result': cheongan_hap_pairs[reverse_pair],
                        'description': f'{gan_positions[i]}({gans[i]})과 {gan_positions[j]}({gans[j]})이 합하여 {cheongan_hap_pairs[reverse_pair]}으로 화합니다.'
                    })

        # === 지지 육합 체크 ===
        yukhap_pairs = {
            ('子', '丑'): '토', ('寅', '亥'): '목', ('卯', '戌'): '화',
            ('辰', '酉'): '금', ('巳', '申'): '수', ('午', '未'): '화'
        }

        for i in range(len(jis)):
            for j in range(i + 1, len(jis)):
                pair = (jis[i], jis[j])
                reverse_pair = (jis[j], jis[i])

                if pair in yukhap_pairs:
                    result['jiji_yukhap'].append({
                        'positions': [ji_positions[i], ji_positions[j]],
                        'jis': [jis[i], jis[j]],
                        'result': yukhap_pairs[pair],
                        'description': f'{ji_positions[i]}({jis[i]})와 {ji_positions[j]}({jis[j]})이 육합을 이룹니다.'
                    })
                elif reverse_pair in yukhap_pairs:
                    result['jiji_yukhap'].append({
                        'positions': [ji_positions[i], ji_positions[j]],
                        'jis': [jis[i], jis[j]],
                        'result': yukhap_pairs[reverse_pair],
                        'description': f'{ji_positions[i]}({jis[i]})와 {ji_positions[j]}({jis[j]})이 육합을 이룹니다.'
                    })

        # === 지지 삼합 체크 ===
        samhap_groups = [
            (['申', '子', '辰'], '수'),
            (['寅', '午', '戌'], '화'),
            (['巳', '酉', '丑'], '금'),
            (['亥', '卯', '未'], '목')
        ]

        for group, element in samhap_groups:
            found_jis = []
            found_positions = []
            for i, ji in enumerate(jis):
                if ji in group:
                    found_jis.append(ji)
                    found_positions.append(ji_positions[i])

            if len(found_jis) >= 2:
                result['jiji_samhap'].append({
                    'positions': found_positions,
                    'jis': found_jis,
                    'result': element,
                    'complete': len(found_jis) == 3,
                    'description': f'{", ".join(found_positions)}이 {element} 삼합을 이룹니다.' if len(found_jis) == 3 else f'{", ".join(found_positions)}이 {element} 삼합의 일부를 이룹니다.'
                })

        # === 지지 충 체크 ===
        chung_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]

        for i in range(len(jis)):
            for j in range(i + 1, len(jis)):
                for c1, c2 in chung_pairs:
                    if (jis[i] == c1 and jis[j] == c2) or (jis[i] == c2 and jis[j] == c1):
                        result['jiji_chung'].append({
                            'positions': [ji_positions[i], ji_positions[j]],
                            'jis': [jis[i], jis[j]],
                            'description': f'{ji_positions[i]}({jis[i]})와 {ji_positions[j]}({jis[j]})이 충을 이룹니다. 변동과 충돌이 있을 수 있습니다.'
                        })

        # === 지지 형 체크 ===
        hyeong_groups = [
            (['寅', '巳', '申'], '무은지형'),
            (['丑', '未', '戌'], '세형'),
            (['子', '卯'], '무례지형')
        ]

        for group, hyeong_type in hyeong_groups:
            found_jis = []
            found_positions = []
            for i, ji in enumerate(jis):
                if ji in group:
                    found_jis.append(ji)
                    found_positions.append(ji_positions[i])

            if len(found_jis) >= 2:
                result['jiji_hyeong'].append({
                    'positions': found_positions,
                    'jis': found_jis,
                    'type': hyeong_type,
                    'description': f'{", ".join(found_positions)}이 {hyeong_type}을 이룹니다.'
                })

        # === 지지 해 체크 ===
        hae_pairs = [
            ('子', '未'), ('丑', '午'), ('寅', '巳'),
            ('卯', '辰'), ('申', '亥'), ('酉', '戌')
        ]

        for i in range(len(jis)):
            for j in range(i + 1, len(jis)):
                for h1, h2 in hae_pairs:
                    if (jis[i] == h1 and jis[j] == h2) or (jis[i] == h2 and jis[j] == h1):
                        result['jiji_hae'].append({
                            'positions': [ji_positions[i], ji_positions[j]],
                            'jis': [jis[i], jis[j]],
                            'description': f'{ji_positions[i]}({jis[i]})와 {ji_positions[j]}({jis[j]})이 해를 이룹니다.'
                        })

        # === 종합 요약 ===
        summary_parts = []
        if result['cheongan_hap']:
            summary_parts.append(f"천간합 {len(result['cheongan_hap'])}개")
        if result['jiji_yukhap']:
            summary_parts.append(f"육합 {len(result['jiji_yukhap'])}개")
        if result['jiji_samhap']:
            summary_parts.append(f"삼합 {len(result['jiji_samhap'])}개")
        if result['jiji_chung']:
            summary_parts.append(f"충 {len(result['jiji_chung'])}개")
        if result['jiji_hyeong']:
            summary_parts.append(f"형 {len(result['jiji_hyeong'])}개")
        if result['jiji_hae']:
            summary_parts.append(f"해 {len(result['jiji_hae'])}개")

        result['summary'] = ', '.join(summary_parts) if summary_parts else '특별한 합충형파해가 없습니다.'

        return result

    def calculate_sinsals(self, pillars: Dict) -> Dict:
        """
        주요 신살 계산

        Args:
            pillars: 사주 기둥 정보

        Returns:
            신살 목록과 설명
        """
        result = {
            'beneficial': [],  # 길신
            'harmful': [],     # 흉신
            'neutral': []      # 중립
        }

        day_gan = pillars['day'][0]
        day_ji = pillars['day'][1]
        year_ji = pillars['year'][1]

        jis = [pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]]

        # === 천을귀인 (天乙貴人) - 최고의 귀인 ===
        cheoneur_map = {
            '甲': ['丑', '未'], '戊': ['丑', '未'],
            '乙': ['子', '申'], '己': ['子', '申'],
            '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }

        if day_gan in cheoneur_map:
            for ji in jis:
                if ji in cheoneur_map[day_gan]:
                    result['beneficial'].append({
                        'name': '천을귀인',
                        'position': ji,
                        'description': '귀인의 도움을 받는 길신입니다. 어려움에서 도움을 받을 수 있습니다.'
                    })
                    break

        # === 역마살 (驛馬殺) - 이동수 ===
        yeokma_map = {
            '寅': '申', '午': '寅', '戌': '申',
            '申': '寅', '子': '寅', '辰': '申',
            '巳': '亥', '酉': '巳', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '亥'
        }

        if year_ji in yeokma_map:
            target = yeokma_map[year_ji]
            for ji in jis:
                if ji == target:
                    result['neutral'].append({
                        'name': '역마살',
                        'position': ji,
                        'description': '이동과 변화가 많은 삶입니다. 여행, 이사, 직장 이동이 잦을 수 있습니다.'
                    })
                    break

        # === 도화살 (桃花殺) - 인기운 ===
        dohwa_map = {
            '寅': '卯', '午': '卯', '戌': '卯',
            '申': '酉', '子': '酉', '辰': '酉',
            '巳': '午', '酉': '午', '丑': '午',
            '亥': '子', '卯': '子', '未': '子'
        }

        if year_ji in dohwa_map:
            target = dohwa_map[year_ji]
            for ji in jis:
                if ji == target:
                    result['neutral'].append({
                        'name': '도화살',
                        'position': ji,
                        'description': '인기가 많고 이성운이 좋습니다. 예술적 재능이 있을 수 있습니다.'
                    })
                    break

        # === 화개살 (華蓋殺) - 예술/종교 ===
        hwagae_map = {
            '寅': '戌', '午': '戌', '戌': '戌',
            '申': '辰', '子': '辰', '辰': '辰',
            '巳': '丑', '酉': '丑', '丑': '丑',
            '亥': '未', '卯': '未', '未': '未'
        }

        if year_ji in hwagae_map:
            target = hwagae_map[year_ji]
            for ji in jis:
                if ji == target:
                    result['neutral'].append({
                        'name': '화개살',
                        'position': ji,
                        'description': '예술적, 종교적 재능이 있습니다. 학문과 연구에도 뛰어날 수 있습니다.'
                    })
                    break

        # === 양인살 (羊刃殺) - 강한 성격 ===
        yangin_map = {
            '甲': '卯', '乙': '寅',
            '丙': '午', '丁': '巳',
            '戊': '午', '己': '巳',
            '庚': '酉', '辛': '申',
            '壬': '子', '癸': '亥'
        }

        if day_gan in yangin_map:
            target = yangin_map[day_gan]
            for ji in jis:
                if ji == target:
                    result['harmful'].append({
                        'name': '양인살',
                        'position': ji,
                        'description': '성격이 강하고 극단적일 수 있습니다. 리더십이 있으나 충동적일 수 있습니다.'
                    })
                    break

        # === 공망 (空亡) ===
        # 60갑자별 공망 (간단 버전: 년주 기준)
        year_gan = pillars['year'][0]
        year_gan_idx = self.CHEONGAN.index(year_gan)

        # 간단 공망 계산 (10천간 - 12지지 = 2개 공망)
        gongmang_idx1 = (year_gan_idx + 10) % 12
        gongmang_idx2 = (year_gan_idx + 11) % 12

        for ji in jis:
            ji_idx = self.JIJI.index(ji)
            if ji_idx == gongmang_idx1 or ji_idx == gongmang_idx2:
                result['harmful'].append({
                    'name': '공망',
                    'position': ji,
                    'description': '허무함이나 공허함을 느낄 수 있습니다. 일이 뜻대로 안 될 때가 있습니다.'
                })
                break

        # === 괴강살 (魁罡殺) ===
        goegang_pairs = [
            ('庚', '辰'), ('庚', '戌'),
            ('壬', '辰'), ('戊', '戌')
        ]

        if (day_gan, day_ji) in goegang_pairs:
            result['neutral'].append({
                'name': '괴강살',
                'position': day_ji,
                'description': '특별한 성격과 능력을 가졌습니다. 강한 카리스마가 있으나 고집이 셀 수 있습니다.'
            })

        return result
