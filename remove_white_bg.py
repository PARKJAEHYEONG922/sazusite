"""
흰색 배경 제거 스크립트
사용법: python remove_white_bg.py input.png output.png
"""
from PIL import Image
import numpy as np
import sys

def remove_white_background(input_path, output_path, threshold=240):
    """
    흰색 배경을 투명하게 변환

    Args:
        input_path: 입력 이미지 경로
        output_path: 출력 이미지 경로
        threshold: 흰색 판단 기준 (0-255, 기본 240)
    """
    # 이미지 열기
    img = Image.open(input_path).convert('RGBA')
    data = np.array(img)

    # RGB 채널 분리
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # 흰색에 가까운 픽셀 찾기 (모든 RGB 값이 threshold 이상)
    white_pixels = (r > threshold) & (g > threshold) & (b > threshold)

    # 흰색 픽셀을 투명하게 만들기
    data[white_pixels] = [255, 255, 255, 0]

    # 저장
    result_img = Image.fromarray(data, 'RGBA')
    result_img.save(output_path, 'PNG')

    print(f"✓ 배경 제거 완료!")
    print(f"  입력: {input_path}")
    print(f"  출력: {output_path}")
    print(f"  투명 처리된 픽셀: {white_pixels.sum()} 개")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("사용법: python remove_white_bg.py <입력파일> <출력파일>")
        print("예제: python remove_white_bg.py logo.png logo_transparent.png")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        remove_white_background(input_file, output_file)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
