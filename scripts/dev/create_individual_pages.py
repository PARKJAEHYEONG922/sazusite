"""
개별 시작 페이지 생성 스크립트
fortune_form.html을 각 서비스별로 복사
"""
import shutil
from pathlib import Path

# 소스 파일
source_file = Path("app/templates/public/fortune_form.html")

# 대상 디렉토리
target_dir = Path("app/templates/fortune")
target_dir.mkdir(parents=True, exist_ok=True)

# 생성할 서비스 코드 목록
services = ['today', 'saju', 'match', 'dream', 'newyear2026', 'taro']

print("개별 시작 페이지 생성 중...")

for service_code in services:
    target_file = target_dir / f"{service_code}.html"

    # 파일이 이미 있으면 건너뛰기
    if target_file.exists():
        print(f"⏭️  {service_code}.html - 이미 존재함 (건너뜀)")
        continue

    # 파일 복사
    shutil.copy(source_file, target_file)
    print(f"✅ {service_code}.html - 생성 완료")

print("\n✨ 모든 개별 시작 페이지 생성 완료!")
print(f"📂 위치: {target_dir.absolute()}")
