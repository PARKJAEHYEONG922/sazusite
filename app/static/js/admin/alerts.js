/* 알림 메시지 관리 */

/**
 * 알림 메시지 표시
 * @param {string} message - 표시할 메시지
 * @param {string} type - 알림 타입 (success, error, warning, info)
 * @param {number} duration - 표시 시간 (ms), 0이면 자동으로 사라지지 않음
 */
function showAlert(message, type = 'info', duration = 5000) {
    // 기존 알림 제거
    const existingAlert = document.querySelector('.alert-floating');
    if (existingAlert) {
        existingAlert.remove();
    }

    // 아이콘 선택
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    const icon = icons[type] || icons.info;

    // 알림 요소 생성
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-floating`;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;

    alertDiv.innerHTML = `
        <span class="alert-icon">${icon}</span>
        <span class="alert-content">${message}</span>
        <button onclick="this.parentElement.remove()"
                style="background: none; border: none; font-size: 20px; cursor: pointer; margin-left: auto; padding: 0 4px; color: inherit; opacity: 0.7;">×</button>
    `;

    // 페이지에 추가
    document.body.appendChild(alertDiv);

    // 자동 제거
    if (duration > 0) {
        setTimeout(() => {
            alertDiv.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => alertDiv.remove(), 300);
        }, duration);
    }
}

/**
 * 성공 메시지 표시
 */
function showSuccess(message, duration = 3000) {
    showAlert(message, 'success', duration);
}

/**
 * 에러 메시지 표시
 */
function showError(message, duration = 5000) {
    showAlert(message, 'error', duration);
}

/**
 * 경고 메시지 표시
 */
function showWarning(message, duration = 4000) {
    showAlert(message, 'warning', duration);
}

/**
 * 정보 메시지 표시
 */
function showInfo(message, duration = 3000) {
    showAlert(message, 'info', duration);
}

/**
 * 확인 대화상자
 * @param {string} message - 확인 메시지
 * @returns {Promise<boolean>} 사용자 선택 (확인: true, 취소: false)
 */
function confirmAction(message) {
    return new Promise((resolve) => {
        const result = confirm(message);
        resolve(result);
    });
}

/**
 * 로딩 오버레이 표시
 */
function showLoading() {
    // 기존 로딩 제거
    hideLoading();

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-overlay';
    loadingDiv.id = 'loadingOverlay';
    loadingDiv.innerHTML = '<div class="loading-spinner"></div>';

    document.body.appendChild(loadingDiv);
    document.body.style.overflow = 'hidden';
}

/**
 * 로딩 오버레이 숨기기
 */
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
        document.body.style.overflow = '';
    }
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .alert-floating {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .alert-floating .alert-content {
        flex: 1;
    }
`;
document.head.appendChild(style);
