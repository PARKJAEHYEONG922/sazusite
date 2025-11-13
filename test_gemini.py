"""
Gemini API 테스트 스크립트
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.gemini_service import gemini_service

def test_gemini():
    """Gemini API 연결 테스트"""
    print("Gemini API 테스트 시작...")
    print("-" * 50)

    try:
        # 간단한 테스트 프롬프트
        test_prompt = "안녕하세요! 간단한 연결 테스트입니다. '연결 성공!'이라고 한 줄로 답해주세요."

        print(f"\n프롬프트: {test_prompt}\n")
        print("응답 대기 중...")

        response = gemini_service.generate_content(test_prompt)

        print("\n[성공] Gemini API 응답:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        print("\n[OK] Gemini API가 정상 작동합니다!")

    except Exception as e:
        print(f"\n[ERROR] Gemini API 오류: {e}")
        return False

    return True

if __name__ == "__main__":
    test_gemini()
