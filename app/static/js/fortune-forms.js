/**
 * FortuneForm - 운세 폼 공통 JavaScript 클래스
 * 모든 운세 페이지(사주, 오늘의운세, 궁합, 꿈해몽, 신년운세)에서 사용
 */

export class FortuneForm {
    constructor(formId, options = {}) {
        this.form = document.getElementById(formId);
        if (!this.form) {
            console.error(`Form with id "${formId}" not found`);
            return;
        }

        this.serviceCode = options.serviceCode || null;
        this.submitBtn = document.getElementById('submitBtn');
        this.birthdateInput = document.getElementById('birthdate');
        this.partnerBirthdateInput = document.getElementById('partner_birthdate');

        this.init();
    }

    init() {
        // 뒤로가기 시 버튼 활성화 (브라우저 캐시 문제 해결)
        window.addEventListener('pageshow', (event) => {
            if (event.persisted || performance.getEntriesByType("navigation")[0]?.type === "back_forward") {
                if (this.submitBtn) {
                    this.submitBtn.disabled = false;
                }
            }
        });

        // 생년월일 포맷팅 설정
        if (this.birthdateInput) {
            this.setupBirthdateFormat(this.birthdateInput);
        }
        if (this.partnerBirthdateInput) {
            this.setupBirthdateFormat(this.partnerBirthdateInput);
        }

        // 성별 버튼 설정
        this.setupGenderButtons();

        // 양력/음력 버튼 설정
        this.setupCalendarButtons();

        // 폼 제출 이벤트 설정
        this.setupFormSubmit();
    }

    /**
     * 생년월일 자동 포맷팅 (1989.09.22)
     */
    setupBirthdateFormat(input) {
        input.addEventListener('input', (e) => {
            const inputEl = e.target;
            let value = inputEl.value.replace(/[^\d]/g, ''); // 숫자만 남기기

            // 최대 8자리까지만
            if (value.length > 8) {
                value = value.substring(0, 8);
            }

            // 포맷팅: 1989.09.22
            let formatted = '';
            if (value.length >= 4) {
                formatted = value.substring(0, 4);
                if (value.length >= 6) {
                    formatted += '.' + value.substring(4, 6);
                    if (value.length >= 8) {
                        formatted += '.' + value.substring(6, 8);
                    } else if (value.length > 6) {
                        formatted += '.' + value.substring(6);
                    }
                } else if (value.length > 4) {
                    formatted += '.' + value.substring(4);
                }
            } else {
                formatted = value;
            }

            inputEl.value = formatted;
        });
    }

    /**
     * 성별 버튼 클릭 이벤트
     */
    setupGenderButtons() {
        document.querySelectorAll('.gender-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const gender = this.getAttribute('data-gender');
                const target = this.getAttribute('data-target') || 'gender';

                // 같은 그룹의 다른 버튼들에서 active 클래스 제거
                const parentButtons = this.parentElement;
                parentButtons.querySelectorAll('.gender-btn').forEach(b => {
                    b.classList.remove('active');
                });

                // 현재 버튼에 active 클래스 추가
                this.classList.add('active');

                // hidden input에 값 설정
                document.getElementById(target).value = gender;
            });
        });
    }

    /**
     * 양력/음력 버튼 클릭 이벤트
     */
    setupCalendarButtons() {
        document.querySelectorAll('.calendar-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const calendar = this.getAttribute('data-calendar');
                const target = this.getAttribute('data-target') || 'calendar';

                // 같은 그룹의 다른 버튼들에서 active 클래스 제거
                const parentButtons = this.parentElement;
                parentButtons.querySelectorAll('.calendar-btn').forEach(b => {
                    b.classList.remove('active');
                });

                // 현재 버튼에 active 클래스 추가
                this.classList.add('active');

                // hidden input에 값 설정
                document.getElementById(target).value = calendar;
            });
        });
    }

    /**
     * 폼 제출 이벤트
     */
    setupFormSubmit() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();

            // 이름 유효성 검사 (꿈해몽이 아닐 때만)
            const nameInput = document.getElementById('name');
            if (nameInput && nameInput.value.trim()) {
                if (!this.validateName(nameInput.value.trim())) {
                    return;
                }
            }

            // 생년월일 유효성 검사
            if (this.birthdateInput && this.serviceCode !== 'dream') {
                if (!this.validateAndConvertBirthdate(this.birthdateInput, 'birthdate_hidden')) {
                    return;
                }
            }

            // 상대방 생년월일 유효성 검사 (사주궁합용)
            if (this.partnerBirthdateInput) {
                if (!this.validateAndConvertBirthdate(
                    this.partnerBirthdateInput,
                    'partner_birthdate_hidden',
                    '상대방 '
                )) {
                    return;
                }
            }

            // 버튼 비활성화 (중복 제출 방지)
            this.submitBtn.disabled = true;

            // 폼 제출 (서버에서 로딩 페이지로 리디렉션)
            this.form.submit();
        });
    }

    /**
     * 이름 유효성 검사
     */
    validateName(name) {
        // 완성된 한글만 허용 (자음/모음 단독 불가)
        const koreanRegex = /^[가-힣]+$/;
        const consonantRegex = /[ㄱ-ㅎ]/;
        const vowelRegex = /[ㅏ-ㅣ]/;

        if (consonantRegex.test(name) || vowelRegex.test(name)) {
            alert('완성된 한글 이름만 입력 가능합니다.');
            document.getElementById('name').focus();
            return false;
        }

        if (!koreanRegex.test(name)) {
            alert('이름은 한글만 입력 가능합니다.');
            document.getElementById('name').focus();
            return false;
        }

        if (name.length < 2 || name.length > 4) {
            alert('이름은 2글자 이상 4글자 이하로 입력해주세요.');
            document.getElementById('name').focus();
            return false;
        }

        return true;
    }

    /**
     * 생년월일 유효성 검사 및 YYYY-MM-DD 변환
     */
    validateAndConvertBirthdate(inputElement, hiddenInputId, prefix = '') {
        const birthdateValue = inputElement.value.replace(/\./g, '');

        if (birthdateValue.length !== 8) {
            return true; // 8자리가 아니면 그냥 통과 (서버에서 처리)
        }

        const year = parseInt(birthdateValue.substring(0, 4));
        const month = parseInt(birthdateValue.substring(4, 6));
        const day = parseInt(birthdateValue.substring(6, 8));

        // 년도 유효성 검사 (150살 이상 불가)
        const currentYear = new Date().getFullYear();
        const minYear = currentYear - 150;
        if (year < minYear || year > currentYear) {
            alert(`${prefix}년도를 다시 확인해주세요. (150살 이상은 검색할 수 없습니다)`);
            inputElement.focus();
            return false;
        }

        // 월 유효성 검사 (1-12월)
        if (month < 1 || month > 12) {
            alert(`${prefix}월을 다시 확인해주세요. (1-12월만 가능합니다)`);
            inputElement.focus();
            return false;
        }

        // 일 유효성 검사 (1-31일)
        if (day < 1 || day > 31) {
            alert(`${prefix}일을 다시 확인해주세요. (1-31일만 가능합니다)`);
            inputElement.focus();
            return false;
        }

        // 월별 일수 체크
        const daysInMonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        if (day > daysInMonth[month - 1]) {
            alert(`${prefix}${month}월은 최대 ${daysInMonth[month - 1]}일까지 입력 가능합니다.`);
            inputElement.focus();
            return false;
        }

        // hidden input에 YYYY-MM-DD 형식으로 저장
        inputElement.name = '';  // 기존 name 제거
        const hiddenInput = document.getElementById(hiddenInputId);
        hiddenInput.name = inputElement.id;  // hidden에 name 부여
        hiddenInput.value = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

        return true;
    }
}
