/**
 * 명월헌 - 메인 자바스크립트
 */

// 사이드바 토글
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const hamburger = document.getElementById('hamburger');

    if (sidebar && overlay && hamburger) {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        hamburger.classList.toggle('active');
    }
}

// 서비스 카드 클릭 이벤트
function goToFortune(serviceCode) {
    window.location.href = `/fortune/${serviceCode}`;
}

// ESC 키로 사이드바 닫기
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && sidebar.classList.contains('active')) {
            toggleSidebar();
        }
    }
});

// 모바일 하단 광고 닫기
function closeMobileAd() {
    const mobileAd = document.getElementById('mobileBottomAd');
    if (mobileAd) {
        mobileAd.classList.add('hidden');
        // 세션 스토리지에 광고 닫음 상태 저장
        sessionStorage.setItem('mobileAdClosed', 'true');
        // body padding 제거
        document.body.style.paddingBottom = '0';
    }
}

// 페이지 로드 시 광고 닫힘 상태 확인
document.addEventListener('DOMContentLoaded', function () {
    const mobileAd = document.getElementById('mobileBottomAd');
    if (mobileAd && sessionStorage.getItem('mobileAdClosed') === 'true') {
        mobileAd.classList.add('hidden');
        document.body.style.paddingBottom = '0';
    }
});
