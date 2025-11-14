/* 탭 전환 기능 */

/**
 * 탭 전환
 * @param {Event} event - 클릭 이벤트
 * @param {string} tabId - 표시할 탭 콘텐츠 ID
 */
function switchTab(event, tabId) {
    // 모든 탭 버튼에서 active 클래스 제거
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });

    // 모든 탭 콘텐츠 숨기기
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // 클릭된 탭 버튼 활성화
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }

    // 선택된 탭 콘텐츠 표시
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}

/**
 * 페이지 로드 시 첫 번째 탭 자동 활성화
 */
function initTabs() {
    const firstTabButton = document.querySelector('.tab-button');
    if (firstTabButton) {
        firstTabButton.click();
    }
}

/**
 * URL 해시를 기반으로 탭 활성화
 * 예: #tab-banner 등의 해시가 있으면 해당 탭으로 이동
 */
function activateTabFromHash() {
    const hash = window.location.hash;
    if (hash) {
        const tabId = hash.substring(1); // # 제거
        const tabButton = document.querySelector(`[onclick*="${tabId}"]`);
        if (tabButton) {
            tabButton.click();
        }
    }
}

/**
 * 탭 전환 시 URL 해시 업데이트
 * @param {string} tabId - 탭 ID
 */
function updateUrlHash(tabId) {
    if (history.pushState) {
        history.pushState(null, null, `#${tabId}`);
    } else {
        window.location.hash = tabId;
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // URL 해시가 있으면 해당 탭으로, 없으면 첫 번째 탭 활성화
    if (window.location.hash) {
        activateTabFromHash();
    } else {
        initTabs();
    }
});

// 브라우저 뒤로가기/앞으로가기 시 탭 상태 복원
window.addEventListener('hashchange', activateTabFromHash);
