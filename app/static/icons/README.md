# 명월헌 아이콘 시스템

## 📁 아이콘 파일 목록

```
/static/icons/
├── kakao.svg      - 카카오톡 공유 버튼 (노란색 말풍선)
├── link.svg       - URL 복사 버튼 (체인 링크)
├── saju.svg       - 정통 사주팔자 (금색 두루마리)
├── match.svg      - 사주궁합 (분홍 하트)
├── today.svg      - 오늘의 운세 (금색 별)
├── newyear.svg    - 신년운세 (파란 달)
└── dream.svg      - 꿈해몽 (보라색 구름)
```

## 🎨 사용 방법

### 방법 1: 직접 이미지 태그 사용
```html
<img src="{{ url_for('static', path='/icons/kakao.svg') }}" alt="카카오톡" width="24">
<img src="{{ url_for('static', path='/icons/link.svg') }}" alt="링크 복사" width="24">
```

### 방법 2: CSS 클래스 사용 (추천)
```html
<!-- icons.css 파일을 먼저 import -->
<link rel="stylesheet" href="{{ url_for('static', path='/css/icons.css') }}">

<!-- 아이콘 사용 -->
<i class="icon icon-kakao"></i>
<i class="icon icon-link icon-lg"></i>
<i class="icon icon-saju icon-sm"></i>
```

크기 옵션:
- `icon-sm` - 16x16px (작게)
- `icon` - 24x24px (기본)
- `icon-lg` - 32x32px (크게)

### 방법 3: 인라인 스타일로 커스텀
```html
<img src="{{ url_for('static', path='/icons/kakao.svg') }}"
     alt="카카오톡"
     style="width: 20px; height: 20px; margin-right: 8px;">
```

## 🔄 아이콘 교체 방법

마음에 안 드는 아이콘이 있으면:

1. 원하는 SVG 파일을 다운로드 (무료 사이트: iconify.design, heroicons.com)
2. 같은 이름으로 `/static/icons/` 폴더에 덮어쓰기
3. 서버 재시작 (또는 브라우저 캐시 삭제)

**예시:**
- 기존: `kakao.svg` (기본 디자인)
- 새 파일: `kakao.svg` (다운받은 디자인) ← 덮어쓰기!

## 📦 추천 무료 아이콘 사이트

- [Iconify](https://iconify.design) - 20만개+ 아이콘, SVG 다운로드
- [Heroicons](https://heroicons.com) - 심플한 라인 아이콘
- [Lucide](https://lucide.dev) - 깔끔한 아이콘 세트
- [Phosphor Icons](https://phosphoricons.com) - 다양한 스타일

**검색 키워드:**
- 카카오톡: "kakao", "chat bubble"
- 링크: "link", "chain", "url"
- 사주: "scroll", "document", "paper"
- 하트: "heart", "love"
- 별: "star", "sparkle"
- 달: "moon", "crescent"
- 구름: "cloud", "dream"

## 💡 팁

1. **SVG 파일 크기**: 가급적 5KB 이하로 (현재 모두 1-2KB)
2. **색상 변경**: SVG 파일 열어서 `fill="#색상코드"` 수정
3. **투명도**: `opacity="0.5"` 값으로 조절
4. **여러 색상**: 각 `<path>`마다 다른 색상 지정 가능

## 🎯 SNS 공유 버튼 예제

```html
<div class="share-buttons">
    <button class="share-btn share-btn-kakao" onclick="shareKakao()">
        <img src="{{ url_for('static', path='/icons/kakao.svg') }}" width="20">
        카카오톡 공유
    </button>
    <button class="share-btn share-btn-link" onclick="copyLink()">
        <img src="{{ url_for('static', path='/icons/link.svg') }}" width="20">
        링크 복사
    </button>
</div>
```

CSS는 `/static/css/icons.css`에 이미 정의되어 있습니다!
