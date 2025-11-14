/* 유틸리티 함수 */

/**
 * 폼 자동 저장 (localStorage 사용)
 * @param {string} formId - 폼 ID
 * @param {number} interval - 저장 간격 (ms)
 */
function enableAutoSave(formId, interval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;

    const storageKey = `autosave_${formId}`;

    // 이전 저장 데이터 복원
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.elements[key];
                if (input) {
                    input.value = data[key];
                }
            });
            showInfo('이전에 작성하던 내용을 복원했습니다.', 2000);
        } catch (e) {
            console.error('자동 저장 데이터 복원 실패:', e);
        }
    }

    // 주기적 저장
    setInterval(() => {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        localStorage.setItem(storageKey, JSON.stringify(data));
    }, interval);

    // 폼 제출 시 저장 데이터 삭제
    form.addEventListener('submit', () => {
        localStorage.removeItem(storageKey);
    });
}

/**
 * 쿼리 파라미터 가져오기
 * @param {string} param - 파라미터 이름
 * @returns {string|null} 파라미터 값
 */
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * 날짜 포맷팅 (YYYY-MM-DD HH:mm:ss)
 * @param {Date} date - 날짜 객체
 * @returns {string} 포맷된 날짜 문자열
 */
function formatDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * 날짜 포맷팅 (YYYY-MM-DD)
 * @param {Date} date - 날짜 객체
 * @returns {string} 포맷된 날짜 문자열
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 파일 크기를 읽기 좋은 형식으로 변환
 * @param {number} bytes - 바이트 크기
 * @returns {string} 포맷된 크기 문자열
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * 문자열을 URL 안전한 형식으로 변환 (slug)
 * @param {string} text - 변환할 텍스트
 * @returns {string} URL 안전 문자열
 */
function slugify(text) {
    return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')
        .replace(/[^\w\-가-힣]+/g, '')
        .replace(/\-\-+/g, '-');
}

/**
 * 클립보드에 텍스트 복사
 * @param {string} text - 복사할 텍스트
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showSuccess('클립보드에 복사되었습니다.', 2000);
    } catch (err) {
        console.error('클립보드 복사 실패:', err);
        showError('클립보드 복사에 실패했습니다.');
    }
}

/**
 * 디바운스 함수 (연속 호출 방지)
 * @param {Function} func - 실행할 함수
 * @param {number} wait - 대기 시간 (ms)
 * @returns {Function} 디바운스된 함수
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 요소가 뷰포트에 보이는지 확인
 * @param {HTMLElement} element - 확인할 요소
 * @returns {boolean} 보이는지 여부
 */
function isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * 페이지 상단으로 부드럽게 스크롤
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * 특정 요소로 부드럽게 스크롤
 * @param {string} elementId - 요소 ID
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}
