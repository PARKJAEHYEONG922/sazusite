"""
AI가 사주 용어를 제대로 이해하는지 테스트
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Gemini API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 테스트 프롬프트
test_cases = [
    {
        "title": "천간합 이해도",
        "prompt": """
당신은 전문 사주 상담가입니다.

사주 정보:
- 천간합: 년간(庚)과 시간(乙)이 합하여 금으로 화합니다.

위 정보를 바탕으로 이 천간합이 무엇을 의미하는지 한 문장으로 설명해주세요.
"""
    },
    {
        "title": "천을귀인 이해도",
        "prompt": """
당신은 전문 사주 상담가입니다.

신살 정보:
- 길신: 천을귀인(丑) - 귀인의 도움을 받는 길신입니다. 어려움에서 도움을 받을 수 있습니다.

위 정보를 바탕으로 천을귀인이 있는 사람의 운세를 한 문장으로 설명해주세요.
"""
    },
    {
        "title": "지지충 이해도",
        "prompt": """
당신은 전문 사주 상담가입니다.

합충형파해 정보:
- 지지충: 년지(子)와 월지(午)이 충을 이룹니다. 변동과 충돌이 있을 수 있습니다.

위 정보를 바탕으로 이 지지충이 무엇을 의미하는지 한 문장으로 설명해주세요.
"""
    },
    {
        "title": "공망 이해도",
        "prompt": """
당신은 전문 사주 상담가입니다.

신살 정보:
- 흉신: 공망(午) - 허무함이나 공허함을 느낄 수 있습니다. 일이 뜻대로 안 될 때가 있습니다.

위 정보를 바탕으로 공망이 있는 사람이 주의해야 할 점을 한 문장으로 설명해주세요.
"""
    }
]

print("=" * 80)
print("AI 사주 용어 이해도 테스트")
print("=" * 80)
print()

for i, test in enumerate(test_cases, 1):
    print(f"\n[테스트 {i}] {test['title']}")
    print("-" * 80)

    try:
        response = model.generate_content(test['prompt'])
        print(f"AI 답변: {response.text.strip()}")
    except Exception as e:
        print(f"오류 발생: {e}")

    print()

print("=" * 80)
print("테스트 완료!")
print("=" * 80)
