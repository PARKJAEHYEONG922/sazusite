/* 이미지 미리보기 기능 */

/**
 * 파일 입력에 대한 이미지/비디오 미리보기 표시
 * @param {HTMLInputElement} input - 파일 입력 요소
 * @param {string} previewId - 미리보기를 표시할 요소의 ID
 */
function previewImage(input, previewId) {
    const previewElement = document.getElementById(previewId);
    if (!previewElement) return;

    const file = input.files[0];
    if (!file) {
        previewElement.innerHTML = '<span style="color: #9ca3af;">미리보기 없음</span>';
        return;
    }

    // 미리보기 타입 결정 (로고, 파비콘, 서브배너, 캐릭터)
    let previewClass = 'image-preview-item';
    if (previewId === 'logo_preview') {
        previewClass = 'image-preview-item logo-preview';
    } else if (previewId === 'favicon_preview') {
        previewClass = 'image-preview-item favicon-preview';
    } else if (previewId.startsWith('sub_banner_preview_') ||
               previewId.startsWith('character_form_preview_') ||
               previewId.startsWith('character_result_preview_')) {
        previewClass = 'image-preview-item sub-banner';
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        const fileType = file.type.split('/')[0];

        if (fileType === 'image') {
            previewElement.innerHTML = `
                <div class="image-preview-wrapper">
                    <div class="${previewClass}">
                        <img src="${e.target.result}" alt="미리보기">
                    </div>
                </div>
            `;
        } else if (fileType === 'video') {
            previewElement.innerHTML = `
                <div class="image-preview-wrapper">
                    <div class="${previewClass}">
                        <video src="${e.target.result}" controls></video>
                    </div>
                </div>
            `;
        }
    };
    reader.readAsDataURL(file);
}

/**
 * 여러 이미지 미리보기 (그리드 형태)
 * @param {HTMLInputElement} input - 파일 입력 요소 (multiple 속성 필요)
 * @param {string} containerId - 미리보기 컨테이너 ID
 */
function previewMultipleImages(input, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const files = Array.from(input.files);
    if (files.length === 0) {
        container.innerHTML = '<p class="text-muted">선택된 이미지가 없습니다.</p>';
        return;
    }

    container.innerHTML = '';

    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewItem = document.createElement('div');
            previewItem.className = 'image-preview-item';
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="${file.name}">
                <span class="image-preview-label">${index + 1}</span>
                <button type="button"
                        class="image-preview-remove"
                        onclick="removePreviewImage(this)"
                        title="삭제">×</button>
            `;
            container.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    });
}

/**
 * 미리보기 이미지 삭제
 * @param {HTMLButtonElement} button - 삭제 버튼 요소
 */
function removePreviewImage(button) {
    const previewItem = button.closest('.image-preview-item');
    if (previewItem) {
        previewItem.remove();
    }
}

/**
 * 드래그 앤 드롭 기능 초기화
 * @param {string} dropZoneId - 드롭존 요소 ID
 * @param {HTMLInputElement} fileInput - 파일 입력 요소
 */
function initDragAndDrop(dropZoneId, fileInput) {
    const dropZone = document.getElementById(dropZoneId);
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        }, false);
    });

    dropZone.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;

        // 미리보기 트리거
        const changeEvent = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(changeEvent);
    }, false);
}

/**
 * 이미지 파일 크기 검증
 * @param {File} file - 검증할 파일
 * @param {number} maxSizeMB - 최대 파일 크기 (MB)
 * @returns {boolean} 유효 여부
 */
function validateImageSize(file, maxSizeMB = 5) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
        alert(`파일 크기는 ${maxSizeMB}MB 이하여야 합니다.`);
        return false;
    }
    return true;
}

/**
 * 이미지 파일 타입 검증
 * @param {File} file - 검증할 파일
 * @param {string[]} allowedTypes - 허용된 MIME 타입 배열
 * @returns {boolean} 유효 여부
 */
function validateImageType(file, allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']) {
    if (!allowedTypes.includes(file.type)) {
        alert('허용되지 않는 파일 형식입니다.');
        return false;
    }
    return true;
}
