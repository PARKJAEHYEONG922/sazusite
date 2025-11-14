"""
Gemini 2.0 Flash API 비용 계산 (2025년 11월 기준)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('=== 현재 사용 중인 모델 ===')
print('모델: gemini-2.0-flash-exp (실험 버전)')
print('상태: 현재 무료 (실험 기간 중)')
print('')

# Gemini 2.0 Flash 정식 버전 가격 (예상)
# Input: $0.10 per 1M tokens (모든 컨텍스트)
# Output: $0.30 per 1M tokens (1.5 Flash와 동일 예상)

input_price_per_1m = 0.10
output_price_per_1m = 0.30

# 한글 토큰 계산
dream_input_chars = 200
dream_input_tokens = int(dream_input_chars * 2.5)
dream_output_tokens = 2048
dream_output_chars = int(dream_output_tokens / 2.5)

# 비용 계산
input_cost = (dream_input_tokens / 1000000) * input_price_per_1m
output_cost = (dream_output_tokens / 1000000) * output_price_per_1m
total_cost_usd = input_cost + output_cost

# 원화 환산
exchange_rate = 1400
total_cost_krw = total_cost_usd * exchange_rate

print('=== Gemini 2.0 Flash 정식 버전 예상 비용 ===')
print(f'입력 토큰: {dream_input_tokens} tokens (~{dream_input_chars}글자)')
print(f'출력 토큰: {dream_output_tokens} tokens (~{dream_output_chars}글자)')
print(f'')
print(f'입력 비용: ${input_cost:.6f} ({input_cost * exchange_rate:.2f}원)')
print(f'출력 비용: ${output_cost:.6f} ({output_cost * exchange_rate:.2f}원)')
print(f'총 비용: ${total_cost_usd:.6f} ({total_cost_krw:.2f}원/회)')
print(f'')
print('=== 월간 사용량별 예상 비용 (2048 tokens 기준) ===')

for count in [100, 500, 1000]:
    monthly_cost_usd = total_cost_usd * count
    monthly_cost_krw = total_cost_krw * count
    print(f'{count}회: ${monthly_cost_usd:.2f} ({monthly_cost_krw:.0f}원/월)')

print(f'')
print('참고: 현재는 실험 버전(gemini-2.0-flash-exp)으로 무료입니다.')
print('정식 버전 출시 후 위 가격이 적용될 예정입니다.')
