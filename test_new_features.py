"""
새로 추가된 합충형파해 및 신살 계산 기능 테스트
"""
from datetime import date
from app.services.saju_calculator import SajuCalculator

# 계산기 인스턴스
calc = SajuCalculator()

# 테스트 생년월일: 1990년 6월 2일 (양력), 오후 2시
birthdate = date(1990, 6, 2)
birth_time = "14:00"

print("=" * 80)
print("사주 계산 테스트 - 새로운 기능 (합충형파해, 신살)")
print("=" * 80)
print(f"생년월일: {birthdate}")
print(f"출생시간: {birth_time}")
print()

# 사주 계산
result = calc.calculate_saju(birthdate, birth_time, 'solar', 'male')

# 기본 사주 출력
print("=" * 80)
print("기본 사주팔자")
print("=" * 80)
pillars_display = {
    'year': f"{result['pillars']['cheongan'][3]}{result['pillars']['jiji'][3]}",
    'month': f"{result['pillars']['cheongan'][2]}{result['pillars']['jiji'][2]}",
    'day': f"{result['pillars']['cheongan'][1]}{result['pillars']['jiji'][1]}",
    'hour': f"{result['pillars']['cheongan'][0]}{result['pillars']['jiji'][0]}"
}
print(f"년주: {pillars_display['year']}")
print(f"월주: {pillars_display['month']}")
print(f"일주: {pillars_display['day']}")
print(f"시주: {pillars_display['hour']}")
print()

# 합충형파해 출력
print("=" * 80)
print("합충형파해 분석 (NEW!)")
print("=" * 80)
hap_chung = result['hap_chung_hyeong_pa_hae']
print(f"요약: {hap_chung['summary']}")
print()

if hap_chung['cheongan_hap']:
    print("【천간합】")
    for item in hap_chung['cheongan_hap']:
        print(f"  - {item['description']}")
    print()

if hap_chung['jiji_yukhap']:
    print("【지지 육합】")
    for item in hap_chung['jiji_yukhap']:
        print(f"  - {item['description']}")
    print()

if hap_chung['jiji_samhap']:
    print("【지지 삼합】")
    for item in hap_chung['jiji_samhap']:
        print(f"  - {item['description']}")
    print()

if hap_chung['jiji_chung']:
    print("【지지 충】")
    for item in hap_chung['jiji_chung']:
        print(f"  - {item['description']}")
    print()

if hap_chung['jiji_hyeong']:
    print("【지지 형】")
    for item in hap_chung['jiji_hyeong']:
        print(f"  - {item['description']}")
    print()

if hap_chung['jiji_hae']:
    print("【지지 해】")
    for item in hap_chung['jiji_hae']:
        print(f"  - {item['description']}")
    print()

# 신살 출력
print("=" * 80)
print("신살 분석 (NEW!)")
print("=" * 80)
sinsals = result['sinsals']

if sinsals['beneficial']:
    print("【길신 (吉神)】")
    for item in sinsals['beneficial']:
        print(f"  ★ {item['name']} ({item['position']})")
        print(f"     {item['description']}")
    print()

if sinsals['neutral']:
    print("【중립 신살】")
    for item in sinsals['neutral']:
        print(f"  ◆ {item['name']} ({item['position']})")
        print(f"     {item['description']}")
    print()

if sinsals['harmful']:
    print("【흉신 (凶神)】")
    for item in sinsals['harmful']:
        print(f"  ▼ {item['name']} ({item['position']})")
        print(f"     {item['description']}")
    print()

if not (sinsals['beneficial'] or sinsals['neutral'] or sinsals['harmful']):
    print("특별한 신살이 없습니다.")
    print()

# 기존 기능도 정상 작동 확인
print("=" * 80)
print("기존 기능 확인")
print("=" * 80)
print(f"오행 분석: {result['ohang']}")
print(f"신강신약: {result['strength']}")
print(f"용신/희신/기신: {result['yongsin']}")
print()

print("=" * 80)
print("테스트 완료!")
print("=" * 80)
