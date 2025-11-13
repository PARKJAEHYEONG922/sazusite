"""
사주팔자 계산 서비스
"""
from datetime import datetime, date
from typing import Dict, List, Tuple
from korean_lunar_calendar import KoreanLunarCalendar


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

        # 대운 계산
        daeun = self.calculate_daeun(year, pillars['month'][0], pillars['month'][1], gender)

        # 신강신약 계산
        strength = self.calculate_strength(pillars, ohang_analysis)

        # 용신 계산
        yongsin = self.calculate_yongsin(day_gan, ohang_analysis, strength)

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
            'yongsin': yongsin
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
                       gender: str) -> Dict:
        """대운 계산"""
        # 양남음녀는 순행, 음남양녀는 역행
        year_gan_index = (birth_year - 4) % 10
        is_yang_year = year_gan_index % 2 == 0
        is_male = gender == 'male'

        is_forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

        # 대운 시작 나이 (간단히 5세로 설정, 실제로는 절기 기준 계산 필요)
        start_age = 5

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
