"""
기존 업로드된 이미지들을 WebP로 일괄 변환
"""
import sqlite3
from pathlib import Path
from app.utils.image_utils import convert_to_webp
import sys
import io

# Windows 인코딩 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def convert_existing_images():
    """uploads 폴더의 기존 이미지를 WebP로 변환"""
    upload_dir = Path("app/static/uploads")

    if not upload_dir.exists():
        print("[INFO] uploads 폴더가 없습니다.")
        return

    db_path = Path("myeongwolheon.db")
    if not db_path.exists():
        print("[ERROR] 데이터베이스 파일이 없습니다.")
        return

    # 변환 대상 확장자
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

    # 변환 제외 파일 (파비콘, SVG는 유지)
    exclude_patterns = ['favicon', '.svg', '.ico']

    converted_files = []
    skipped_files = []

    print("\n=== 기존 이미지 WebP 변환 시작 ===\n")

    # 모든 이미지 파일 찾기
    for img_file in upload_dir.iterdir():
        if not img_file.is_file():
            continue

        # 제외 대상 확인
        if any(pattern in img_file.name.lower() for pattern in exclude_patterns):
            print(f"[SKIP] {img_file.name} (변환 제외 파일)")
            skipped_files.append(img_file.name)
            continue

        # 이미지 확장자 확인
        if img_file.suffix.lower() not in image_extensions:
            continue

        # 이미 WebP면 건너뛰기
        if img_file.suffix.lower() == '.webp':
            continue

        try:
            # 이미지 데이터 읽기
            with img_file.open('rb') as f:
                image_data = f.read()

            # 파일명 분석 (확장자 제거)
            file_stem = img_file.stem

            # 품질 및 최대 너비 설정
            quality = 85
            max_width = None

            # 파일 유형별 설정
            if 'banner_pc' in file_stem:
                quality = 90
                max_width = 2100
            elif 'banner' in file_stem or 'sub_banner' in file_stem:
                quality = 90
                max_width = 1200
            elif 'og_image' in file_stem:
                quality = 90
                max_width = 1200
            elif 'site_logo' in file_stem or 'logo' in file_stem:
                quality = 90
                max_width = 800
            elif 'character' in file_stem:
                quality = 85
                max_width = 400

            # WebP로 변환
            output_path = upload_dir / file_stem
            convert_to_webp(image_data, output_path, quality=quality, max_width=max_width)

            # 원본 파일 크기와 WebP 파일 크기 비교
            webp_file = upload_dir / f"{file_stem}.webp"
            original_size = img_file.stat().st_size
            webp_size = webp_file.stat().st_size
            reduction = ((original_size - webp_size) / original_size) * 100

            print(f"[OK] {img_file.name} → {file_stem}.webp")
            print(f"     {original_size:,} bytes → {webp_size:,} bytes ({reduction:.1f}% 감소)")

            # 원본 파일 삭제
            img_file.unlink()
            print(f"     원본 파일 삭제 완료\n")

            converted_files.append({
                'original': img_file.name,
                'webp': f"{file_stem}.webp",
                'original_size': original_size,
                'webp_size': webp_size,
                'reduction': reduction
            })

        except Exception as e:
            print(f"[ERROR] {img_file.name} 변환 실패: {e}\n")
            skipped_files.append(img_file.name)

    # 데이터베이스 URL 업데이트
    print("\n=== 데이터베이스 URL 업데이트 ===\n")
    update_database_urls(converted_files)

    # 결과 요약
    print("\n=== 변환 완료 ===\n")
    print(f"✅ 변환 성공: {len(converted_files)}개")
    print(f"⏭️  건너뛴 파일: {len(skipped_files)}개")

    if converted_files:
        total_original = sum(f['original_size'] for f in converted_files)
        total_webp = sum(f['webp_size'] for f in converted_files)
        total_reduction = ((total_original - total_webp) / total_original) * 100

        print(f"\n📊 전체 용량:")
        print(f"   원본: {total_original:,} bytes")
        print(f"   WebP: {total_webp:,} bytes")
        print(f"   절감: {total_original - total_webp:,} bytes ({total_reduction:.1f}%)")

def update_database_urls(converted_files):
    """데이터베이스의 이미지 URL을 .webp로 업데이트"""
    if not converted_files:
        return

    conn = sqlite3.connect("myeongwolheon.db")
    cursor = conn.cursor()

    try:
        for file_info in converted_files:
            original_name = file_info['original']
            webp_name = file_info['webp']

            # site_config 테이블 업데이트
            columns = [
                'site_logo', 'seo_og_image',
                'banner_image_1', 'banner_image_2', 'banner_image_3', 'banner_image_4',
                'banner_image_pc_1', 'banner_image_pc_2', 'banner_image_pc_3', 'banner_image_pc_4',
                'sub_banner_image_1', 'sub_banner_image_2', 'sub_banner_image_3', 'sub_banner_image_4'
            ]

            for column in columns:
                cursor.execute(f"""
                    UPDATE site_config
                    SET {column} = REPLACE({column}, '{original_name}', '{webp_name}')
                    WHERE {column} LIKE '%{original_name}%'
                """)

            # services 테이블 업데이트
            cursor.execute(f"""
                UPDATE services
                SET character_image = REPLACE(character_image, '{original_name}', '{webp_name}')
                WHERE character_image LIKE '%{original_name}%'
            """)

            cursor.execute(f"""
                UPDATE services
                SET character_form_image = REPLACE(character_form_image, '{original_name}', '{webp_name}')
                WHERE character_form_image LIKE '%{original_name}%'
            """)

        conn.commit()
        print("[OK] 데이터베이스 URL 업데이트 완료")

    except Exception as e:
        print(f"[ERROR] 데이터베이스 업데이트 실패: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║          기존 이미지 WebP 일괄 변환 스크립트             ║
╚═══════════════════════════════════════════════════════════╝

⚠️  주의사항:
   1. 원본 이미지 파일이 삭제됩니다
   2. 백업을 먼저 해두는 것을 권장합니다
   3. 데이터베이스 URL이 자동으로 업데이트됩니다

🔄 변환 대상:
   - 로고, 배너, 서브배너, OG 이미지, 캐릭터 이미지

❌ 변환 제외:
   - 파비콘 (.ico, .png의 favicon)
   - SVG 파일
   - 동영상 파일 (.mp4, .webm)
    """)

    convert_existing_images()
