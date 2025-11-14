"""
Gemini API 비용 계산 (2025년 11월 기준)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Gemini 1.5 Flash 가격 (2025년 최신)
# https://ai.google.dev/pricing
# Input: $0.075 per 1M tokens (128K context 이하)
# Output: $0.30 per 1M tokens (128K context 이하)

input_price_per_1m = 0.075
output_price_per_1m = 0.30

# 한글 토큰 계산 (한글 1글자 = 약 2.5토큰)
# 꿈해몽 예시
dream_input_chars = 200  # 프롬프트 + 사용자 꿈 내용
dream_input_tokens = int(dream_input_chars * 2.5)

dream_output_tokens = 2048  # 현재 설정값
dream_output_chars = int(dream_output_tokens / 2.5)

# 비용 계산 (USD)
input_cost = (dream_input_tokens / 1000000) * input_price_per_1m
output_cost = (dream_output_tokens / 1000000) * output_price_per_1m
total_cost_usd = input_cost + output_cost

# 원화 환산 (1 USD = 1,400 KRW 가정)
exchange_rate = 1400
total_cost_krw = total_cost_usd * exchange_rate

print('=== Gemini 1.5 Flash API 비용 계산 (2025년 11월 기준) ===')
print(f'입력 토큰: {dream_input_tokens} tokens (~{dream_input_chars}글자)')
print(f'출력 토큰: {dream_output_tokens} tokens (~{dream_output_chars}글자)')
print(f'')
print(f'입력 비용: ${input_cost:.6f} ({input_cost * exchange_rate:.2f}원)')
print(f'출력 비용: ${output_cost:.6f} ({output_cost * exchange_rate:.2f}원)')
print(f'총 비용: ${total_cost_usd:.6f} ({total_cost_krw:.2f}원/회)')
print(f'')
print('=== 다양한 출력 토큰별 비용 비교 ===')

for tokens in [512, 1024, 2048]:
    out_cost = (tokens / 1000000) * output_price_per_1m
    total = (dream_input_tokens / 1000000) * input_price_per_1m + out_cost
    total_krw = total * exchange_rate
    chars = int(tokens / 2.5)
    print(f'{tokens} tokens (~{chars}글자): ${total:.6f} ({total_krw:.2f}원/회)')

print(f'')
print('=== 월간 사용량별 예상 비용 (현재 2048 tokens 기준) ===')
for count in [100, 500, 1000]:
    monthly_cost_usd = total_cost_usd * count
    monthly_cost_krw = total_cost_krw * count
    print(f'{count}회: ${monthly_cost_usd:.2f} ({monthly_cost_krw:.0f}원/월)')
